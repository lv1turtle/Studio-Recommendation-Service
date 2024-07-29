import agent_data_to_s3

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from datetime import datetime


# agent 데이터를 다운로드
def download_data(download_path):
    agent_data_to_s3.download_agent_data(download_path)

# 다운로드 받은 데이터를 S3에 적재
def load_csv_to_s3(download_path, key, bucket_name):
    paths = agent_data_to_s3.load_s3(download_path)

    hook = S3Hook('s3_conn')
    hook.load_file(filename=paths["csv_filepath"],
                    key=key+paths["csv_filename"],
                    bucket_name=bucket_name,
                    replace=True)
    
    return paths
    
# 다운로드 받은 파일을 삭제
def clear_data(**context):
    import os
    paths = context["task_instance"].xcom_pull(key="return_value", task_ids='load_csv_to_s3')

    os.remove(paths["zip_filepath"])
    os.remove(paths["extract_dir"])

default_args = {
    'retries' : 0,
}

with DAG(
    dag_id = 'crawling_agent_data',
    start_date = datetime(2024, 7, 1),
    catchup = False,
    schedule_interval = '@weekly',
    default_args = default_args,
    tags = ['S3']
    ):
    download_data = PythonOperator(
        task_id='download_data',
        python_callable=download_data,
        op_kwargs={
                    "download_path": "/opt/airflow/data/"
                }
    )
    load_csv_to_s3 = PythonOperator(
        task_id='load_csv_to_s3',
        python_callable=load_csv_to_s3,
        op_kwargs={
                    "download_path": "/opt/airflow/data/",
                    "key":"agent/",
                    "bucket_name":"team-ariel-1-bucket"
                }
    )

    download_data >> load_csv_to_s3