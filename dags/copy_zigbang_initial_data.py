from airflow.hooks.postgres_hook import PostgresHook



def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_dev_db')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


def copy_s3_to_redshift(schema, table, s3_url, iam_s3_role):
    cursor = get_Redshift_connection()  

    try:
        cursor.execute("BEGIN;")

        define_sql = f"""
                DROP TABLE IF EXISTS {schema}.{table};
                CREATE TABLE {schema}.{table}(
                    room_id varchar(100),
                    platform varchar(50),
                    room_type varchar(50),
                    service_type varchar(50),
                    area real,
                    floor varchar(50),
                    deposit bigint,
                    rent bigint,
                    maintenance_fee real,
                    latitude real,
                    longitude real,
                    address varchar(255),
                    property_link varchar(255),
                    registration_number varchar(100),
                    agency_name varchar(100),
                    agent_name varchar(100),
                    market_count bigint,
                    nearest_market_distance bigint,
                    store_count bigint,
                    nearest_store_distance bigint,
                    subway_count bigint,
                    nearest_subway_distance bigint,
                    restaurant_count bigint,
                    nearest_restaurant_distance bigint,
                    cafe_count bigint,
                    nearest_cafe_distance bigint,
                    hospital_count bigint,
                    nearest_hospital_distance bigint,
                    title varchar(4095),
                    description varchar(4095),
                    image_link varchar(255)
                )
                """
        cursor.execute(define_sql)
        
        copy_sql = f"""
            COPY {schema}.{table}  
            FROM '{s3_url}'
            IAM_ROLE '{iam_s3_role}'
            FORMAT AS PARQUET;
        """
        cursor.execute(copy_sql)

        cursor.execute("COMMIT;") 

    
    except Exception as error:
        print(error)
        print("ROLLBACK")
        cursor.execute("ROLLBACK;")
        raise