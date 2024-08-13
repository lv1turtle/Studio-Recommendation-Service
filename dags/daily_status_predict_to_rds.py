import ml_pipeline

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os
import shutil
import joblib
import logging


DEFAULT_DIR = '/opt/airflow/data/ml/'


# redshift 에서 전처리 테이블 생성 후 데이터를 가져와 DataFrame으로 변환
def fetch_transform_train_data(schema, raw_table, preprocessed_table):
    ml_pipeline.preprocessing_redshift_sold_table(schema, raw_table, preprocessed_table)
    df = ml_pipeline.fetch_preprocessed_data_from_redshift(schema, preprocessed_table)
    
    # 디렉토리가 없을 경우 생성
    if not os.path.exists(DEFAULT_DIR):
        os.mkdir(DEFAULT_DIR)

    filepath = os.path.join(DEFAULT_DIR, "train_data.csv")
    df.to_csv(filepath, encoding="utf-8", index=False)

    return filepath
    

# 학습 데이터 원핫인코딩, 언더샘플링 진행
def preprocessing_train_data(**context):
    filepath = context["task_instance"].xcom_pull(key="return_value", task_ids='fetch_transform_train_data')
    df = pd.read_csv(filepath)

    df_encoded = ml_pipeline.feature_encoding(df)
    df_resampled = ml_pipeline.perform_undersampling(df_encoded)

    logging.info(f"데이터 개수: {df.shape[0]}")

    filepath_df = os.path.join(DEFAULT_DIR, "resampled_df.csv")
    df_resampled.to_csv(filepath_df, encoding="utf-8", index=False)

    return filepath_df


# 머신러닝 모델 학습
def train_ml(**context):
    filepath = context["task_instance"].xcom_pull(key="return_value", task_ids='preprocessing_train_data')
    df_resampled = pd.read_csv(filepath)

    model, accuracy = ml_pipeline.train_randomforest(df_resampled)
    
    context["task_instance"].xcom_push(key="accuracy", value=accuracy)

    filepath_model = os.path.join(DEFAULT_DIR, "model.joblib")
    joblib.dump(model, filepath_model)

    return filepath_model


# redshift 테이블에 모델 학습 결과(accuracy) 적재
def insert_accuracy_to_redshift(schema, table, **context):
    accuracy = context["task_instance"].xcom_pull(key="accuracy", task_ids='train_ml')
    execution_date = context['execution_date'].strftime('%Y-%m-%d')

    ml_pipeline.insert_accuracy_to_redshift(schema, table, execution_date, accuracy)
    

# RDS table에서 데이터 추출 및 원핫인코딩
def fetch_preprocessed_property_from_rds(schema, table):
    df = ml_pipeline.fetch_preprocessed_data_from_rds(schema, table)
    df_encoded = ml_pipeline.feature_encoding(df)

    filepath = os.path.join(DEFAULT_DIR, "rds_data.csv")
    df_encoded.to_csv(filepath, encoding="utf-8", index=False)

    return filepath


# 머신러닝 모델에서 예측된 status 추출
def predict_status(**context):
    filepath_data = context["task_instance"].xcom_pull(key="return_value", task_ids='fetch_preprocessed_property_from_rds')
    df = pd.read_csv(filepath_data)

    filepath_model = context["task_instance"].xcom_pull(key="return_value", task_ids='train_ml')
    model = joblib.load(filepath_model)

    predict_df = ml_pipeline.predict_status(df, model)

    filepath = os.path.join(DEFAULT_DIR, "predict_data.csv")
    predict_df.to_csv(filepath, encoding="utf-8", index=False)

    return filepath


# RDS table에 status 값 update
def update_predicted_status_in_rds(schema, table, **context):
    filepath = context["task_instance"].xcom_pull(key="return_value", task_ids='predict_status')
    df = pd.read_csv(filepath)
    
    ml_pipeline.update_status_in_rds(df, schema, table)


# 다운로드 받은 임시 파일을 삭제
def clear_directory():
    for filename in os.listdir(DEFAULT_DIR):
        file_path = os.path.join(DEFAULT_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')



default_args = {
    'retries': 1,
}


with DAG(
    dag_id='daily_status_predict_to_rds',
    start_date=datetime(2024, 7, 1),
    catchup=False,
    schedule_interval=None,
    default_args=default_args,
) as dag:
    fetch_transform_train_data = PythonOperator(
        task_id='fetch_transform_train_data',
        python_callable=fetch_transform_train_data,
        op_kwargs={
            "schema": "transformed",
            "raw_table": "property_sold_status",
            "preprocessed_table": "model_data"
        }
    )

    preprocessing_train_data = PythonOperator(
        task_id='preprocessing_train_data',
        python_callable=preprocessing_train_data
    )

    train_ml = PythonOperator(
        task_id='train_ml',
        python_callable=train_ml
    )

    insert_accuracy_to_redshift = PythonOperator(
        task_id='insert_accuracy_to_redshift',
        python_callable=insert_accuracy_to_redshift,
        op_kwargs={
            "schema": "analytics",
            "table": "model_accuracy"
        }
    )

    fetch_preprocessed_property_from_rds = PythonOperator(
        task_id='fetch_preprocessed_property_from_rds',
        python_callable=fetch_preprocessed_property_from_rds,
        op_kwargs={
            "schema": "production",
            "table": "property"
        }
    )

    predict_status = PythonOperator(
        task_id='predict_status',
        python_callable=predict_status
    )

    update_predicted_status_in_rds = PythonOperator(
        task_id='update_predicted_status_in_rds',
        python_callable=update_predicted_status_in_rds,
        op_kwargs={
            "schema": "production",
            "table": "property"
        }
    )

    clear_directory = PythonOperator(
        task_id='clear_directory',
        python_callable=clear_directory
    )

    fetch_transform_train_data >> preprocessing_train_data >> train_ml >> insert_accuracy_to_redshift >> fetch_preprocessed_property_from_rds >> predict_status >> update_predicted_status_in_rds >> clear_directory

# EOF