from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

import time


def fetch_data():
    import extract_dabang_v2
    extract_dabang_v2.get_data_all()


def upload_to_s3(filename: str, key: str, bucket_name: str) -> None:
    hook = S3Hook("s3_conn")
    hook.load_file(filename=filename, key=key, bucket_name=bucket_name, replace=True)


def clear_data(filename: str) -> None:
    import os

    os.remove(filename)


with DAG(
    "dabang_upload_to_s3",
    schedule_interval="0 3 * * *",
    start_date=datetime(2024, 7, 1),
    catchup=False,
) as dag:

    fetch = PythonOperator(task_id="fetch_data", python_callable=fetch_data)
    
    save_upload = PythonOperator(
        task_id="save_upload",
        python_callable=upload_to_s3,
        op_kwargs={
            filename": "/opt/airflow/data/dabang.parquet",
            "key": "dabang/save/dabang_{{ ds }}.parquet",
            "bucket_name": "team-ariel-1-bucket",
        },
    )
    overwrite_upload = PythonOperator(
        task_id="overwrite_upload",
        python_callable=upload_to_s3,
        op_kwargs={
            "filename": "/opt/airflow/data/dabang.parquet",
            "key": "dabang/overwrite/dabang_{{ ds }}.parquet",
            "bucket_name": "team-ariel-1-bucket",
        },
    )
    clear = PythonOperator(
        task_id="clear_data",
        python_callable=clear_data,
        op_kwargs={"filename": "/opt/airflow/data/dabang.parquet"},
    )
fetch >> overwrite_upload >> save_upload >> clear
