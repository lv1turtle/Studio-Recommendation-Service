from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import extract_zigbang_v3


def fetch_room_data(**context):
    data = extract_zigbang_v3.extract_room_data()

    ti = context['ti']
    ti.xcom_push(key='extract_room_ids', value=data["extract_room_ids"])
    ti.xcom_push(key='room_data', value=data["room_data"])


def update_to_redshift(**context):
    schema = context["params"]["schema"]
    table = context["params"]["table"]
    
    ti = context['ti']
    room_data = ti.xcom_pull(task_ids='fetch_room_data', key='room_data')
    new_ids = ti.xcom_pull(task_ids='fetch_room_data', key='extract_room_ids')

    existing_ids = extract_zigbang_v3.fetch_existing_ids(schema, table)
    ids = extract_zigbang_v3.check_room_ids(new_ids, existing_ids)
    ids_to_delete = ids["ids_to_delete"]
    ids_to_add = ids["ids_to_add"]
    ti.xcom_push(key='ids_to_add', value=ids_to_add)

    extract_zigbang_v3.delete_deleted_room_info(ids_to_delete, schema, table)

    maintained_data = extract_zigbang_v3.get_maintained_data(room_data, ids_to_add)
    extract_zigbang_v3.alter_room_info(maintained_data, schema, table)


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
         schedule_interval='0 1 * * *',
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