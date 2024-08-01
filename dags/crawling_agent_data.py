import agent_data_to_s3

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.mysql.hooks.mysql import MySqlHook

from datetime import datetime, timedelta
import os

agent_s3_url = None

# agent 데이터를 다운로드
def download_data(download_path):
    agent_data_to_s3.download_agent_data(download_path)


# agent 데이터 columns 변환
def transform(download_path):
    paths = agent_data_to_s3.get_csv_file_path(download_path)

    global agent_s3_url # 추후 redshift에 적재를 위해 파일명을 전역변수로 지정
    agent_s3_url = "agent/" + paths["csv_filename"]

    agent_data_to_s3.transform_columns(paths["csv_filepath"])

    return paths


# 다운로드 받은 데이터를 S3에 적재
def load_csv_to_s3(**context):
    paths = context["task_instance"].xcom_pull(key="return_value", task_ids='transform')
    key = context["params"]["key"]
    bucket_name = context["params"]["bucket_name"]

    hook = S3Hook('s3_conn')
    hook.load_file(filename=paths["csv_filepath"],
                    key=key+paths["csv_filename"],
                    bucket_name=bucket_name,
                    replace=True)

    
# 다운로드 받은 파일을 삭제
def clear_data(**context):
    import os
    import shutil
    paths = context["task_instance"].xcom_pull(key="return_value", task_ids='transform')

    os.remove(paths["zip_filepath"])
    shutil.rmtree(paths["extract_dir"])


# s3에 적재한 데이터를 redshift에 적재
def load_agent_data_to_rds(**context):
    schema = context["params"]["schema"]
    table = context["params"]["table"]
    key = context["params"]["key"]

    s3_hook = S3Hook(aws_conn_id= 's3_conn')
    file = s3_hook.download_file(key=key)
    try:
        mysql = MySqlHook(mysql_conn_id='rds_conn', local_infile=True)
        conn = mysql.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM {schema}.{table}")
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
    'retries' : 0,
}


with DAG(
    dag_id = 'crawling_agent_data',
    start_date = datetime(2024, 7, 1),
    catchup = False,
    schedule_interval = '0 1 * * *',
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

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform,
        op_kwargs={
                    "download_path": "/opt/airflow/data/"
                }
    )

    load_csv_to_s3 = PythonOperator(
        task_id='load_csv_to_s3',
        python_callable=load_csv_to_s3,
        params={
                    "download_path": "/opt/airflow/data/",
                    "key":"agent/",
                    "bucket_name":"team-ariel-1-bucket"
                }
    )

    clear_data = PythonOperator(
        task_id='clear_data',
        python_callable=clear_data
    )

    load_agent_data_to_redshift_from_s3 = S3ToRedshiftOperator(
        task_id = "load_agent_data_to_redshift_from_s3",
        s3_bucket = "team-ariel-1-bucket",	# 데이터를 가져오는 S3 bucket 이름
        s3_key = agent_s3_url,			# 데이터를 가져오는 위치
        schema = "raw_data",		# 데이터를 적재할 schema
        table = "agency_details",		# 데이터를 적재할 table
        copy_options=['csv', 'IGNOREHEADER 1'],	# S3에서 가져올 file 확장자
        redshift_conn_id = "redshift_dev_db",	# Connections에서 저장한 redshift Conn id
        aws_conn_id = "s3_conn",    	# Connections에서 저장한 S3 Conn id
        method = "REPLACE"
    )

    load_agent_data_to_rds = PythonOperator(
        task_id='load_agent_data_to_rds',
        python_callable=load_agent_data_to_rds,
        params={
                    "schema": "production",
                    "table": "agency_details",
                    "key":agent_s3_url
                }
    )



    download_data >> transform >> load_csv_to_s3 >>  clear_data >> load_agent_data_to_redshift_from_s3 >> load_agent_data_to_rds