import logging
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import pyarrow.parquet as pq
from airflow.exceptions import AirflowFailException
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from botocore.exceptions import ClientError


def get_redshift_conn(autocommit=True):
    hook = PostgresHook(postgres_conn_id="redshift_conn")
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


def read_parquet_from_s3(bucket_name: str, key: str):
    s3 = S3Hook(aws_conn_id="s3_conn")
    s3_client = s3.get_conn()
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        return pq.read_table(BytesIO(obj["Body"].read())).to_pandas()

    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            error_message = (
                f"{key}에 해당하는 파일이 {bucket_name}에 존재하지 않습니다."
            )
            logging.error(error_message)
            raise AirflowFailException(error_message)
        else:
            error_message = f"An error occurred: {e}"
            logging.error(error_message)
            raise AirflowFailException(error_message)


def compare_parquet_files(bucket_name, key1, key2):
    df1 = read_parquet_from_s3(bucket_name, key1)
    df2 = read_parquet_from_s3(bucket_name, key2)

    missing_data = df1[~df1.isin(df2.to_dict(orient="list")).all(axis=1)]

    columns_to_keep = [
        "room_id",
        "floor",
        "area",
        "deposit",
        "rent",
        "maintenance_fee",
        "address",
        "subway_count",
        "store_count",
        "cafe_count",
        "market_count",
        "restaurant_count",
        "hospital_count",
    ]

    missing_data = missing_data[columns_to_keep]
    missing_data["status"] = 0
    missing_data["status"] = missing_data["status"].astype("Int16")
    return missing_data


# Redshift에 데이터 저장
def save_to_redshift(data, table_name):
    cursor = get_redshift_conn()

    # DataFrame의 모든 numpy 타입을 Python의 기본 타입으로 변환
    data = data.astype(object).where(pd.notnull(data), None)

    columns = ", ".join(data.columns)
    values = ", ".join(["%s"] * len(data.columns))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

    for row in data.itertuples(index=False, name=None):
        cursor.execute(insert_query, row)

    cursor.close()


def compare_and_save(**kwargs):
    executionDate = kwargs["ds"]
    execution_date = datetime.strptime(executionDate, "%Y-%m-%d")
    execution_date_yesterday = execution_date - timedelta(days=1)

    execution_date_str = execution_date.strftime("%Y-%m-%d")
    execution_date_yesterday_str = execution_date_yesterday.strftime("%Y-%m-%d")

    bucket_name = "team-ariel-1-bucket"

    key1 = f"dabang/save/{execution_date_str}/dabang_{execution_date_str}.parquet"
    key2 = f"dabang/save/{execution_date_yesterday_str}/dabang_{execution_date_yesterday_str}.parquet"

    missing_data = compare_parquet_files(bucket_name, key1, key2)

    if not missing_data.empty:
        save_to_redshift(missing_data, "transformed.property_sold_status")
        # logging.info("Missing data:\n%s", missing_data.info())
    else:
        logging.info("No missing data found.")


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
    default_args=default_args,
    description="Compare two parquet files in S3 and save missing data to Redshift",
    schedule="0 7 * * *",
    start_date=datetime(2023, 8, 1),
    catchup=False,
) as dag:
    compare_and_save_task = PythonOperator(
        task_id="compare_and_save_task",
        python_callable=compare_and_save,
    )
