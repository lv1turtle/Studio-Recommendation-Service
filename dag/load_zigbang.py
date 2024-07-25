from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
from datetime import datetime
from datetime import timedelta
import logging

from extract_zigbang import extract_room_ids_from_geohash, extract_room_info


def extract_room_ids(**context):
    # geohashs = ["wydnp", "wydju", "wydjv", "wydjy", "wydjz", "wydjs", "wydjt", "wydjw", "wydjx", "wydjk", "wydjm", "wydjq", "wydjr", "wydjh", "wydjj", "wydjn", "wydjp", \
    #             "wydhzx", "wydhzz", "wydhzw", "wydhzy", "wydq8", "wydq9", "wydqd", "wydqe", "wydqs", "wydq2", "wydq3", "wydq6", "wydq7", "wydqk", "wydq0", "wydq1", "wydq4", "wydq5", "wydqh", \
    #             "wydmb", "wydmc", "wydmf", "wydmg", "wydmu", "wydmv", "wydmy",  "wydm8", "wydm9", "wydmd", "wydme", "wydms", "wydmt", "wydmw", "wydm2", "wydm3", "wydm6", "wydm7", \
    #             "wydmk", "wydmm", "wydm0", "wydm1", "wydm4", "wydm5", "wydmh", "wydmj"]
    geohashs = ["wydnp"]

    logging.info("[ extract room id start ]")

    ids = []
    for geohash in geohashs:
        logging.info(geohash)
        ids.extend(extract_room_ids_from_geohash(geohash))
    logging.info("[ extract room id end ]\n")

    logging.info(f"[ total id : {len(ids)} ]\n")

    return ids[:5]


def extract_room_infos(**context):
    ids = context["task_instance"].xcom_pull(key="return_value", task_ids='extract_room_ids')

    logging.info("[ extract room info start ]")

    data = []

    for i, id in enumerate(ids):
        print(i, id)
        if i%5000 == 0:
            room = extract_room_info(id, delay=2)
        else:
            room = extract_room_info(id, delay=0)

        if room:
            data.append(room)
        
    logging.info("[ extract room info end ]")

    return data


def load_s3(**context):
    data = context["task_instance"].xcom_pull(key="return_value", task_ids='extract_room_infos')

    name = f"zigbang_{datetime.now().strftime('%y%m%d')}_v1.parquet"
    filename = context["params"]["filepath"] + name
    key = context["params"]["key"] + name
    
    bucket_name = context["params"]["bucket_name"]

    print("[ load s3 start ]")

    df = pd.DataFrame(data)

    df['area'] = df['area'].astype('float32')
    df['deposit'] = df['deposit'].astype('Int64')
    df['rent'] = df['rent'].astype('Int64')
    df['maintenance_fee'] = df['maintenance_fee'].astype('float32')
    df['latitude'] = df['latitude'].astype('float32')
    df['longitude'] = df['longitude'].astype('float32')

    df['marcket_count'] = df['marcket_count'].astype('Int64')
    df['store_count'] = df['store_count'].astype('Int64')
    df['subway_count'] = df['subway_count'].astype('Int64')
    df['restaurant_count'] = df['restaurant_count'].astype('Int64')
    df['cafe_count'] = df['cafe_count'].astype('Int64')
    df['hospital_count'] = df['hospital_count'].astype('Int64')

    df['nearest_marcket_distance'] = df['nearest_marcket_distance'].astype('Int64')
    df['nearest_store_distance'] = df['nearest_store_distance'].astype('Int64')
    df['nearest_subway_distance'] = df['nearest_subway_distance'].astype('Int64')
    df['nearest_restaurant_distance'] = df['nearest_restaurant_distance'].astype('Int64')
    df['nearest_cafe_distance'] = df['nearest_cafe_distance'].astype('Int64')
    df['nearest_hospital_distance'] = df['nearest_hospital_distance'].astype('Int64')
    
    df.to_parquet(filename, index=False, encoding="utf-8")
    
    # upload it to S3
    hook = S3Hook('s3_conn')
    hook.load_file(filename=filename,
                    key=key,
                    bucket_name=bucket_name,
                    replace=True)

    print("[ load s3 end ]")


dag = DAG(
    dag_id='load_zigbang',
    start_date=datetime(2024, 7, 10),  
    schedule='@once', #'*/10 * * * *',  
    max_active_runs=1,
    catchup=False,
    default_args={
        'retries': 0,
        'retry_delay': timedelta(minutes=3),
    }
)

params = {
    'filepath': '/opt/airflow/data/',
    'key': 'zigbang/',
    'bucket_name': 'team-ariel-1-bucket'
}


extract_room_ids = PythonOperator(
        task_id = 'extract_room_ids',
        python_callable = extract_room_ids,
        dag = dag)

extract_room_infos = PythonOperator(
    task_id = 'extract_room_infos',
    python_callable = extract_room_infos,
    dag = dag
)

load_s3 = PythonOperator(
    task_id='load_s3',
    python_callable=load_s3,
    params = params,
    dag = dag
)


extract_room_ids >> extract_room_infos >> load_s3