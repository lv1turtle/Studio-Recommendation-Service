from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

import time

def fetch_data():
    import extract_dabang_v2

    # 작업속도 확인
    start_time = time.time()  # 시작 시간 기록
    extract_dabang_v2.get_data_all()
    end_time = time.time()  # 종료 시간 기록
    execution_time = end_time - start_time  # 실행 시간 계산
    hours, rem = divmod(execution_time, 3600)
    minutes, seconds = divmod(rem, 60)

    print(f"작업 시간: {int(hours)}시간 {int(minutes)}분 {seconds:.5f}초")

def upload_to_s3(filename: str, key: str, bucket_name: str) -> None:
    hook = S3Hook('s3_conn')
    hook.load_file(filename=filename,
                   key=key,
                   bucket_name=bucket_name,
                   replace=True)

def clear_data(filename: str) -> None:
    import os
    os.remove(filename)

with DAG('dabang_upload_to_s3',
         schedule_interval='0 10 * * *',
         start_date=datetime(2024, 7, 1),
         catchup=False
         ) as dag:

    fetch = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data
    )
    upload = PythonOperator(task_id='upload',
                            python_callable=upload_to_s3,
                            op_kwargs={
                                'filename': '/opt/airflow/data/dabang.parquet',
                                'key': 'dabang/dabang_{{ ds }}.parquet',
                                'bucket_name': 'team-ariel-1-bucket'
                            })
    clear = PythonOperator(task_id='clear_data',
                           python_callable=clear_data,
                           op_kwargs={
                                'filename': '/opt/airflow/data/dabang.parquet'
                           })
fetch >> upload >> clear
