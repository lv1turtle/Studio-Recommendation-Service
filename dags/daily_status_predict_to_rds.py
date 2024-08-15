import ml_pipeline

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging


# redshift 에서 전처리 테이블 생성 후 데이터를 가져와 DataFrame으로 변환
def fetch_transform_train_data(schema, raw_table, preprocessed_table):
    ml_pipeline.preprocessing_redshift_sold_table(schema, raw_table, preprocessed_table)
    df = ml_pipeline.fetch_preprocessed_data_from_redshift(schema, preprocessed_table)

    key = ml_pipeline.upload_dataframe_to_s3(df, "train_data.csv")

    return key
    

# 학습 데이터 원핫인코딩, 언더샘플링 진행
def preprocessing_train_data(**context):
    key = context["task_instance"].xcom_pull(key="return_value", task_ids='fetch_transform_train_data')
    df = ml_pipeline.read_csv_and_remove(key, ml_pipeline.DEFAULT_DIR)

    df_encoded = ml_pipeline.feature_encoding(df)
    df_resampled = ml_pipeline.perform_undersampling(df_encoded)

    logging.info(f"데이터 개수: {df.shape[0]}")

    key = ml_pipeline.upload_dataframe_to_s3(df_resampled, "resampled_df.csv")

    return key


# 머신러닝 모델 학습
def train_ml(**context):
    key = context["task_instance"].xcom_pull(key="return_value", task_ids='preprocessing_train_data')
    df_resampled = ml_pipeline.read_csv_and_remove(key, ml_pipeline.DEFAULT_DIR)

    model, accuracy = ml_pipeline.train_randomforest(df_resampled)
    
    context["task_instance"].xcom_push(key="accuracy", value=accuracy)

    key = ml_pipeline.upload_model_to_s3(model, "model.joblib")

    return key


# redshift 테이블에 모델 학습 결과(accuracy) 적재
def insert_accuracy_to_redshift(schema, table, **context):
    accuracy = context["task_instance"].xcom_pull(key="accuracy", task_ids='train_ml')
    execution_date = context['execution_date'].strftime('%Y-%m-%d')

    logging.info(f"accuracy : {accuracy}")
    ml_pipeline.insert_accuracy_to_redshift(schema, table, execution_date, accuracy)


# RDS table에서 데이터 추출 및 원핫인코딩
def fetch_preprocessed_property_from_rds(schema, table):
    df = ml_pipeline.fetch_preprocessed_data_from_rds(schema, table)
    df_encoded = ml_pipeline.feature_encoding(df)
    
    key = ml_pipeline.upload_dataframe_to_s3(df_encoded, "rds_data.csv")

    return key


# 머신러닝 모델에서 예측된 status 추출
def predict_status(**context):
    df_key = context["task_instance"].xcom_pull(key="return_value", task_ids='fetch_preprocessed_property_from_rds')
    df = ml_pipeline.read_csv_and_remove(df_key, ml_pipeline.DEFAULT_DIR)

    model_key = context["task_instance"].xcom_pull(key="return_value", task_ids='train_ml')
    model = ml_pipeline.read_model_and_remove(model_key, ml_pipeline.DEFAULT_DIR)

    predict_df = ml_pipeline.predict_status(df, model)

    filepath, key = ml_pipeline.upload_dataframe_to_s3(predict_df, "predict_data.csv")

    return key


# RDS table에 status 값 update
def update_predicted_status_in_rds(schema, table, **context):
    key = context["task_instance"].xcom_pull(key="return_value", task_ids='predict_status')
    df = ml_pipeline.read_csv_and_remove(key, ml_pipeline.DEFAULT_DIR)
    
    ml_pipeline.update_status_in_rds(df, schema, table)



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


    fetch_transform_train_data >> preprocessing_train_data >> train_ml >> insert_accuracy_to_redshift >> fetch_preprocessed_property_from_rds >> predict_status >> update_predicted_status_in_rds 

# EOF