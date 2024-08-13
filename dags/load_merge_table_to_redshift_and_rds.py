from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import Variable
from airflow import DAG

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.mysql.hooks.mysql import MySqlHook
import os

from datetime import datetime
from datetime import timedelta


# Redshift 연결
def get_redshift_conn(autocommit=True):
    hook = PostgresHook(postgres_conn_id = 'redshift_conn')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


# S3의 다방 파일(.parquet)을 Redshift의 외부 테이블로 가져옴
def load_dabang_data_to_external_from_s3(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]
    uri = context["params"]["uri"]

    try:
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        external_table_query = f"""CREATE EXTERNAL TABLE {schema}.{table}(
                                room_id varchar(100),
                                platform varchar(50),
                                service_type varchar(50),
                                title varchar(4095),
                                floor varchar(50),
                                area float,
                                deposit bigint,
                                rent bigint,
                                maintenance_fee real,
                                address varchar(255),
                                latitude float,
                                longitude float,
                                property_link varchar(255),
                                registration_number varchar(100),
                                agency_name varchar(100),
                                agent_name varchar(100),
                                subway_count bigint,
                                nearest_subway_distance bigint,
                                store_count bigint,
                                nearest_store_distance bigint,
                                cafe_count bigint,
                                nearest_cafe_distance bigint,
                                market_count bigint,
                                nearest_market_distance bigint,
                                restaurant_count bigint,
                                nearest_restaurant_distance bigint,
                                hospital_count bigint,
                                nearest_hospital_distance bigint,
                                image_link varchar(255),
                                direction varchar(50)
                                )
                                stored as parquet
                                location '{uri}';"""
        cur.execute(external_table_query)
    except Exception as error:
        print(error)
        raise


# 다방(외부 테이블)과 직방(적재된 상태)를 병합하고 중복을 제거한 테이블을 Redshift에 적재
def load_merge_table_with_dabang_and_zigbang(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DELETE FROM {schema}.{table};")
        merge_table_query = f"""INSERT INTO {schema}.{table}
                                WITH numbered_data AS (
                                    SELECT room_id, platform, service_type, title, floor, area, deposit, rent,
                                    maintenance_fee, address, latitude, longitude, direction, registration_number,
                                    agency_name, agent_name, subway_count, nearest_subway_distance,
                                    store_count, nearest_store_distance, cafe_count, nearest_cafe_distance,
                                    market_count, nearest_market_distance, restaurant_count,
                                    nearest_restaurant_distance, hospital_count, nearest_hospital_distance,
                                    property_link, image_link,
                                    ROW_NUMBER() OVER (PARTITION BY address, floor, deposit, rent, maintenance_fee ORDER BY room_id) AS rn
                                    FROM (
                                    SELECT room_id, platform, service_type, title, floor, area, deposit, rent,
                                    maintenance_fee, address, latitude, longitude,
                                    (CASE
                                        WHEN direction = 'N' THEN '북'
                                        WHEN direction = 'S' THEN '남'
                                        WHEN direction = 'E' THEN '동'
                                        WHEN direction = 'W' THEN '서'
                                        WHEN direction = 'SE' THEN '남동'
                                        WHEN direction = 'SW' THEN '남서'
                                        WHEN direction = 'NE' THEN '북동'
                                        WHEN direction = 'NW' THEN '북서'
                                    END) as direction,
                                    registration_number,
                                    agency_name, agent_name, subway_count, nearest_subway_distance,
                                    store_count, nearest_store_distance, cafe_count, nearest_cafe_distance,
                                    market_count, nearest_market_distance, restaurant_count,
                                    nearest_restaurant_distance, hospital_count, nearest_hospital_distance,
                                    property_link, image_link
                                    FROM raw_data.zigbang
                                
                                    UNION ALL
                                
                                    SELECT room_id, platform, service_type, title, floor, area, deposit, rent,
                                    maintenance_fee, address, latitude, longitude, direction, registration_number,
                                    agency_name, agent_name, subway_count, nearest_subway_distance,
                                    store_count, nearest_store_distance, cafe_count, nearest_cafe_distance,
                                    market_count, nearest_market_distance, restaurant_count,
                                    nearest_restaurant_distance, hospital_count, nearest_hospital_distance,
                                    property_link, image_link
                                    FROM external_schema.dabang
                                    )
                                )
                                SELECT room_id, platform, service_type, REPLACE(REPLACE(title, ',', '.'), '\n', '. ') AS title, floor, area, deposit, rent,
                                    maintenance_fee, REPLACE(address, ',', ' '), latitude, longitude,
                                    (CASE
                                        WHEN direction not in ('동', '서', '남', '북', '남동', '남서', '북동', '북서') THEN ''
                                        ELSE direction
                                    END) as direction,
                                    registration_number,
                                    agency_name, agent_name, subway_count, nearest_subway_distance,
                                    store_count, nearest_store_distance, cafe_count, nearest_cafe_distance,
                                    market_count, nearest_market_distance, restaurant_count,
                                    nearest_restaurant_distance, hospital_count, nearest_hospital_distance,
                                    property_link, image_link
                                FROM numbered_data
                                WHERE rn = 1;"""
        cur.execute(merge_table_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


# 병합한 테이블(property)을 S3로 UNLOAD
def unload_merge_table(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]
    uri = context["params"]["uri"]
    iam_role = context["params"]["iam_role"]

    try:
        cur.execute("BEGIN;")
        unload_query = f"""UNLOAD ('SELECT * FROM {schema}.{table}')
                            TO '{uri}'
                            IAM_ROLE '{iam_role}'
                            CSV
                            ALLOWOVERWRITE
                            PARALLEL OFF
                            DELIMITER ','
                            HEADER;
                        """
        cur.execute(unload_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise
    

# UNLOAD된 파일을 RDS(mysql)에 적재
def load_merge_table_to_rds(**context):
    table = context["params"]["table"]
    uri = context["params"]["uri"]

    s3_hook = S3Hook(aws_conn_id= 's3_conn')
    file = s3_hook.download_file(key=f"{uri}000")
    try:
        mysql = MySqlHook(mysql_conn_id='rds_conn', local_infile=True)
        conn = mysql.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM production.property")
        cursor.execute("ALTER TABLE production.property DROP COLUMN status")
        cursor.execute(
            f"""
            LOAD DATA LOCAL INFILE '{file}'
            IGNORE
            INTO TABLE {table}
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            """
        )
        cursor.execute("ALTER TABLE production.property ADD COLUMN status smallint")
        cursor.close()
        conn.commit()
    finally:
        os.remove(file)


dag = DAG(
    dag_id = 'load_merge_table_to_redshift_and_rds',
    start_date = datetime(2024, 7, 1),
    schedule_interval = '0 6 * * *',
    catchup = False,
    default_args = {
        'owner' : 'sangmin',
        'retries' : 2,
        'retry_delay': timedelta(minutes=1),
    }
)

load_dabang_data_to_external_from_s3 = PythonOperator(
    task_id = 'load_dabang_data_to_external_from_s3',
    python_callable = load_dabang_data_to_external_from_s3,
    params = {'uri' : Variable.get("dabang_s3_uri"),
            'schema' : 'external_schema',
            'table' : 'dabang'},
    dag = dag
)

load_merge_table_with_dabang_and_zigbang = PythonOperator(
    task_id = 'load_merge_table_with_dabang_and_zigbang',
    python_callable = load_merge_table_with_dabang_and_zigbang,
    params = {'schema' : 'raw_data',
            'table' : 'property'},
    dag = dag
)

unload_merge_table = PythonOperator(
    task_id = 'unload_merge_table',
    python_callable = unload_merge_table,
    params = {'uri' : Variable.get("unload_s3_uri"),
            'iam_role' : Variable.get("redshift_iam_role"),
            'schema' : 'raw_data',
            'table' : 'property'},
    dag = dag
)

load_merge_table_to_rds = PythonOperator(
    task_id = 'load_merge_table_to_rds',
    python_callable = load_merge_table_to_rds,
    params = {'uri' : Variable.get("unload_s3_uri"),
            'table' : 'property'},
    dag = dag
)

# create_transformed_and_analytics_tables DAG를 Trigger하기 위한 Task
trigger_create_transformed_and_analytics_tables = TriggerDagRunOperator(
    task_id="trigger_create_transformed_and_analytics_tables",
    trigger_dag_id="create_transformed_and_analytics_tables",
    execution_date="{{ ds }}",
    reset_dag_run=True,
    wait_for_completion=True
)

# daily_status_predict_to_rds DAG를 Trigger하기 위한 Task
trigger_daily_status_predict_to_rds = TriggerDagRunOperator(
    task_id="trigger_daily_status_predict_to_rds",
    trigger_dag_id="daily_status_predict_to_rds",
    execution_date="{{ ds }}",
    reset_dag_run=True,
    wait_for_completion=True
)

load_dabang_data_to_external_from_s3 >> load_merge_table_with_dabang_and_zigbang >> trigger_create_transformed_and_analytics_tables
load_merge_table_with_dabang_and_zigbang >> unload_merge_table >> load_merge_table_to_rds >> trigger_daily_status_predict_to_rds