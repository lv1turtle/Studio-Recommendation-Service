from datetime import datetime, timedelta

import extract_zigbang_v3
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator

S3_BUCKET_NAME = "team-ariel-1-bucket"
# 가장 최근 파일명
yesterday = datetime.now() - timedelta(days=1)
ZIGBANG_S3_URL = f"zigbang/zigbang_2024-07-29{yesterday.strftime('%Y-%m-%d')}.parquet"


# 직방 매물 데이터를 수집해서 airflow xcom을 이용해 task간 데이터 공유
def fetch_room_data(**context):
    room_ids = extract_zigbang_v3.extract_room_ids()
    data = extract_zigbang_v3.extract_room_data(room_ids)

    ti = context["ti"]
    ti.xcom_push(key="extract_room_ids", value=room_ids)
    ti.xcom_push(key="room_data", value=data)


# redshift 테이블 내의 직방 데이터 갱신(insert, update, delete)
def update_to_redshift(**context):
    schema = context["params"]["schema"]
    table = context["params"]["table"]
    load_schema = context["params"]["load_schema"]
    load_table = context["params"]["load_table"]

    # xcom으로 공유한 직방 매물 데이터를 받아옴
    ti = context["ti"]
    room_data = ti.xcom_pull(task_ids="fetch_room_data", key="room_data")
    new_ids = ti.xcom_pull(task_ids="fetch_room_data", key="extract_room_ids")

    existing_ids = extract_zigbang_v3.fetch_existing_ids(schema, table)
    ids = extract_zigbang_v3.check_room_ids(new_ids, existing_ids)
    ids_to_delete = ids["ids_to_delete"]
    ids_to_add = ids["ids_to_add"]
    # 추가해야 할 매물 데이터를 xcom을 통해 task간 공유 (insert)
    ti.xcom_push(key="ids_to_add", value=ids_to_add)

    # 사라진 매물들(판매된 매물들)을 sold 테이블에 적재
    extract_zigbang_v3.insert_deleted_room_info(
        ids_to_delete, schema, table, load_schema, load_table
    )

    # 사라진 매물들을 테이블에서 제거 (delete)
    extract_zigbang_v3.delete_deleted_room_info(ids_to_delete, schema, table)

    # update_at이 31일 이상인 데이터를 sold 테이블에 적재
    extract_zigbang_v3.insert_unsold_room_info(schema, table, load_schema, load_table)

    # 추가된 데이터가 아닌 기존 데이터들은 상태 정보만 갱신 (update)
    maintained_data = extract_zigbang_v3.get_maintained_data(room_data, ids_to_add)
    extract_zigbang_v3.alter_room_info(maintained_data, schema, table)


# 추가해야 할 매물 데이터들을 S3에 적재 (agent_data와 결합하기 위함) 후 매물 데이터 삭제
def load_to_s3(**context):
    import os

    filename = context["params"]["filename"]
    key = context["params"]["key"]
    bucket_name = context["params"]["bucket_name"]

    execution_date_str = context["execution_date"].strftime("%Y-%m-%d")
    key = key.replace("ymd", execution_date_str)

    ti = context["ti"]
    room_data = ti.xcom_pull(task_ids="fetch_room_data", key="room_data")
    ids_to_add = ti.xcom_pull(task_ids="update_to_redshift", key="ids_to_add")

    new_info_data = extract_zigbang_v3.get_new_data(room_data, ids_to_add)
    data_to_add = extract_zigbang_v3.extend_facilities_info(new_info_data)
    extract_zigbang_v3.room_data_save_to_parquet(data_to_add, filename)

    hook = S3Hook("s3_conn")
    hook.load_file(filename=filename, key=key, bucket_name=bucket_name, replace=True)

    os.remove(filename)


with DAG(
    "zigbang_update",
    schedule="0 2 * * *",
    start_date=datetime(2024, 7, 1),
    catchup=False,
) as dag:

    fetch_room_data = PythonOperator(
        task_id="fetch_room_data", python_callable=fetch_room_data
    )
    update_to_redshift = PythonOperator(
        task_id="update_to_redshift",
        python_callable=update_to_redshift,
        params={
            "schema": "raw_data",
            "table": "zigbang",
            "load_schema": "transformed",
            "load_table": "property_sold_status",
        },
    )
    load_to_s3 = PythonOperator(
        task_id="load_to_s3",
        python_callable=load_to_s3,
        params={
            "filename": "/opt/airflow/data/zigbang.parquet",
            "key": "zigbang/zigbang_ymd.parquet",
            "bucket_name": S3_BUCKET_NAME,
        },
    )

    load_zigbang_data_to_redshift_from_s3 = S3ToRedshiftOperator(
        task_id="load_zigbang_data_to_redshift_from_s3",
        s3_bucket=S3_BUCKET_NAME,  # 데이터를 가져오는 S3 bucket 이름
        s3_key=ZIGBANG_S3_URL,  # 데이터를 가져오는 위치
        schema="raw_data",  # 데이터를 적재할 schema
        table="zigbang",  # 데이터를 적재할 table
        copy_options=["parquet"],  # S3에서 가져올 file 확장자
        redshift_conn_id="redshift_conn",  # Connections에서 저장한 redshift Conn id
        aws_conn_id="s3_conn",  # Connections에서 저장한 S3 Conn id
        method="APPEND",
    )


(
    fetch_room_data
    >> update_to_redshift
    >> load_to_s3
    >> load_zigbang_data_to_redshift_from_s3
)
