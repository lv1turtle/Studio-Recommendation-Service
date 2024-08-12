import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from imblearn.under_sampling import RandomUnderSampler
from sklearn.ensemble import RandomForestClassifier
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook



def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_conn')  # redshift_dev_db
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()

# production db
def get_RDS_connection(autocommit=True):
    hook = MySqlHook(mysql_conn_id='rds_conn', local_infile=True)
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


# redshift 에서 sold 테이블에 대해 전처리 후 전처리 테이블 생성
def preprocessing_redshift_sold_table(schema, raw_table, preprocessed_table): # transformed model_data property_sold_status
    try:
        cursor = get_Redshift_connection()  

        cursor.execute("BEGIN;")
        sql = f"""
            DROP TABLE IF EXISTS {schema}.{preprocessed_table};

            CREATE TABLE {schema}.{preprocessed_table} AS (
                SELECT room_id,
                    CASE
                        WHEN floor LIKE '%옥탑%' THEN '옥탑'
                        WHEN floor LIKE '%반지%' THEN '반지하'
                        WHEN floor LIKE '%저%' THEN '기타'
                        WHEN floor LIKE '%중%' THEN '기타'
                        WHEN floor LIKE '%고%' THEN '기타'
                        WHEN floor LIKE '%층' THEN
                            CASE
                                WHEN CAST(REPLACE(floor, '층', '') AS INTEGER) BETWEEN 1 AND 2 THEN '저'
                                WHEN CAST(REPLACE(floor, '층', '') AS INTEGER) BETWEEN 3 AND 14 THEN '중'
                                WHEN CAST(REPLACE(floor, '층', '') AS INTEGER) >= 15 THEN '고'
                            END
                        WHEN floor NOT LIKE '%층' THEN
                            CASE
                                WHEN CAST(floor AS INTEGER) BETWEEN 1 AND 2 THEN '저'
                                WHEN CAST(floor AS INTEGER) BETWEEN 3 AND 14 THEN '중'
                                WHEN CAST(floor AS INTEGER) >= 15 THEN '고'
                            END
                        ELSE '기타'
                    END AS floor_level,
                    area,
                    deposit,
                    rent,
                    maintenance_fee,
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
                    CAST(
                    (CASE WHEN subway_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN store_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN cafe_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN market_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN restaurant_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN hospital_count >= 1 THEN 1 ELSE 0 END)
                    AS SMALLINT) AS facility_count,
                    status
                FROM {schema}.{raw_table}
                WHERE district <> '기타' AND floor_level <> '기타'
            );
            """
        cursor.execute(sql)
        cursor.execute("COMMIT;") 

    except Exception as error:
        print(error)
        print("ROLLBACK")
        cursor.execute("ROLLBACK;")
        raise
    
    finally:
        cursor.close()


# 전처리 테이블에서 데이터를 가져와 데이터프레임 형태로 return
def fetch_preprocessed_data_from_redshift(schema, preprocessed_table):
    cursor = get_Redshift_connection()  

    query = f"SELECT * FROM {schema}.{preprocessed_table};"
    cursor.execute(query)

    records = cursor.fetchall()
    
    cursor.close()

    columns = ["room_id", "floor_level", "area", "deposit", "rent", "maintenance_fee", "district", "facility_count", "status"]
    df = pd.DataFrame(records, columns=columns)

    return df


# 카테고리형 변수 인코딩
def feature_encoding(df):
    # One-Hot Encoding을 위한 인코더 설정
    one_hot_encoder = OneHotEncoder(sparse=False, drop='if_binary')
    
    # 'floor_level'과 'district'을 한 번에 인코딩
    encoded_features = one_hot_encoder.fit_transform(df[['floor_level', 'district']])
    
    # 인코딩된 데이터프레임 생성
    df_encoded = pd.DataFrame(encoded_features, columns=one_hot_encoder.get_feature_names_out())
    
    # 원래 데이터프레임에서 인코딩할 컬럼 제거
    df_encoded = pd.concat([df.drop(columns=['floor_level', 'district']), df_encoded], axis=1)

    return df_encoded



# 판매완료, 미판매 데이터 개수를 맞추기 위한 랜덤 언더샘플링
def perform_undersampling(df):
    X = df.drop(columns=['room_id', 'status'])
    y = df['status']

    rus = RandomUnderSampler(sampling_strategy='auto', random_state=42)
    X_resampled, y_resampled = rus.fit_resample(X, y)

    return X_resampled, y_resampled


# random forest 모델 학습
def train_randomforest(X, y):
    clf = RandomForestClassifier()
    clf.fit(X, y)

    return clf


# RDS에서 데이터를 가져오면서 전처리 작업
def fetch_preprocessed_data_from_rds(schema, table): # taw_data.property
    cursor = get_RDS_connection()  

    query = f"""
        SELECT *
        FROM (
            SELECT room_id,
                CASE
                    WHEN floor LIKE '%옥탑%' THEN '옥탑'
                    WHEN floor LIKE '%반지%' THEN '반지하'
                    WHEN floor LIKE '%저%' THEN '기타'
                    WHEN floor LIKE '%중%' THEN '기타'
                    WHEN floor LIKE '%고%' THEN '기타'
                    WHEN floor LIKE '%층' THEN
                        CASE
                            WHEN CAST(REPLACE(floor, '층', '') AS SIGNED) BETWEEN 1 AND 2 THEN '저'
                            WHEN CAST(REPLACE(floor, '층', '') AS SIGNED) BETWEEN 3 AND 14 THEN '중'
                            WHEN CAST(REPLACE(floor, '층', '') AS SIGNED) >= 15 THEN '고'
                        END
                    WHEN floor NOT LIKE '%층' THEN
                        CASE
                            WHEN CAST(floor AS SIGNED) BETWEEN 1 AND 2 THEN '저'
                            WHEN CAST(floor AS SIGNED) BETWEEN 3 AND 14 THEN '중'
                            WHEN CAST(floor AS SIGNED) >= 15 THEN '고'
                        END
                    ELSE '기타'
                END AS floor_level,
                area,
                deposit,
                rent,
                maintenance_fee,
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
                CAST(
                    (CASE WHEN subway_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN store_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN cafe_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN market_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN restaurant_count >= 1 THEN 1 ELSE 0 END +
                    CASE WHEN hospital_count >= 1 THEN 1 ELSE 0 END)
                AS SIGNED) AS facility_count
            FROM {schema}.{table}
        ) AS subquery
        WHERE district <> '기타' AND floor_level <> '기타';
    """
    cursor.execute(query)

    records = cursor.fetchall()
    
    cursor.close()

    columns = ["room_id", "floor_level", "area", "deposit", "rent", "maintenance_fee", "district", "facility_count"]
    df = pd.DataFrame(records, columns=columns)

    return df


def predict_status(df, model):
    X = df.drop(columns=['room_id'])
    predictions = model.predict(X)
    df["status"] = predictions

    return df


def update_status_in_rds(df, schema, table):
    update_query = f"""
            UPDATE {schema}.{table}
            SET status = %s
            WHERE room_id = %s
        """
    
    try:
        cursor = get_RDS_connection()  

        cursor.execute("BEGIN;")

        for _, row in df.iterrows():
            cursor.execute(update_query, (row["room_id"], row["status"]))
        
        cursor.execute("COMMIT;") 

    except Exception as error:
        print(error)
        print("ROLLBACK")
        cursor.execute("ROLLBACK;")
        raise
    
    finally:
        cursor.close()