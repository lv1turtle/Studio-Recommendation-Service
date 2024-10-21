from datetime import datetime, timedelta

import extract_zigbang_v3
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator
from airflow.sensors.time_delta import TimeDeltaSensor

# 일일 수집 매물 개수 제한 (kakaomap API 제한 때문)
DAILY_FETCH_LIMIT = 15000


# 수집할 매물 id 가져오기
def fetch_room_ids(**context):
    ids = extract_zigbang_v3.extract_room_ids()

    context["ti"].xcom_push(key="room_ids", value=ids)


# (1일차) 매물 데이터 수집하기
def extract_room_infos_1(**context):
    room_ids = context["ti"].xcom_pull(task_ids="fetch_room_ids", key="room_ids")
    last_fetched_index = 0
    data = []

    data.extend(
        extract_zigbang_v3.extract_room_info_include_facilities(
            room_ids[last_fetched_index : last_fetched_index + DAILY_FETCH_LIMIT]
        )
    )

    context["ti"].xcom_push(
        key="last_fetched_index", value=last_fetched_index + DAILY_FETCH_LIMIT
    )
    context["ti"].xcom_push(key="data", value=data)


# (2일차) 매물 데이터 수집하기
def extract_room_infos_2(**context):
    room_ids = context["ti"].xcom_pull(task_ids="fetch_room_ids", key="room_ids")
    last_fetched_index = context["ti"].xcom_pull(
        task_ids="extract_room_infos_1", key="last_fetched_index"
    )
    data = context["ti"].xcom_pull(task_ids="extract_room_infos_1", key="data")

    data.extend(
        extract_zigbang_v3.extract_room_info_include_facilities(
            room_ids[last_fetched_index : last_fetched_index + DAILY_FETCH_LIMIT]
        )
    )

    context["ti"].xcom_push(
        key="last_fetched_index", value=last_fetched_index + DAILY_FETCH_LIMIT
    )
    context["ti"].xcom_push(key="data", value=data)


# (3일차) 매물 데이터 수집하기
def extract_room_infos_3(**context):
    room_ids = context["ti"].xcom_pull(task_ids="fetch_room_ids", key="room_ids")
    last_fetched_index = context["ti"].xcom_pull(
        task_ids="extract_room_infos_2", key="last_fetched_index"
    )
    data = context["ti"].xcom_pull(task_ids="extract_room_infos_2", key="data")

    data.extend(
        extract_zigbang_v3.extract_room_info_include_facilities(
            room_ids[last_fetched_index : last_fetched_index + DAILY_FETCH_LIMIT]
        )
    )

    context["ti"].xcom_push(
        key="last_fetched_index", value=last_fetched_index + DAILY_FETCH_LIMIT
    )
    context["ti"].xcom_push(key="data", value=data)


# 수집한 데이터를 parquet 형태로 s3에 저장
def load_to_s3(**context):
    filename = context["params"]["filename"]
    key = context["params"]["key"]
    bucket_name = context["params"]["bucket_name"]

    ti = context["ti"]
    data = ti.xcom_pull(task_ids="extract_room_infos_2", key="data")

    extract_zigbang_v3.room_data_save_to_parquet(data, filename)

    hook = S3Hook("s3_conn")
    hook.load_file(filename=filename, key=key, bucket_name=bucket_name, replace=True)


# 볼륨에 저장됐던 parquet 데이터 삭제
def clear_data(filename: str) -> None:
    import os

    os.remove(filename)


# DAG 정의
with DAG(
    "load_initial_zigbang_data",
    schedule="@once",  # 최초에 한 번만 실행
    start_date=datetime(2024, 7, 26),
    catchup=False,
) as dag:

    fetch_room_ids = PythonOperator(
        task_id="fetch_room_ids",
        python_callable=fetch_room_ids,
        dag=dag,
    )

    # 첫째 날 데이터 수집 태스크
    extract_room_infos_1 = PythonOperator(
        task_id="extract_room_infos_1",
        python_callable=extract_room_infos_1,
        dag=dag,
    )

    # 자정까지 대기
    wait_until_midnight_1 = TimeDeltaSensor(
        task_id="wait_until_midnight_1",
        delta=timedelta(hours=12, minutes=0)
        - timedelta(
            seconds=datetime.now().second,
            minutes=datetime.now().minute,
            hours=datetime.now().hour,
        ),
    )

    # 둘째 날 데이터 수집 태스크
    extract_room_infos_2 = PythonOperator(
        task_id="extract_room_infos_2",
        python_callable=extract_room_infos_2,
        dag=dag,
    )

    # 자정까지 대기
    wait_until_midnight_2 = TimeDeltaSensor(
        task_id="wait_until_midnight_2",
        delta=timedelta(hours=12, minutes=0)
        - timedelta(
            seconds=datetime.now().second,
            minutes=datetime.now().minute,
            hours=datetime.now().hour,
        ),
    )

    # 셋째 날 데이터 수집 태스크
    extract_room_infos_3 = PythonOperator(
        task_id="extract_room_infos_3",
        python_callable=extract_room_infos_3,
        dag=dag,
    )

    load_to_s3 = PythonOperator(
        task_id="load_to_s3",
        python_callable=load_to_s3,
        params={
            "filename": "/opt/airflow/data/zigbang.parquet",
            "key": "zigbang/zigbang_init.parquet",
            "bucket_name": "team-ariel-1-bucket",
        },
    )

    clear_data = PythonOperator(
        task_id="clear_data",
        python_callable=clear_data,
        op_kwargs={"filename": "/opt/airflow/data/zigbang.parquet"},
    )

    load_zigbang_init_data_to_redshift_from_s3 = S3ToRedshiftOperator(
        task_id="load_zigbang_inti_data_to_redshift_from_s3",
        s3_bucket="team-ariel-1-bucket",  # 데이터를 가져오는 S3 bucket 이름
        s3_key="zigbang/zigbang_init.parquet",  # 데이터를 가져오는 위치
        schema="raw_data",  # 데이터를 적재할 schema
        table="zigbang",  # 데이터를 적재할 table
        copy_options=["parquet"],  # S3에서 가져올 file 확장자
        redshift_conn_id="redshift_conn",  # Connections에서 저장한 redshift Conn id
        aws_conn_id="s3_conn",  # Connections에서 저장한 S3 Conn id
        method="REPLACE",
    )


(
    fetch_room_ids
    >> extract_room_infos_1
    >> wait_until_midnight_1
    >> extract_room_infos_2
    >> wait_until_midnight_2
    >> extract_room_infos_3
    >> load_to_s3
    >> clear_data
    >> load_zigbang_init_data_to_redshift_from_s3
)
