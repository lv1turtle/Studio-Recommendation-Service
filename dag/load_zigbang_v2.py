from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from datetime import datetime
from datetime import timedelta
import logging

from extract_zigbang import extract_room_ids_from_geohash, extract_room_info



def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_dev_db')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


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

    return ids[:5]


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


# 새로 추가된 id 삭제할 id 체크
def check_room_ids(**context):
    new_ids = context["task_instance"].xcom_pull(key="return_value", task_ids='extract_room_ids')
    existing_ids = context["task_instance"].xcom_pull(key="return_value", task_ids='fetch_existing_ids')

    logging.info("[ check room ids start ]")

    new_ids_set = set(new_ids)
    existing_ids_set = set(existing_ids)

    ids_to_delete = list(existing_ids_set - new_ids_set)
    ids_to_add = sorted(list(new_ids_set - existing_ids_set))

    logging.info(f"[ check room ids end, delete : {len(ids_to_delete)}, add : {len(ids_to_add)} ]")

    return {"ids_to_delete" : ids_to_delete, "ids_to_add" : ids_to_add}


# 새로 추가된 매물 데이터 수집
def extract_room_infos(**context):
    new_ids = context["task_instance"].xcom_pull(key="return_value", task_ids='check_room_ids')["ids_to_add"]

    logging.info("[ extract room info start ]")

    data = []

    for i, id in enumerate(new_ids):
        print(i, id)
        if i%5000 == 0:
            room = extract_room_info(id, delay=2)
        else:
            room = extract_room_info(id, delay=0)

        if room:
            data.append(room)
        
    logging.info("[ extract room info end ]")

    return data


# 삭제된 매물 제거 및 새로운 매물 데이터 추가
def incremental_update_redshift(**context):
    ids_to_delete = context["task_instance"].xcom_pull(key="return_value", task_ids='check_room_ids')["ids_to_delete"]
    new_data = context["task_instance"].xcom_pull(key="return_value", task_ids='extract_room_infos')
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    logging.info("[ incremental update start ]")

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

    logging.info("delete info of deleted room success")

    if new_data:
        for record in new_data:
            try:
                cur.execute("BEGIN;")
                sql = f"""
                    INSERT INTO {schema}.{table} (
                        room_id, platform, room_type, service_type, area, floor, deposit, rent, maintenance_fee, latitude, longitude, address, property_link, registration_number, agency_name, agent_name, 
                        marcket_count, nearest_marcket_distance, store_count, nearest_store_distance, subway_count, nearest_subway_distance, restaurant_count, 
                        nearest_restaurant_distance, cafe_count, nearest_cafe_distance, hospital_count, nearest_hospital_distance, 
                        title, description, image_link
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                cur.execute(sql, (
                    record["room_id"], record["platform"], record["room_type"], record["service_type"], record["area"], record["floor"], record["deposit"], record["rent"], record["maintenance_fee"], record["latitude"], \
                    record["longitude"], record["address"], record["property_link"], record["registration_number"], record["agency_name"], record["agent_name"], record["marcket_count"], record["nearest_marcket_distance"], \
                    record["store_count"], record["nearest_store_distance"], record["subway_count"], record["nearest_subway_distance"], \
                    record["restaurant_count"], record["nearest_restaurant_distance"], record["cafe_count"], record["nearest_cafe_distance"], record["hospital_count"], record["nearest_hospital_distance"], \
                    record["title"], record["description"], record["image_link"]))
                
                cur.execute("COMMIT;") 

            except Exception as error:
                logging.error(error)
                logging.info("ROLLBACK")
                cur.execute("ROLLBACK;")
                raise

    logging.info("insert info of the new room success")


    logging.info("[ incremental update end ]")


dag = DAG(
    dag_id='load_zigbang_v2',
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
    "table" : "zigbang_test"
}

extract_room_ids = PythonOperator(
    task_id = 'extract_room_ids',
    python_callable = extract_room_ids,
    dag = dag)

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

extract_room_infos = PythonOperator(
    task_id = 'extract_room_infos',
    python_callable = extract_room_infos,
    dag = dag
)

incremental_update_redshift = PythonOperator(
    task_id = 'incremental_update_redshift',
    python_callable = incremental_update_redshift,
    params = params,
    dag = dag
)



extract_room_ids >> fetch_existing_ids >> check_room_ids >> extract_room_infos >> incremental_update_redshift