import requests
from time import sleep
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook

# kakaomap API
KAKAOMAP_URL = 'https://dapi.kakao.com/v2/local/search/keyword.json'
HEADERS = {"Authorization": "KakaoAK 0b802f8cc02b1b1343b8706eaf18efd1"}
CATEGORY_GROUP = {
                    "대형마트":{
                        "code":"MT1",
                        "radius":1712,
                        "eng":"market"
                    },
                    "편의점":{
                        "code":"CS2",
                        "radius":629,
                        "eng":"store"
                    },
                    "지하철역":{
                        "code":"SW8",
                        "radius":1058,
                        "eng":"subway"
                    },
                    "음식점":{
                        "code":"FD6",
                        "radius":500,
                        "eng":"restaurant"
                    },
                    "카페":{
                        "code":"CE7",
                        "radius":987,
                        "eng":"cafe"
                    },
                    "병원":{
                        "code":"HP8",
                        "radius":946,
                        "eng":"hospital"
                    }
                }



# geohash 기반 매물 id 추출
def extract_room_ids_from_geohash(geohash) -> list:
    url = f"https://apis.zigbang.com/v2/items/oneroom?geohash={geohash}&depositMin=0&rentMin=0&salesTypes[1]=월세&serviceType[0]=원룸&domain=zigbang"
    
    response = requests.get(url)
    # sleep(2)
    
    if response.status_code == 200:
        items = response.json()["items"]
        ids = [str(item["itemId"]) for item in items]

        return ids  
    else:
        print("status_code 400 :")
        print(response.json())
        raise


# 중개인 정보 추출
def get_agent_info(agent_id, delay=2):
    url = f"https://apis.zigbang.com/v3/agents/{agent_id}"

    columns = ["userNo", "userName", "agentName", "agentRegid"]
    
    response = requests.get(url)
    sleep(delay)

    if response.status_code == 200:
        response_data = response.json()
        agent_info = {key:response_data[key] for key in columns}
        
        return agent_info

    else:
        print("status_code 400 :")
        print(response.json())
        raise


# id 기반 매물 추출, dataframe으로 반환
def extract_room_info(id, delay=2):
    url = f"https://apis.zigbang.com/v3/items/{id}?version=&domain=zigbang"
    
    room_type_to_eng = {"원룸":"oneroom", "빌라":"villa", "오피스텔":"officetel"}

    response = requests.get(url)
    sleep(delay)

    if response.status_code == 200:
        try:
            json_data = response.json()
            item_data = json_data["item"]
            if item_data["status"] == "open":
                room_data = dict()

                room_data["room_id"] = str(item_data["itemId"])
                room_data["platform"] = "직방"
                room_data["room_type"] = item_data["roomType"]
                room_data["service_type"] = item_data["serviceType"]
                room_data["area"] = item_data["area"]["전용면적M2"]
                try:
                    room_data["floor"] = item_data["floor"]["floor"]
                except :
                    room_data["floor"] = None

                room_data["deposit"] = item_data["price"]["deposit"]
                room_data["rent"] = item_data["price"]["rent"]
                room_data["maintenance_fee"] = float(item_data["manageCost"]["amount"])
                room_data["latitude"] = item_data["location"]["lat"]
                room_data["longitude"] = item_data["location"]["lng"]
                room_data["direction"] = item_data["roomDirection"]
                room_data["address"] = item_data["jibunAddress"] if "jibunAddress" in item_data.keys() else item_data["addressOrigin"]["localText"]
                room_data["property_link"] = "https://sp.zigbang.com/share/" + room_type_to_eng[item_data["serviceType"]] + "/" +str(item_data["itemId"])

                agent_info = get_agent_info(json_data["agent"]["agentUserNo"], delay)
                room_data["registration_number"] = agent_info["agentRegid"]
                room_data["agency_name"] = agent_info["agentName"]
                room_data["agent_name"] = agent_info["userName"]
                
                room_data["title"] = item_data["title"]
                room_data["description"] = item_data["description"]
                room_data["image_link"] = item_data["imageThumbnail"] + "?w=400&h=300&q=70&a=1"
                room_data["update_at"] = item_data["updatedAt"]


                return room_data
            else:
                return None
        
        except Exception as error:
            print("Error:", response.json())
            print(error)
            raise
            
    else:
        print("Error:", response.json())
        raise


# id 기반 매물 추출(편의시설 데이터까지 추출), dataframe으로 반환
def extract_room_info_include_facilities(id, delay=2):
    url = f"https://apis.zigbang.com/v3/items/{id}?version=&domain=zigbang"
    
    room_type_to_eng = {"원룸":"oneroom", "빌라":"villa", "오피스텔":"officetel"}

    response = requests.get(url)
    sleep(delay)

    if response.status_code == 200:
        try:
            json_data = response.json()
            item_data = json_data["item"]
            if item_data["status"] == "open":
                room_data = dict()

                room_data["room_id"] = str(item_data["itemId"])
                room_data["platform"] = "직방"
                room_data["room_type"] = item_data["roomType"]
                room_data["service_type"] = item_data["serviceType"]
                room_data["area"] = item_data["area"]["전용면적M2"]
                try:
                    room_data["floor"] = item_data["floor"]["floor"]
                except :
                    room_data["floor"] = None

                room_data["deposit"] = item_data["price"]["deposit"]
                room_data["rent"] = item_data["price"]["rent"]
                room_data["maintenance_fee"] = float(item_data["manageCost"]["amount"])
                room_data["latitude"] = item_data["location"]["lat"]
                room_data["longitude"] = item_data["location"]["lng"]
                room_data["direction"] = item_data["roomDirection"]
                room_data["address"] = item_data["jibunAddress"] if "jibunAddress" in item_data.keys() else item_data["addressOrigin"]["localText"]
                room_data["property_link"] = "https://sp.zigbang.com/share/" + room_type_to_eng[item_data["serviceType"]] + "/" +str(item_data["itemId"])

                agent_info = get_agent_info(json_data["agent"]["agentUserNo"], delay)
                room_data["registration_number"] = agent_info["agentRegid"]
                room_data["agency_name"] = agent_info["agentName"]
                room_data["agent_name"] = agent_info["userName"]

                room_data.update(extract_nearest_all_facilities_info(room_data["longitude"], room_data["latitude"]))

                room_data["title"] = item_data["title"]
                room_data["description"] = item_data["description"]
                room_data["image_link"] = item_data["imageThumbnail"] + "?w=400&h=300&q=70&a=1"
                room_data["update_at"] = item_data["updatedAt"]

                return room_data
            else:
                return None
        
        except Exception as error:
            print("Error:", response.json())
            print(error)
            raise
            
    else:
        print("Error:", response.json())
        raise


# 주변 편의시설 데이터 수집
def extract_nearest_all_facilities_info(lng, lat) -> dict:
    data = dict()
    for category in CATEGORY_GROUP.keys():
        params = {'query' : category, 'x' : lng, 'y' : lat, 'radius' : CATEGORY_GROUP[category]["radius"], 'CATEGORY_GROUP_code' : CATEGORY_GROUP[category]["code"]}
        
        response = requests.get(KAKAOMAP_URL, params=params, headers=HEADERS)

        try:
            request = response.json()
            count = request['meta']['total_count']
            if count > 0:
                nearest_distance = int(request["documents"][0]["distance"])
            else: 
                nearest_distance = None
            
            data[CATEGORY_GROUP[category]["eng"]+"_count"] = count
            data[f"nearest_"+CATEGORY_GROUP[category]["eng"]+"_distance"] = nearest_distance
        except KeyError as e:
            print("Error:", request)
            data[CATEGORY_GROUP[category]["eng"]+"_count"] = 0
            data[f"nearest_"+CATEGORY_GROUP[category]["eng"]+"_distance"] = None
            continue

    return data


# room id 수집
def extract_room_ids():
    geohashs = ["wydnp", "wydju", "wydjv", "wydjy", "wydjz", "wydjs", "wydjt", "wydjw", "wydjx", "wydjk", "wydjm", "wydjq", "wydjr", "wydjh", "wydjj", "wydjn", "wydjp", \
                "wydhzx", "wydhzz", "wydhzw", "wydhzy", "wydq8", "wydq9", "wydqd", "wydqe", "wydqs", "wydq2", "wydq3", "wydq6", "wydq7", "wydqk", "wydq0", "wydq1", "wydq4", "wydq5", "wydqh", \
                "wydmb", "wydmc", "wydmf", "wydmg", "wydmu", "wydmv", "wydmy",  "wydm8", "wydm9", "wydmd", "wydme", "wydms", "wydmt", "wydmw", "wydm2", "wydm3", "wydm6", "wydm7", \
                "wydmk", "wydmm", "wydm0", "wydm1", "wydm4", "wydm5", "wydmh", "wydmj"]

    ids = []
    for geohash in geohashs:
        print(geohash)
        ids.extend(extract_room_ids_from_geohash(geohash))

    print(f"total id count : {len(ids)}")

    return ids


# 직방 매물 데이터 수집
def extract_room_data(room_ids):
    data = []
    for i, id in enumerate(room_ids):
        print(i, id)
        if i%5000 == 0:
            room = extract_room_info(id, delay=2)
        else:
            room = extract_room_info(id, delay=0)

        if room and room["room_type"] in ['원룸', '분리형원룸', '오픈형원룸', '투룸', '복층형원룸']:
            data.append(room)

    return data


def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_conn')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


# Redshift에서 기존 ID 가져오기
def fetch_existing_ids(schema, table):
    cursor = get_Redshift_connection()  

    cursor.execute(f'SELECT room_id FROM {schema}.{table};')
    records = cursor.fetchall()
    cursor.close()

    existing_ids = [record[0] for record in records]

    print(f"[ fetch existing ids end : {len(existing_ids)}]")

    return existing_ids


# 새로 추가된 id, 삭제할 id 체크
def check_room_ids(new_ids, existing_ids):
    new_ids_set = set(new_ids)
    existing_ids_set = set(existing_ids)

    ids_to_delete = list(existing_ids_set - new_ids_set)
    ids_to_add = list(new_ids_set - existing_ids_set)

    print(f"delete : {len(ids_to_delete)}, add : {len(ids_to_add)}")

    return {"ids_to_delete" : ids_to_delete, "ids_to_add" : ids_to_add}


# 삭제된 매물 삭제
def delete_deleted_room_info(ids_to_delete, schema, table):
    cursor = get_Redshift_connection()  

    if ids_to_delete:
        try:
            cursor.execute("BEGIN;")
            delete_sql = f"DELETE FROM {schema}.{table} WHERE room_id IN ({','.join(map(str, ids_to_delete))})"
            cursor.execute(delete_sql)
            cursor.execute("COMMIT;") 

        except Exception as error:
            print(error)
            print("ROLLBACK")
            cursor.execute("ROLLBACK;")
            raise


# 삭제된(판매된) 매물 load 테이블에 insert
def insert_deleted_room_info(ids_to_delete, schema, table, load_schema, load_table):
    cursor = get_Redshift_connection()

    if ids_to_delete:
        try:
            cursor.execute("BEGIN;")
            insert_sql = f"""
                    INSERT INTO {load_schema}.{load_table} (
                    room_id, floor, area, deposit, rent, maintenance_fee, address, 
                    market_count, store_count, subway_count, restaurant_count, cafe_count, 
                    hospital_count, status
                    )
                    SELECT 
                        room_id, floor, area, deposit, rent, maintenance_fee, address, 
                    market_count, store_count, subway_count, restaurant_count, cafe_count, 
                    hospital_count, 0
                    FROM {schema}.{table}
                    WHERE room_id IN ({','.join(map(str, ids_to_delete))});
                    """
            cursor.execute(insert_sql)
            cursor.execute("COMMIT;") 

        except Exception as error:
            print(error)
            print("ROLLBACK")
            cursor.execute("ROLLBACK;")
            raise
    

# 미 판매된 매물 sold 테이블에 insert
def insert_unsold_room_info(schema, table, load_schema, load_table):
    cursor = get_Redshift_connection()

    try:
        cursor.execute("BEGIN;")
        insert_sql = f"""
                INSERT INTO {load_schema}.{load_table} (
                room_id, floor, area, deposit, rent, maintenance_fee, address, direction,
                market_count, store_count, subway_count, restaurant_count, cafe_count, 
                hospital_count, status
                )
                SELECT 
                    room_id, floor, area, deposit, rent, maintenance_fee, address, direction,
                    market_count, store_count, subway_count, restaurant_count, cafe_count, 
                    hospital_count, 1 AS status
                FROM {schema}.{table} t
                WHERE t.update_at < current_date - INTERVAL '31 days'
                    AND NOT EXISTS (
                        SELECT 1
                        FROM {load_schema}.{load_table} lt
                        WHERE lt.room_id = t.room_id
                    );
                """
        cursor.execute(insert_sql)
        cursor.execute("COMMIT;") 

    except Exception as error:
        print(error)
        print("ROLLBACK")
        cursor.execute("ROLLBACK;")
        raise


def get_new_data(room_data, ids_to_add):
    data = []
    for item in room_data:
        if item["room_id"] in ids_to_add:
            data.append(item)
    
    return data


# 추가된 매물 편의시설 데이터 추가 수집
def extend_facilities_info(new_info_data):
    for i, item in enumerate(new_info_data):
        facilities = extract_nearest_all_facilities_info(lng=item["longitude"], lat=item["latitude"])
        new_info_data[i].update(facilities)
        
    return new_info_data


# 수집한 매물 데이터 csv에 적재
def room_data_save_to_parquet(data, filename):
    df = pd.DataFrame(data)

    df['room_id'] = df['room_id'].astype('str')

    df['area'] = df['area'].astype('float32')
    df['deposit'] = df['deposit'].astype('Int64')
    df['rent'] = df['rent'].astype('Int64')
    df['maintenance_fee'] = df['maintenance_fee'].astype('float32')
    df['latitude'] = df['latitude'].astype('float32')
    df['longitude'] = df['longitude'].astype('float32')

    df['market_count'] = df['market_count'].astype('Int64')
    df['store_count'] = df['store_count'].astype('Int64')
    df['subway_count'] = df['subway_count'].astype('Int64')
    df['restaurant_count'] = df['restaurant_count'].astype('Int64')
    df['cafe_count'] = df['cafe_count'].astype('Int64')
    df['hospital_count'] = df['hospital_count'].astype('Int64')

    df['nearest_market_distance'] = df['nearest_market_distance'].astype('Int64')
    df['nearest_store_distance'] = df['nearest_store_distance'].astype('Int64')
    df['nearest_subway_distance'] = df['nearest_subway_distance'].astype('Int64')
    df['nearest_restaurant_distance'] = df['nearest_restaurant_distance'].astype('Int64')
    df['nearest_cafe_distance'] = df['nearest_cafe_distance'].astype('Int64')
    df['nearest_hospital_distance'] = df['nearest_hospital_distance'].astype('Int64')

    df.to_parquet(filename, engine='pyarrow')


def get_maintained_data(room_data, ids_to_add):
    data = []
    for item in room_data:
        if item["room_id"] not in ids_to_add:
            data.append(item)
    
    return data


# 그대로인 매물 update
def alter_room_info(maintained_data, schema, table):
    cursor = get_Redshift_connection()  

    # 새로 수집한 기존 매물 데이터를 임시 테이블에 적재 후 join
    if maintained_data:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(f"""
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
                        direction VARCHAR(50),
                        property_link VARCHAR(255),
                        registration_number VARCHAR(100),
                        agency_name VARCHAR(100),
                        agent_name VARCHAR(100),
                        image_link VARCHAR(255),
                        update_at TIMESTAMP,

                        PRIMARY KEY (room_id)
            );""")

            for record in maintained_data:
                insert_sql = f"""
                    INSERT INTO {schema}.tmp (
                        room_id, platform, room_type, service_type, title, description, floor, area, deposit, rent, maintenance_fee, latitude, longitude, direction,
                        address, property_link, registration_number, agency_name, agent_name, image_link, update_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                cursor.execute(insert_sql, (
                    record["room_id"], record["platform"], record["room_type"], record["service_type"], record["title"], record["description"], record["floor"], record["area"], record["deposit"], record["rent"], \
                    record["maintenance_fee"], record["latitude"], record["longitude"], record["direction"], record["address"], record["property_link"], record["registration_number"],  \
                    record["agency_name"], record["agent_name"], record["image_link"], record["update_at"]))
            
            join_sql = f"""
                CREATE TABLE {schema}.join_tmp AS
                WITH o AS (
                    SELECT room_id AS o_room_id, market_count, nearest_market_distance, store_count, nearest_store_distance, subway_count, nearest_subway_distance, restaurant_count, 
                            nearest_restaurant_distance, cafe_count, nearest_cafe_distance, hospital_count, nearest_hospital_distance
                    FROM {schema}.{table}
                )
                SELECT room_id, platform, room_type, service_type, area, floor, deposit, rent, maintenance_fee, 
                        latitude, longitude, direction, address, property_link, registration_number, agency_name, agent_name, 
                        market_count, nearest_market_distance, store_count, nearest_store_distance, subway_count, 
                        nearest_subway_distance, restaurant_count, nearest_restaurant_distance, cafe_count, 
                        nearest_cafe_distance, hospital_count, nearest_hospital_distance, 
                        title, description, image_link, update_at
                FROM {schema}.tmp t
                JOIN o ON o.o_room_id = t.room_id;
            """
            cursor.execute(join_sql)

            alter_sql = f"""
                DELETE FROM {schema}.{table};
                INSERT INTO {schema}.{table} (
                    room_id, platform, room_type, service_type, area, floor, deposit, rent, maintenance_fee, 
                    latitude, longitude, direction, address, property_link, registration_number, agency_name, agent_name, 
                    market_count, nearest_market_distance, store_count, nearest_store_distance, subway_count, 
                    nearest_subway_distance, restaurant_count, nearest_restaurant_distance, cafe_count, 
                    nearest_cafe_distance, hospital_count, nearest_hospital_distance, title, description, image_link, update_at
                )
                SELECT 
                    room_id, platform, room_type, service_type, area, floor, deposit, rent, maintenance_fee, 
                    latitude, longitude, direction, address, property_link, registration_number, agency_name, agent_name, 
                    market_count, nearest_market_distance, store_count, nearest_store_distance, subway_count, 
                    nearest_subway_distance, restaurant_count, nearest_restaurant_distance, cafe_count, 
                    nearest_cafe_distance, hospital_count, nearest_hospital_distance, title, description, image_link, update_at
                FROM {schema}.join_tmp;
            """
            cursor.execute(alter_sql)

            drop_sql = f"""
                DROP TABLE IF EXISTS {schema}.tmp;
                DROP TABLE IF EXISTS {schema}.join_tmp;
            """
            cursor.execute(drop_sql)
            
            cursor.execute("COMMIT;") 

        except Exception as error:
            print(error)
            print("ROLLBACK")
            cursor.execute("ROLLBACK;")
            raise