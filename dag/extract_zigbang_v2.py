import requests
from time import sleep


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
                room_data["address"] = item_data["jibunAddress"] if "jibunAddress" in item_data.keys() else item_data["addressOrigin"]["localText"]
                room_data["property_link"] = "https://sp.zigbang.com/share/" + room_type_to_eng[item_data["serviceType"]] + "/" +str(item_data["itemId"])

                agent_info = get_agent_info(json_data["agent"]["agentUserNo"], delay)
                room_data["registration_number"] = agent_info["agentRegid"]
                room_data["agency_name"] = agent_info["agentName"]
                room_data["agent_name"] = agent_info["userName"]
                
                room_data["title"] = item_data["title"]
                room_data["description"] = item_data["description"]
                room_data["image_link"] = item_data["imageThumbnail"] + "?w=400&h=300&q=70&a=1"

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