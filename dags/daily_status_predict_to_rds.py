import ml_pipeline

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os
import shutil
import joblib

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
    X_train, y_train = ml_pipeline.perform_undersampling(df_encoded)

    print(f"학습 데이터 개수: {df.shape[0]}")

    filepath_X = os.path.join(DEFAULT_DIR, "X_train_data.csv")
    filepath_y = os.path.join(DEFAULT_DIR, "y_train_data.csv")

    X_train.to_csv(filepath_X, encoding="utf-8", index=False)
    y_train.to_csv(filepath_y, encoding="utf-8", index=False)

    return {"X_train":filepath_X, "y_train":filepath_y}


# 머신러닝 모델 학습
def train_ml(**context):
    filepath = context["task_instance"].xcom_pull(key="return_value", task_ids='preprocessing_train_data')

    # JSON 문자열을 DataFrame으로 변환
    X_train = pd.read_csv(filepath["X_train"])
    y_train = pd.read_csv(filepath["y_train"])
    
    model = ml_pipeline.train_randomforest(X_train, y_train)
    
    filepath_model = os.path.join(DEFAULT_DIR, "model.joblib")
    joblib.dump(model, filepath_model)

    return filepath_model


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
    schedule_interval='@once',
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

    fetch_preprocessed_property_from_rds = PythonOperator(
        task_id='fetch_preprocessed_property_from_rds',
        python_callable=fetch_preprocessed_property_from_rds,
        op_kwargs={
            "schema": "raw_data",
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
            "schema": "raw_data",
            "table": "property"
        }
    )

    clear_directory = PythonOperator(
        task_id='clear_directory',
        python_callable=clear_directory
    )

    fetch_transform_train_data >> preprocessing_train_data >> train_ml >> fetch_preprocessed_property_from_rds >> predict_status >> update_predicted_status_in_rds