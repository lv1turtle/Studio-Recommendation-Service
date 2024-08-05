from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.models import Variable
from airflow import DAG

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import pyarrow.parquet as pq
import os
from io import BytesIO
from datetime import datetime, timedelta
import logging


# Redshift 연결
def get_redshift_conn(autocommit=True):
    hook = PostgresHook(postgres_conn_id="redshift_conn")
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


# S3에서 parquet 파일 읽기
def read_parquet_from_s3(bucket_name, key):
    s3 = S3Hook("s3_conn")
    s3_client = s3.get_client_type("s3")
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
    return pq.read_table(BytesIO(obj["Body"].read())).to_pandas()


# 두 parquet 파일 비교
def compare_parquet_files(bucket_name, key1, key2):
    df1 = read_parquet_from_s3(bucket_name, key1)
    df2 = read_parquet_from_s3(bucket_name, key2)

    # df1에는 있고 df2에는 없는 데이터를 추출
    missing_data = df1[~df1.isin(df2.to_dict(orient="list")).all(axis=1)]

    return missing_data


# Redshift에 데이터 저장
def save_to_redshift(data, table_name):
    cursor = get_redshift_conn()

    # DataFrame을 SQL INSERT문으로 변환
    columns = ", ".join(data.columns)
    values = ", ".join(["%s"] * len(data.columns))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

    for row in data.itertuples(index=False, name=None):
        cursor.execute(insert_query, row)

    cursor.close()


# 메인 작업 함수
def compare_and_save(**kwargs):
    bucket_name = "team-ariel-1-bucket"
    key1 = "dabang/save/2024-08-02/dabang_2024-08-02.parquet"
    key2 = "dabang/save/2024-08-03/dabang_2024-08-03.parquet"

    # 두 파일 비교
    missing_data = compare_parquet_files(bucket_name, key1, key2)

    # 결과를 Redshift에 저장
    if not missing_data.empty:
        # save_to_redshift(missing_data, "your_redshift_table_name")
        logging.info("Missing data:\n%s", missing_data)


# DAG 설정
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "s3_parquet_compare",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 8, 1),
    catchup=False,
) as dag:
    compare_and_save_task = PythonOperator(
    task_id="compare_and_save_task",
    python_callable=compare_and_save,
    provide_context=True,
    dag=dag,
)

compare_and_save_task
