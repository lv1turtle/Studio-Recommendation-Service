import agent_data_to_s3
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.mysql.hooks.mysql import MySqlHook

from datetime import datetime
import os

S3_BUCKET_NAME = "team-ariel-1-bucket"
DOWNLOAD_PATH = "/opt/airflow/data/agent/"

# agent 데이터를 다운로드
def download_data(download_path):
    agent_data_to_s3.set_download_directory(download_path)
    agent_data_to_s3.download_agent_data(download_path)


# agent 데이터 columns 변환
def transform(download_path):
    paths = agent_data_to_s3.get_csv_file_path(download_path)
    paths["s3_url"] = "agent/" + paths["csv_filename"]

    agent_data_to_s3.transform_columns(paths["csv_filepath"])

    return paths


# 다운로드 받은 데이터를 S3에 적재 후 다운로드 받은 데이터 삭제
def load_csv_to_s3(**context):
    import os
    import shutil
    paths = context["task_instance"].xcom_pull(key="return_value", task_ids='transform')
    bucket_name = context["params"]["bucket_name"]

    hook = S3Hook('s3_conn')
    hook.load_file(filename=paths["csv_filepath"],
                    key=paths["s3_url"],
                    bucket_name=bucket_name,
                    replace=True)
    
    os.remove(paths["zip_filepath"])
    shutil.rmtree(paths["extract_dir"])


# s3에 적재한 데이터를 redshift에 적재
def load_agent_data_to_rds(**context):
    schema = context["params"]["schema"]
    table = context["params"]["table"]
    key = context["ti"].xcom_pull(task_ids='transform')['s3_url']
    bucket_name = context["params"]["bucket_name"]
    
    s3_hook = S3Hook(aws_conn_id= 's3_conn')
    file = s3_hook.download_file(key=key, bucket_name=bucket_name)
    try:
        mysql = MySqlHook(mysql_conn_id='rds_conn', local_infile=True)
        conn = mysql.get_conn()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {schema}.{table}")
        cursor.execute(
            f"""
            LOAD DATA LOCAL INFILE '{file}'
            IGNORE
            INTO TABLE {schema}.{table}
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            """
        )

        cursor.close()
        conn.commit()
    finally:
        os.remove(file)



default_args = {
    'retries': 0,
}

with DAG(
    dag_id='crawling_agent_data',
    start_date=datetime(2024, 7, 1),
    catchup=False,
    schedule_interval='0 1 * * *',
    default_args=default_args,
    tags=['S3']
) as dag:

    download_data = PythonOperator(
        task_id='download_data',
        python_callable=download_data,
        op_kwargs={
            "download_path": DOWNLOAD_PATH
        }
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform,
        op_kwargs={
            "download_path": DOWNLOAD_PATH
        }
    )

    load_csv_to_s3 = PythonOperator(
        task_id='load_csv_to_s3',
        python_callable=load_csv_to_s3,
        params={
            "bucket_name": S3_BUCKET_NAME
        }
    )

    load_agent_data_to_redshift_from_s3 = S3ToRedshiftOperator(
        task_id="load_agent_data_to_redshift_from_s3",
        s3_bucket=S3_BUCKET_NAME,
        s3_key="{{ task_instance.xcom_pull(task_ids='transform')['s3_url'] }}",
        schema="raw_data",
        table="agency_details",
        copy_options=['csv', 'IGNOREHEADER 1'],
        redshift_conn_id="redshift_conn",
        aws_conn_id="s3_conn",
        method="REPLACE"
    )

    load_agent_data_to_rds = PythonOperator(
        task_id='load_agent_data_to_rds',
        python_callable=load_agent_data_to_rds,
        params={
            "schema": "production",
            "table": "agency_details",
            "bucket_name": S3_BUCKET_NAME
        }
    )

    download_data >> transform >> load_csv_to_s3 >> load_agent_data_to_redshift_from_s3 >> load_agent_data_to_rds
