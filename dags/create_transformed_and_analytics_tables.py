from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow import DAG

from datetime import datetime
from datetime import timedelta


# Redshift 연결
def get_redshift_conn(autocommit=True):
    hook = PostgresHook(postgres_conn_id = 'redshift_conn')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


# raw_data.property이 정제된 transformed.property 테이블 생성
def transform_property(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        transform_query = f"""
                            CREATE TABLE {schema}.{table} AS (
                                SELECT room_id, floor, area,
                                deposit, rent, maintenance_fee,
                                CASE
                                    WHEN address LIKE '%강남구%' THEN '강남구'
                                    WHEN address LIKE '%강동구%' THEN '강동구'
                                    WHEN address LIKE '%강북구%' THEN '강북구'
                                    WHEN address LIKE '%강서구%' THEN '강서구'
                                    WHEN address LIKE '%관악구%' THEN '관악구'
                                    WHEN address LIKE '%광진구%' THEN '광진구'
                                    WHEN address LIKE '%구로구%' THEN '구로구'
                                    WHEN address LIKE '%금천구%' THEN '금천구'
                                    WHEN address LIKE '%노원구%' THEN '노원구'
                                    WHEN address LIKE '%도봉구%' THEN '도봉구'
                                    WHEN address LIKE '%동대문구%' THEN '동대문구'
                                    WHEN address LIKE '%동작구%' THEN '동작구'
                                    WHEN address LIKE '%마포구%' THEN '마포구'
                                    WHEN address LIKE '%서대문구%' THEN '서대문구'
                                    WHEN address LIKE '%서초구%' THEN '서초구'
                                    WHEN address LIKE '%성동구%' THEN '성동구'
                                    WHEN address LIKE '%성북구%' THEN '성북구'
                                    WHEN address LIKE '%송파구%' THEN '송파구'
                                    WHEN address LIKE '%양천구%' THEN '양천구'
                                    WHEN address LIKE '%영등포구%' THEN '영등포구'
                                    WHEN address LIKE '%용산구%' THEN '용산구'
                                    WHEN address LIKE '%은평구%' THEN '은평구'
                                    WHEN address LIKE '%종로구%' THEN '종로구'
                                    WHEN address LIKE '%중구%' THEN '중구'
                                    WHEN address LIKE '%중랑구%' THEN '중랑구'
                                    ELSE '기타'
                                END AS district,
                                latitude, longitude, registration_number,
                                agency_name, agent_name, subway_count, store_count,
                                cafe_count, market_count, restaurant_count, hospital_count
                                FROM raw_data.{table}
                                WHERE district NOT LIKE '기타'
                            );"""
        cur.execute(transform_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


# analytics.property_position_and_fee 테이블 생성
def analytics_property_position_and_fee(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        analytics_query = f"""
                        CREATE TABLE {schema}.{table} AS (
                            SELECT room_id, district, latitude, longitude, deposit, (rent + maintenance_fee) as rent_fee
                            FROM transformed.property
                        );"""
        cur.execute(analytics_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


# analytics.property_having_all_facility_count 테이블 생성
def analytics_property_having_all_facility_count(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        analytics_query = f"""
                        CREATE TABLE {schema}.{table} AS (
                            SELECT district, CAST(COUNT(*) AS INTEGER) AS property_count
                            FROM transformed.property
                            WHERE subway_count > 0
                                AND store_count > 0
                                AND cafe_count > 0
                                AND market_count > 0
                                AND restaurant_count > 0
                                AND hospital_count > 0
                            GROUP BY 1
                        );"""
        cur.execute(analytics_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


# analytics.property_agency_count 테이블 생성
def analytics_property_agency_count(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        analytics_query = f"""
                        CREATE TABLE {schema}.{table} AS (
                            SELECT agency_name, CAST(COUNT(*) AS INTEGER) AS property_count
                            FROM transformed.property
                            GROUP BY 1
                        );"""
        cur.execute(analytics_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


# analytics.property_floor_count 테이블 생성
def analytics_property_floor_count(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        analytics_query = f"""
                        CREATE TABLE {schema}.{table} AS (
                            SELECT
                                CASE
                                    WHEN floor LIKE '%반지층%' THEN '반지하'
                                    WHEN floor ~ '^[0-9]+$' THEN floor || '층'
                                    WHEN floor = '옥탑' THEN '옥탑방'
                                    ELSE floor
                                END AS floor,
                                CAST(COUNT(*) AS INTEGER) AS property_count
                            FROM transformed.property
                            WHERE floor NOT LIKE '%고%' AND floor NOT LIKE '%중%' AND floor NOT LIKE '%저%'
                            GROUP BY 1
                        );"""
        cur.execute(analytics_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


# analytics.agency_certificate_count 테이블 생성
def analytics_agency_certificate_count(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        analytics_query = f"""
                        CREATE TABLE {schema}.{table} AS (
                            SELECT
                            CASE
                                WHEN a.certificate_number = '' THEN '미인증'
                                WHEN a.agent_code NOT IN (2, 3) THEN '미인증'
                                ELSE '인증'
                            END AS certificate_status,
                            CAST(COUNT(*) AS INTEGER) AS property_count
                            FROM transformed.property AS p
                            LEFT JOIN raw_data.agency_details AS a
                            ON p.registration_number = a.registration_number AND p.agent_name = a.agent_name
                            GROUP BY certificate_status
                        );"""
        cur.execute(analytics_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


# analytics.property_not_certificate 테이블 생성
def analytics_property_not_certificate(**context):
    cur = get_redshift_conn()
    schema = context["params"]["schema"]
    table = context["params"]["table"]

    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        analytics_query = f"""
                        CREATE TABLE {schema}.{table} AS (
                            SELECT p.agency_name, p.agent_name, CAST(COUNT(*) AS INTEGER) AS property_count
                            FROM transformed.property AS p
                            LEFT JOIN raw_data.agency_details AS a
                            ON p.registration_number = a.registration_number AND p.agent_name = a.agent_name
                            WHERE a.certificate_number = '' OR a.agent_code NOT IN (2, 3)
                            GROUP BY 1, 2
                        );"""
        cur.execute(analytics_query)
        cur.execute("COMMIT;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise


dag = DAG(
    dag_id = 'create_transformed_and_analytics_tables',
    start_date = datetime(2024, 7, 1),
    schedule_interval = None,
    catchup = False,
    default_args = {
        'owner' : 'sangmin',
        'retries' : 2,
        'retry_delay': timedelta(minutes=1),
    }
)

transform_property = PythonOperator(
    task_id = 'transform_property',
    python_callable = transform_property,
    params = {'schema' : 'transformed',
            'table' : 'property'},
    dag = dag
)

analytics_property_position_and_fee = PythonOperator(
    task_id = 'analytics_property_position_and_fee',
    python_callable = analytics_property_position_and_fee,
    params = {'schema' : 'analytics',
            'table' : 'property_position_and_fee'},
    dag = dag
)

analytics_property_having_all_facility_count = PythonOperator(
    task_id = 'analytics_property_having_all_facility_count',
    python_callable = analytics_property_having_all_facility_count,
    params = {'schema' : 'analytics',
            'table' : 'property_having_all_facility_count'},
    dag = dag
)

analytics_property_agency_count = PythonOperator(
    task_id = 'analytics_property_agency_count',
    python_callable = analytics_property_agency_count,
    params = {'schema' : 'analytics',
            'table' : 'property_agency_count'},
    dag = dag
)

analytics_property_floor_count = PythonOperator(
    task_id = 'analytics_property_floor_count',
    python_callable = analytics_property_floor_count,
    params = {'schema' : 'analytics',
            'table' : 'property_floor_count'},
    dag = dag
)

analytics_agency_certificate_count = PythonOperator(
    task_id = 'analytics_agency_certificate_count',
    python_callable = analytics_agency_certificate_count,
    params = {'schema' : 'analytics',
            'table' : 'agency_certificate_count'},
    dag = dag
)

analytics_property_not_certificate = PythonOperator(
    task_id = 'analytics_property_not_certificate',
    python_callable = analytics_property_not_certificate,
    params = {'schema' : 'analytics',
            'table' : 'property_not_certificate'},
    dag = dag
)

transform_property >> [analytics_property_position_and_fee, analytics_property_having_all_facility_count, analytics_property_agency_count, analytics_property_floor_count, analytics_agency_certificate_count, analytics_property_not_certificate]