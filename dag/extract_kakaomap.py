import requests

url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
headers = {"Authorization": "KakaoAK 0b802f8cc02b1b1343b8706eaf18efd1"}
category_group = {
                    "대형마트":{
                        "code":"MT1",
                        "radius":1712,
                        "eng":"marcket"
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


def extract_nearest_facilities_info(lng, lat, category) -> dict:
    params = {'query' : category, 'x' : lng, 'y' : lat, 'radius' : category_group[category]["radius"], 'category_group_code' : category_group[category]["code"]}
    
    response = requests.get(url, params=params, headers=headers)
    
    try:
        data = response.json()
        count = data['meta']['total_count']
        if count > 0:
            nearest_distance = int(data["documents"][0]["distance"])
        else: 
            nearest_distance = None
        
        return {"count":count, "nearest_distance":nearest_distance}
    
    except Exception as error:
        print("Error:", response.json())
        print(error)
        raise