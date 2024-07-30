from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import extract_zigbang_v3


# 직방 매물 데이터를 수집해서 airflow xcom을 이용해 task간 데이터 공유
def fetch_room_data(**context):
    data = extract_zigbang_v3.extract_room_data()

    ti = context['ti']
    ti.xcom_push(key='extract_room_ids', value=data["extract_room_ids"])
    ti.xcom_push(key='room_data', value=data["room_data"])

# redshift 테이블 내의 직방 데이터 갱신(insert, update, delete)
def update_to_redshift(**context):
    schema = context["params"]["schema"]
    table = context["params"]["table"]
    
    # xcom으로 공유한 직방 매물 데이터를 받아옴
    ti = context['ti']
    room_data = ti.xcom_pull(task_ids='fetch_room_data', key='room_data')
    new_ids = ti.xcom_pull(task_ids='fetch_room_data', key='extract_room_ids')

    existing_ids = extract_zigbang_v3.fetch_existing_ids(schema, table)
    ids = extract_zigbang_v3.check_room_ids(new_ids, existing_ids)
    ids_to_delete = ids["ids_to_delete"]
    ids_to_add = ids["ids_to_add"]
    # 추가해야 할 매물 데이터를 xcom을 통해 task간 공유 (insert)
    ti.xcom_push(key='ids_to_add', value=ids_to_add)

    # 사라진 매물들을 테이블에서 제거 (delete)
    extract_zigbang_v3.delete_deleted_room_info(ids_to_delete, schema, table)

    # 추가된 데이터가 아닌 기존 데이터들은 상태 정보만 갱신 (update)
    maintained_data = extract_zigbang_v3.get_maintained_data(room_data, ids_to_add)
    extract_zigbang_v3.alter_room_info(maintained_data, schema, table)

# 추가해야 할 매물 데이터들을 S3에 적재 (agent_data와 결합하기 위함)
def load_to_s3(**context):
    filename = context["params"]["filename"]
    key = context["params"]["key"]
    bucket_name = context["params"]["bucket_name"]

    execution_date_str = context['execution_date'].strftime('%Y-%m-%d')
    key = key.replace('ymd', execution_date_str)
    
    ti = context['ti']
    room_data = ti.xcom_pull(task_ids='fetch_room_data', key='room_data') 
    ids_to_add = ti.xcom_pull(task_ids='update_to_redshift', key='ids_to_add')

    new_info_data = extract_zigbang_v3.get_new_data(room_data, ids_to_add)
    data_to_add = extract_zigbang_v3.extend_facilities_info(new_info_data)
    extract_zigbang_v3.room_data_save_to_parquet(data_to_add, filename)

    hook = S3Hook('s3_conn')
    hook.load_file(filename=filename,
                    key=key,
                    bucket_name=bucket_name,
                    replace=True)


def clear_data(filename: str) -> None:
    import os
    os.remove(filename)



with DAG('zigbang_update',
        schedule_interval='0 2 * * *',
        start_date=datetime(2024, 7, 1),
        catchup=False
        ) as dag:

    fetch_room_data = PythonOperator(
        task_id='fetch_room_data',
        python_callable=fetch_room_data
    )
    update_to_redshift = PythonOperator(
        task_id='update_to_redshift',
        python_callable=update_to_redshift,
        params={
                'schema': 'rawdata',
                'table': 'zigbang'
            }
    )
    load_to_s3 = PythonOperator(
        task_id='load_to_s3',
        python_callable=load_to_s3,
        params={
                'filename': '/opt/airflow/data/zigbang.parquet',
                'key': 'zigbang/zigbang_ymd.parquet',
                'bucket_name': 'team-ariel-1-bucket'
            }
    )
    clear_data = PythonOperator(
        task_id='clear_data',
        python_callable=clear_data,
        op_kwargs={
                    'filename': '/opt/airflow/data/zigbang.parquet'
                }
    )

fetch_room_data >> update_to_redshift >> load_to_s3 >> clear_data