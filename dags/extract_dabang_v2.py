import requests
import re
import pandas as pd
from airflow.models.variable import Variable

# API 키 모음
kakao_api_key = Variable.get("kakao_api_key_dabang")

# 다방 request url
dabang_base_url = Variable.get("dabang_base_url")
dabang_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Cookie": "_fwb=37od3E9MpyXVmFsL4IofFB.1720697470212; _fbp=fb.1.1720697470585.225224189142580448; _gcl_aw=GCL.1720697471.Cj0KCQjwhb60BhClARIsABGGtw-kc-hlUX7yjy6_4EHU8ub7a9PsTdTTN1p5i12H1O7P4uS3z-JEWoUaAjkGEALw_wcB; _gcl_gs=2.1.k1$i1720697470; _gid=GA1.2.363020388.1720697472; _gac_UA-59111157-1=1.1720697472.Cj0KCQjwhb60BhClARIsABGGtw-kc-hlUX7yjy6_4EHU8ub7a9PsTdTTN1p5i12H1O7P4uS3z-JEWoUaAjkGEALw_wcB; ring-session=1391973f-c2b6-42db-a949-9ce55784cd56; wcs_bt=s_3d10ff175f87:1720698474; _ga=GA1.1.844565415.1720697471; _ga_QMSMS2LS99=GS1.1.1720697470.1.1.1720698475.54.0.0",
    "Csrf": "token",
    "D-Api-Version": "5.0.0",
    "D-App-Version": "1",
    "D-Call-Type": "web",
    "Expires": "-1",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Referer": "https://www.dabangapp.com/map/onetwo?sellingTypeList=%5B%22MONTHLY_RENT%22%5D&m_lat=37.5822204&m_lng=126.9710212&m_zoom=13",
    "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}

category_group_code = {
    "대형마트": "MT1",
    "편의점": "CS2",
    "지하철역": "SW8",
    "은행": "BK9",
    "음식점": "FD6",
    "카페": "CE7",
    "병원": "HP8",
    "약국": "PM9",
}


def split_and_convert_korean_number(s):
    parts = re.findall(r"[0-9]+억|[0-9]+만", s)
    converted_parts = []

    for part in parts:
        if "억" in part:
            number = int(part.replace("억", "")) * 10000
        elif "만" in part:
            number = int(part.replace("만", ""))
        converted_parts.append((number))

    return converted_parts


def extract_nearest_facilities_info(lng, lat, category, radius=500) -> dict:
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": kakao_api_key}
    params = {
        "query": category,
        "x": lng,
        "y": lat,
        "radius": radius,
        "category_group_code": category_group_code.get(category, ""),
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return {"count": 0, "nearest_distance": None}

    data = response.json()
    count = data["meta"]["total_count"]

    if count > 0:
        nearest_distance = data["documents"][0].get("distance")
    else:
        nearest_distance = None

    return {"count": count, "nearest_distance": nearest_distance}


def fetch_rooms(base_url, page):
    current_url = base_url.format(page=page)
    response = requests.get(current_url, headers=dabang_headers)

    if response.status_code == 200:
        data = response.json()
        room_list = data.get("result", {}).get("roomList")
        return room_list
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


def process_rooms(room_list):
    data_for_parquet = []
    for room in room_list:
        id = room.get("id")
        price = room.get("priceTitle").split("/")
        Deposit = (price[0] + "만").strip()
        deposit_num = sum(split_and_convert_korean_number(Deposit))
        monthly_fee = price[1]
        lat = room.get("randomLocation").get("lat")
        lng = room.get("randomLocation").get("lng")
        roomDesc = room.get("roomDesc").split(",")
        area = roomDesc[1].strip().replace("m²", "")
        manage_money = re.findall(r"\d+", roomDesc[2].strip())
        img_url = room.get("imgUrlList")[0]

        if manage_money:
            manage_money = int(manage_money[0])
        else:
            manage_money = 0

        # 주변 정보 가져오기 By Kakao Map API
        mart = extract_nearest_facilities_info(lng, lat, "대형마트", 1712)
        store = extract_nearest_facilities_info(lng, lat, "편의점", 629)
        subway = extract_nearest_facilities_info(lng, lat, "지하철역", 1058)
        food = extract_nearest_facilities_info(lng, lat, "음식점")
        cafe = extract_nearest_facilities_info(lng, lat, "카페", 987)
        hospital = extract_nearest_facilities_info(lng, lat, "병원", 946)

        # 주소
        address_url = f"https://www.dabangapp.com/api/3/room/near?api_version=3.0.1&call_type=web&room_id={id}&version=1"
        response = requests.get(address_url, headers=dabang_headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address")

        # 상세 정보
        registration_url = f"https://www.dabangapp.com/api/3/new-room/detail?api_version=3.0.1&call_type=web&room_id={id}&version=1"
        response = requests.get(registration_url, headers=dabang_headers)
        if response.status_code == 200:
            data = response.json()
            registration_name = data.get("agent").get("name")
            agent_name = data.get("agent").get("facename")
            registration_number = data.get("agent").get("reg_id")
            direction = data.get("room").get("direction_str")
        else:
            print(f"Request failed with status code {response.status_code}")

        data_for_parquet.append(
            {
                "room_id": id,
                "platform": "다방",
                "service_type": room.get("roomTypeName"),
                "title": room.get("roomTitle"),
                "floor": roomDesc[0].strip(),
                "area": float(area),
                "deposit": int(deposit_num),
                "rent": int(monthly_fee),
                "maintenance_fee": int(manage_money),
                "address": address,
                "latitude": float(lat),
                "longitude": float(lng),
                "property_link": "https://www.dabangapp.com/room/"
                + room.get("id"),
                "registration_number": registration_number,
                "agency_name": registration_name,
                "agent_name": agent_name,
                "subway_count": subway.get("count"),
                "nearest_subway_distance": subway.get("nearest_distance"),
                "store_count": store.get("count"),
                "nearest_store_distance": store.get("nearest_distance"),
                "cafe_count": cafe.get("count"),
                "nearest_cafe_distance": cafe.get("nearest_distance"),
                "market_count": mart.get("count"),
                "nearest_market_distance": mart.get("nearest_distance"),
                "restaurant_count": food.get("count"),
                "nearest_restaurant_distance": food.get("nearest_distance"),
                "hospital_count": hospital.get("count"),
                "nearest_hospital_distance": hospital.get("nearest_distance"),
                "image_link": img_url,
                "direction": direction,
            }
        )
    return data_for_parquet


def save_to_parquet(data, filename):
    df = pd.DataFrame(data)

    df["area"] = df["area"].astype("float32")
    df["deposit"] = df["deposit"].astype("Int64")
    df["rent"] = df["rent"].astype("Int64")
    df["maintenance_fee"] = df["maintenance_fee"].astype("float32")
    df["latitude"] = df["latitude"].astype("float32")
    df["longitude"] = df["longitude"].astype("float32")

    df["market_count"] = pd.to_numeric(
        df["market_count"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["store_count"] = pd.to_numeric(
        df["store_count"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["subway_count"] = pd.to_numeric(
        df["subway_count"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["restaurant_count"] = pd.to_numeric(
        df["restaurant_count"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["cafe_count"] = pd.to_numeric(df["cafe_count"], errors="coerce").astype(
        pd.Int64Dtype()
    )
    df["hospital_count"] = pd.to_numeric(
        df["hospital_count"], errors="coerce"
    ).astype(pd.Int64Dtype())

    df["nearest_subway_distance"] = pd.to_numeric(
        df["nearest_subway_distance"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["nearest_store_distance"] = pd.to_numeric(
        df["nearest_store_distance"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["nearest_cafe_distance"] = pd.to_numeric(
        df["nearest_cafe_distance"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["nearest_market_distance"] = pd.to_numeric(
        df["nearest_market_distance"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["nearest_restaurant_distance"] = pd.to_numeric(
        df["nearest_restaurant_distance"], errors="coerce"
    ).astype(pd.Int64Dtype())
    df["nearest_hospital_distance"] = pd.to_numeric(
        df["nearest_hospital_distance"], errors="coerce"
    ).astype(pd.Int64Dtype())

    df.to_parquet(filename, engine="pyarrow", index=False)
    print(f"Data has been written to {filename}")


def get_data_by_range(start, end):
    data_for_parquet = []
    cnt = 0
    for page in range(start, end):
        room_list = fetch_rooms(dabang_base_url, page)
        if room_list:
            processed_data = process_rooms(room_list)
            data_for_parquet.extend(processed_data)
            cnt += len(room_list)
        else:
            break
    file_path = "/opt/airflow/data/dabang.parquet"
    save_to_parquet(data_for_parquet, file_path)
    return file_path

def get_data_all():
    cnt = 0
    page = 1
    data_for_parquet = []
    while True:

        room_list = fetch_rooms(dabang_base_url, page)

        if room_list:
            processed_data = process_rooms(room_list)
            data_for_parquet.extend(processed_data)
            cnt += len(room_list)
            page += 1
        else:
            print("No more rooms found. Exiting.")
            break
    file_path = "/opt/airflow/data/dabang.parquet"
    save_to_parquet(data_for_parquet, file_path)
    print(f"총 개수: {cnt}")
    return file_path