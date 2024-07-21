import requests

url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
headers = {"Authorization": "KakaoAK 0b802f8cc02b1b1343b8706eaf18efd1"}
category_group_code = {"대형마트":"MT1",
                        "편의점":"CS2",
                        "지하철역":"SW8",
                        "은행":"BK9",
                        "음식점":"FD6",
                        "카페":"CE7",
                        "병원":"HP8",
                        "약국":"PM9"}

def extract_nearest_facilities_info(lng, lat, category, radius=500) -> dict:
    params = {'query' : category, 'x' : lng, 'y' : lat, 'radius' : radius, 'category_group_code' : category_group_code[category]}
    
    response = requests.get(url, params=params, headers=headers)
    
    try:
        data = response.json()
        count = data['meta']['total_count']
        if count > 0:
            nearest_distance = data["documents"][0]["distance"]  
        else: 
            nearest_distance = None
        
        return {"count":count, "nearest_distance":nearest_distance}
    
    except Exception as error:
        print("Error:", response.json())
        print(error)
        raise

