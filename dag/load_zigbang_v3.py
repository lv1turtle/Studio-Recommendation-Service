from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd

from datetime import datetime
from datetime import timedelta
import logging

from extract_zigbang_v2 import extract_room_ids_from_geohash, extract_room_info
from extract_kakaomap_v2 import extract_nearest_all_facilities_info


def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_dev_db')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


# room id 수집
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

    logging.info(f"[ total id count : {len(ids)} ]\n")

    return ids[3:7]


# 직방 매물 수집
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


# Redshift에서 기존 ID 가져오기
def fetch_existing_ids(**context):
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    logging.info("[ fetch existing ids start ]")

    try:
        cursor = get_Redshift_connection()  

        cursor.execute(f'SELECT room_id FROM {schema}.{table};')
        records = cursor.fetchall()
        cursor.close()

        existing_ids = [record[0] for record in records]

        logging.info(f"[ fetch existing ids end : {len(existing_ids)}]")

        return existing_ids
    
    except Exception as e:
        logging.error(f"Error in  task: {e}")
        raise


# 새로 추가된 id, 삭제할 id 체크
def check_room_ids(**context):
    new_ids = context["task_instance"].xcom_pull(key="return_value", task_ids='extract_room_ids')
    existing_ids = context["task_instance"].xcom_pull(key="return_value", task_ids='fetch_existing_ids')

    logging.info("[ check room ids start ]")

    new_ids_set = set(new_ids)
    existing_ids_set = set(existing_ids)

    ids_to_delete = list(existing_ids_set - new_ids_set)
    ids_to_add = list(new_ids_set - existing_ids_set)

    logging.info(f"[ check room ids end, delete : {len(ids_to_delete)}, add : {len(ids_to_add)} ]")

    return {"ids_to_delete" : ids_to_delete, "ids_to_add" : ids_to_add}


# 삭제된 매물 삭제
def delete_deleted_room_info(**context):
    ids_to_delete = context["task_instance"].xcom_pull(key="return_value", task_ids='check_room_ids')["ids_to_delete"]
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    logging.info("[ delete info of deleted room start ]")

    cur = get_Redshift_connection()  

    if ids_to_delete:
        try:
            cur.execute("BEGIN;")
            delete_sql = f"DELETE FROM {schema}.{table} WHERE room_id IN ({','.join(map(str, ids_to_delete))})"
            cur.execute(delete_sql)
            cur.execute("COMMIT;") 

        except Exception as error:
            logging.error(error)
            logging.info("ROLLBACK")
            cur.execute("ROLLBACK;")
            raise

    logging.info("[ delete info of deleted room end ]")


# 추가된 매물 편의시설 데이터 추가 수집
def extend_facilities_info(**context):
    ids_to_add = context["task_instance"].xcom_pull(key="return_value", task_ids='check_room_ids')["ids_to_add"]
    info_data = context["task_instance"].xcom_pull(key="return_value", task_ids='extract_room_infos')
    new_info_data = [item for item in info_data if item["room_id"] in ids_to_add]

    logging.info("[ extract facilities info start ]")

    for i, item in enumerate(new_info_data):
        facilities = extract_nearest_all_facilities_info(lng=item["longitude"], lat=item["latitude"])
        new_info_data[i].update(facilities)
        
    logging.info("[ extract facilities info end ]")

    return new_info_data


# 추가로 수집한 매물 데이터 csv에 적재
def load_s3_facilities_info(**context):
    data = context["task_instance"].xcom_pull(key="return_value", task_ids='extend_facilities_info')

    name = f"zigbang_{datetime.now().strftime('%y%m%d')}.parquet"
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

    df.to_parquet(filename, engine='pyarrow')
    
    # upload it to S3
    hook = S3Hook('s3_conn')
    hook.load_file(filename=filename,
                    key=key,
                    bucket_name=bucket_name,
                    replace=True)

    print("[ load s3 end ]")


# 그대로인 매물 update
def alter_room_info(**context):
    # 새로 수집한 데이터 중 새로운 매물을 제외한 데이터, 즉 기존 매물 데이터 필터링
    data = context["task_instance"].xcom_pull(key="return_value", task_ids='extract_room_infos')
    ids_to_add = context["task_instance"].xcom_pull(key="return_value", task_ids='check_room_ids')["ids_to_add"]
    maintained_data = [item for item in data if item["room_id"] not in ids_to_add]

    schema = context["params"]["schema"]
    table = context["params"]["table"]

    logging.info("[ alter room info start ]")

    cur = get_Redshift_connection()  

    # 새로 수집한 기존 매물 데이터를 임시 테이블에 적재 후 join
    if maintained_data:
        try:
            cur.execute("BEGIN;")
            cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.tmp (
                        room_id VARCHAR(100),
                        platform VARCHAR(50),
                        room_type VARCHAR(50),
                        service_type VARCHAR(50),
                        title VARCHAR(4095),
                        description VARCHAR(4095),
                        floor VARCHAR(50),
                        area REAL,
                        deposit INT,
                        rent INT,
                        maintenance_fee REAL,
                        address VARCHAR(255),
                        latitude REAL,
                        longitude REAL,
                        property_link VARCHAR(255),
                        registration_number VARCHAR(100),
                        agency_name VARCHAR(100),
                        agent_name VARCHAR(100),
                        image_link VARCHAR(255),

                        PRIMARY KEY (room_id)
            );""")

            for record in maintained_data:
                insert_sql = f"""
                    INSERT INTO {schema}.tmp (
                        room_id, platform, room_type, service_type, title, description, floor, area, deposit, rent, maintenance_fee, latitude, longitude, address, 
                        property_link, registration_number, agency_name, agent_name, image_link
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                cur.execute(insert_sql, (
                    record["room_id"], record["platform"], record["room_type"], record["service_type"], record["title"], record["description"], record["floor"], record["area"], record["deposit"], record["rent"], \
                    record["maintenance_fee"], record["latitude"], record["longitude"], record["address"], record["property_link"], record["registration_number"],  \
                    record["agency_name"], record["agent_name"], record["image_link"]))
            
            join_sql = f"""
                CREATE TABLE {schema}.join_tmp AS
                WITH o AS (
                    SELECT room_id AS o_room_id, marcket_count, nearest_marcket_distance, store_count, nearest_store_distance, subway_count, nearest_subway_distance, restaurant_count, 
                            nearest_restaurant_distance, cafe_count, nearest_cafe_distance, hospital_count, nearest_hospital_distance
                    FROM {schema}.{table}
                )
                SELECT room_id, platform, room_type, service_type, area, floor, deposit, rent, maintenance_fee, 
                        latitude, longitude, address, property_link, registration_number, agency_name, agent_name, 
                        marcket_count, nearest_marcket_distance, store_count, nearest_store_distance, subway_count, 
                        nearest_subway_distance, restaurant_count, nearest_restaurant_distance, cafe_count, 
                        nearest_cafe_distance, hospital_count, nearest_hospital_distance, 
                        title, description, image_link
                FROM {schema}.tmp t
                JOIN o ON o.o_room_id = t.room_id;
            """
            cur.execute(join_sql)

            alter_sql = f"""
                DELETE FROM {schema}.{table};
                INSERT INTO {schema}.{table} (
                    room_id, platform, room_type, service_type, area, floor, deposit, rent, maintenance_fee, 
                    latitude, longitude, address, property_link, registration_number, agency_name, agent_name, 
                    marcket_count, nearest_marcket_distance, store_count, nearest_store_distance, subway_count, 
                    nearest_subway_distance, restaurant_count, nearest_restaurant_distance, cafe_count, 
                    nearest_cafe_distance, hospital_count, nearest_hospital_distance, title, description, image_link
                )
                SELECT 
                    room_id, platform, room_type, service_type, area, floor, deposit, rent, maintenance_fee, 
                    latitude, longitude, address, property_link, registration_number, agency_name, agent_name, 
                    marcket_count, nearest_marcket_distance, store_count, nearest_store_distance, subway_count, 
                    nearest_subway_distance, restaurant_count, nearest_restaurant_distance, cafe_count, 
                    nearest_cafe_distance, hospital_count, nearest_hospital_distance, title, description, image_link
                FROM {schema}.join_tmp;
            """
            cur.execute(alter_sql)

            drop_sql = f"""
                DROP TABLE IF EXISTS {schema}.tmp;
                DROP TABLE IF EXISTS {schema}.join_tmp;
            """
            cur.execute(drop_sql)
            
            cur.execute("COMMIT;") 

        except Exception as error:
            logging.error(error)
            logging.info("ROLLBACK")
            cur.execute("ROLLBACK;")
            raise

    logging.info("[ alter room info end ]")


dag = DAG(
    dag_id='load_zigbang_v3',
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
    "schema" : "mool8487",
    "table" : "zigbang_test",
    'filepath': '/opt/airflow/data/',
    'key': 'zigbang/',
    'bucket_name': 'team-ariel-1-bucket'
}

extract_room_ids = PythonOperator(
    task_id = 'extract_room_ids',
    python_callable = extract_room_ids,
    params = params,
    dag = dag)

extract_room_infos = PythonOperator(
    task_id = 'extract_room_infos',
    python_callable = extract_room_infos,
    params = params,
    dag = dag
)

fetch_existing_ids = PythonOperator(
    task_id = 'fetch_existing_ids',
    python_callable = fetch_existing_ids,
    params = params,
    dag = dag
)

check_room_ids = PythonOperator(
    task_id = 'check_room_ids',
    python_callable = check_room_ids,
    dag = dag
)

delete_deleted_room_info = PythonOperator(
    task_id = 'delete_deleted_room_info',
    python_callable = delete_deleted_room_info,
    params = params,
    dag = dag
)

extend_facilities_info = PythonOperator(
    task_id = 'extend_facilities_info',
    python_callable = extend_facilities_info,
    params = params,
    dag = dag
)

load_s3_facilities_info = PythonOperator(
    task_id = 'load_s3_facilities_info',
    python_callable = load_s3_facilities_info,
    params = params,
    dag = dag
)

alter_room_info = PythonOperator(
    task_id = 'alter_room_info',
    python_callable = alter_room_info,
    params = params,
    dag = dag
)

extract_room_ids >>  extract_room_infos >> fetch_existing_ids >> check_room_ids >> delete_deleted_room_info >> extend_facilities_info >> load_s3_facilities_info >> alter_room_info