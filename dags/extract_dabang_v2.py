import requests
import csv
import re
import pandas as pd

# API 키 모음
# vworld_api_key = "F5B25757-5CED-3188-BB82-B0A2522DCB6A"
kakao_api_key = "KakaoAK f48c38a5cf26ec7a7bd7b54c20f2f994"
# 다방 request url
base_url = "https://www.dabangapp.com/api/v5/room-list/category/one-two/bbox?bbox=%7B%22sw%22%3A%7B%22lat%22%3A37.4401052%2C%22lng%22%3A126.6997919%7D%2C%22ne%22%3A%7B%22lat%22%3A37.6893849%2C%22lng%22%3A127.2484216%7D%7D&filters=%7B%22sellingTypeList%22%3A%5B%22MONTHLY_RENT%22%5D%2C%22depositRange%22%3A%7B%22min%22%3A0%2C%22max%22%3A999999%7D%2C%22priceRange%22%3A%7B%22min%22%3A0%2C%22max%22%3A999999%7D%2C%22isIncludeMaintenance%22%3Afalse%2C%22pyeongRange%22%3A%7B%22min%22%3A0%2C%22max%22%3A999999%7D%2C%22roomFloorList%22%3A%5B%22GROUND_FIRST%22%2C%22GROUND_SECOND_OVER%22%2C%22SEMI_BASEMENT%22%2C%22ROOFTOP%22%5D%2C%22roomTypeList%22%3A%5B%22ONE_ROOM%22%2C%22TWO_ROOM%22%5D%2C%22dealTypeList%22%3A%5B%22AGENT%22%2C%22DIRECT%22%5D%2C%22canParking%22%3Afalse%2C%22isShortLease%22%3Afalse%2C%22hasElevator%22%3Afalse%2C%22hasPano%22%3Afalse%2C%22isDivision%22%3Afalse%2C%22isDuplex%22%3Afalse%7D&page={page}&useMap=naver&zoom=11"
headers = {
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
        "category_group_code": category_group_code[category],
    }

    data = requests.get(url, params=params, headers=headers).json()
    count = data["meta"]["total_count"]
    if count > 0:
        nearest_distance = data["documents"][0]["distance"]
    else:
        nearest_distance = None

    return {"count": count, "nearest_distance": nearest_distance}


# def get_address(lat, lng):
#     base_url = "http://api.vworld.kr/req/address"
#     params = {
#         "service": "address",
#         "request": "getaddress",
#         "version": "2.0",
#         "format": "json",
#         "crs": "epsg:4326",
#         "point": f"{lng},{lat}",
#         "type": "both",
#         "key": vworld_api_key,
#     }

#     response = requests.get(base_url, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         if data["response"]["status"] == "OK":
#             address = data["response"]["result"][0]["text"]
#             return address
#         else:
#             return "No address found"
#     else:
#         return f"Request failed with status code {response.status_code}"


def fetch_rooms(base_url, page):
    current_url = base_url.format(page=page)
    response = requests.get(current_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        room_list = data.get("result", {}).get("roomList")
        return room_list
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


def process_rooms(room_list):
    data_for_csv = []
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

        # 주소 받아오기
        address_url = f"https://www.dabangapp.com/api/3/room/near?api_version=3.0.1&call_type=web&room_id={id}&version=1"
        response = requests.get(address_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address")

        # 부동산 정보 받아오기
        registration_url = f"https://www.dabangapp.com/api/3/new-room/detail?api_version=3.0.1&call_type=web&room_id={id}&version=1"
        response = requests.get(registration_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            registration_name = data.get("agent").get("name")
            agent_name = data.get("agent").get("facename")
            registration_number = data.get("agent").get("reg_id")
        else:
            print(f"Request failed with status code {response.status_code}")

        data_for_csv.append(
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
                "property_link": "https://www.dabangapp.com/room/" + room.get("id"),
                "registration_number": registration_number,
                "agency_name": registration_name,
                "agent_name": agent_name,
                "subway_count": subway.get("count"),
                "nearest_subway_dsitance": subway.get("nearest_distance"),
                "store_count": store.get("count"),
                "nearest_store_distance": store.get("nearest_distance"),
                "cafe_count": cafe.get("count"),
                "nearest_cafe_distance": cafe.get("nearest_distance"),
                "supermart_count": mart.get("count"),
                "nearest_supermart_distance": mart.get("nearest_distance"),
                "restaurant_count": food.get("count"),
                "nearest_restaurant_distance": food.get("nearest_distance"),
                "hospital_count": hospital.get("count"),
                "nearest_hospital_distance": hospital.get("nearest_distance"),
                "img_link": img_url,
            }
        )
    return data_for_csv


def save_to_csv(data, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "room_id",
                "platform",
                "service_type",
                "title",
                "floor",
                "area",
                "deposit",
                "rent",
                "maintenance_fee",
                "address",
                "latitude",
                "longitude",
                "property_link",
                "registration_number",
                "agency_name",
                "agent_name",
                "subway_count",
                "nearest_subway_distance",
                "store_count",
                "nearest_store_distance",
                "cafe_count",
                "nearest_cafe_distance",
                "market_count",
                "nearest_market_distance",
                "restaurant_count",
                "nearest_restaurant_distance",
                "hospital_count",
                "nearest_hospital_distance",
                "img_link",
            ],
        )
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Data has been written to {filename}")


def save_to_parquet(data, filename):
    df = pd.DataFrame(data)

    df["area"] = df["area"].astype("float32")
    df["deposit"] = df["deposit"].astype("Int64")
    df["rent"] = df["rent"].astype("Int64")
    df["maintenance_fee"] = df["maintenance_fee"].astype("float32")
    df["latitude"] = df["latitude"].astype("float32")
    df["longitude"] = df["longitude"].astype("float32")

    df["market_count"] = df["market_count"].astype("Int64")
    df["store_count"] = df["store_count"].astype("Int64")
    df["subway_count"] = df["subway_count"].astype("Int64")
    df["restaurant_count"] = df["restaurant_count"].astype("Int64")
    df["cafe_count"] = df["cafe_count"].astype("Int64")
    df["hospital_count"] = df["hospital_count"].astype("Int64")

    df["nearest_market_distance"] = df["nearest_market_distance"].astype("Int64")
    df["nearest_store_distance"] = df["nearest_store_distance"].astype("Int64")
    df["nearest_subway_distance"] = df["nearest_subway_distance"].astype("Int64")
    df["nearest_restaurant_distance"] = df["nearest_restaurant_distance"].astype(
        "Int64"
    )
    df["nearest_cafe_distance"] = df["nearest_cafe_distance"].astype("Int64")
    df["nearest_hospital_distance"] = df["nearest_hospital_distance"].astype("Int64")
    df.to_parquet(filename, engine="pyarrow", index=False)
    print(f"Data has been written to {filename}")


def get_data_by_range(start, end):
    data_for_csv = []
    cnt = 0
    for page in range(start, end):
        room_list = fetch_rooms(base_url, page)
        if room_list:
            processed_data = process_rooms(room_list)
            data_for_csv.extend(processed_data)
            cnt += len(room_list)
        else:
            break
    # save_to_csv(data_for_csv, "dabang_sapling_120.csv")
    # save_to_csv(data_for_csv, "/opt/airflow/data/dabang_sampling.csv")
    # save_to_parquet(data_for_csv, "/opt/airflow/data/dabang_sampling.parquet")
    save_to_parquet(data_for_csv, "test.parquet")
    print(f"총 개수: {cnt}")


def get_data_all():
    cnt = 0
    page = 1
    data_for_csv = []
    while True:

        room_list = fetch_rooms(base_url, page)
        print(f"{page}페이지 방 정보 가져오는 중")
        # Check if 'roomList' is found and if it's empty
        if room_list:
            processed_data = process_rooms(room_list)
            print(f"{page}페이지 데이터 처리 중")
            data_for_csv.extend(processed_data)
            print(f"{page}페이지 데이터 저장 중")
            cnt += len(room_list)
            page += 1
        else:
            print("No more rooms found. Exiting.")
            break
    # save_to_csv(data_for_csv, "/opt/airflow/data/dabang.csv")
    save_to_parquet(data_for_csv, "/opt/airflow/data/dabang.parquet")
    print(f"총 개수: {cnt}")


def read_parquet_file(filename):
    df = pd.read_parquet(filename, engine="pyarrow")

    # 데이터 확인
    print(df.head())
    print(df.info())
    print(df.describe())

    return df


get_data_by_range(1, 6)
