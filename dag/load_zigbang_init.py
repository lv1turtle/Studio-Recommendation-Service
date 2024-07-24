from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
from datetime import datetime
from datetime import timedelta
import logging

from extract_zigbang import extract_room_ids_from_geohash, extract_room_info


# Define the DAG
dag = DAG(
    dag_id='load_zigbang_init',
    schedule='@once',
    schedule_interval=timedelta(days=1),
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 7, 20),
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    }
)

def extract_room_ids():
    geohashs = ["wydnp", "wydju", "wydjv", "wydjy", "wydjz", "wydjs", "wydjt", "wydjw", "wydjx", "wydjk", "wydjm", "wydjq", "wydjr", "wydjh", "wydjj", "wydjn", "wydjp", \
                "wydhzx", "wydhzz", "wydhzw", "wydhzy", "wydq8", "wydq9", "wydqd", "wydqe", "wydqs", "wydq2", "wydq3", "wydq6", "wydq7", "wydqk", "wydq0", "wydq1", "wydq4", "wydq5", "wydqh", \
                "wydmb", "wydmc", "wydmf", "wydmg", "wydmu", "wydmv", "wydmy",  "wydm8", "wydm9", "wydmd", "wydme", "wydms", "wydmt", "wydmw", "wydm2", "wydm3", "wydm6", "wydm7", \
                "wydmk", "wydmm", "wydm0", "wydm1", "wydm4", "wydm5", "wydmh", "wydmj"]

    logging.info("[ extract room id start ]")

    ids = []
    for geohash in geohashs:
        logging.info(geohash)
        ids.extend(extract_room_ids_from_geohash(geohash))
    logging.info("[ extract room id end ]\n")

    logging.info(f"[ total id : {len(ids)} ]\n")

    return ids

def load_s3(**kwargs):
    data = kwargs["data"]
    filename = kwargs["filename"]
    key = kwargs["key"]
    bucket_name = kwargs["bucket_name"]

    logging.info("[ load s3 start ]")

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8")
    
    # upload it to S3
    hook = S3Hook('s3_conn')
    hook.load_file(filename=filename,
                    key=key,
                    bucket_name=bucket_name,
                    replace=True)

    logging.info("[ load s3 end ]")


# 데이터를 수집하는 함수 정의
def collect_data(**kwargs):
    logging.info("[ extract start ]")

    ti = kwargs['ti']  # 태스크 인스턴스 가져오기
    # XCom에서 마지막으로 가져온 기록 상태를 가져오기
    ids = ti.xcom_pull(task_ids='collect_data', key='ids')
    last_fetched_index = ti.xcom_pull(task_ids='collect_data', key='last_fetched_index')
    data = ti.xcom_pull(task_ids='collect_data', key='data')
    if not ids:
        ids = extract_room_ids()
        ti.xcom_push(key='ids', value=ids)

        last_fetched_index = 0
        data = []
    
    ## 데이터 수집 및 저장
    logging.info("[ extract room info start ]")

    for i, id in enumerate(ids[last_fetched_index:last_fetched_index+10000]):
        print(i, id)
        if i%1000 == 0:
            room = extract_room_info(id, delay=2)
        else:
            room = extract_room_info(id, delay=0)

        if room:
            data.append(room)

        last_fetched_index += 1
        
    logging.info("[ extract room info end ]")

    if last_fetched_index >= len(ids):
        params = {
            "data":data,
            'filename': '/opt/airflow/data/zigbang_init.csv',
            'key': 'zigbang/zigbang_init.csv',
            'bucket_name': 'team-ariel-1-bucket'
        }

        load_s3(params)
        ti.xcom_push(key='continue_processing', value=False)

    else:
        ti.xcom_push(key='continue_processing', value=True)

        ti.xcom_push(key='data', value=data)
        ti.xcom_push(key='last_fetched_index', value=last_fetched_index)

        logging.info("[ extract end ]")


# 태스크 정의
collect_data_task = PythonOperator(
    task_id='collect_data', 
    provide_context=True,
    python_callable=collect_data,
    dag=dag,  # DAG 연결
)

# DAG 구조 정의
collect_data_task