from extract_zigbang import extract_room_ids_from_geohash, extract_room_info
import pandas as pd

if "__main__" == __name__:
    geohashs = ["wydnp", "wydju", "wydjv", "wydjy", "wydjz", "wydjs", "wydjt", "wydjw", "wydjx", "wydjk", "wydjm", "wydjq", "wydjr", "wydjh", "wydjj", "wydjn", "wydjp", \
                "wydhzx", "wydhzz", "wydhzw", "wydhzy", "wydq8", "wydq9", "wydqd", "wydqe", "wydqs", "wydq2", "wydq3", "wydq6", "wydq7", "wydqk", "wydq0", "wydq1", "wydq4", "wydq5", "wydqh", \
                "wydmb", "wydmc", "wydmf", "wydmg", "wydmu", "wydmv", "wydmy",  "wydm8", "wydm9", "wydmd", "wydme", "wydms", "wydmt", "wydmw", "wydm2", "wydm3", "wydm6", "wydm7", \
                "wydmk", "wydmm", "wydm0", "wydm1", "wydm4", "wydm5", "wydmh", "wydmj"]

    # geohashs = ["wydhzw", "wydhzy", "wydq", "wydm"]

    print("[ extract room id start ]")
    ids = []
    for geohash in geohashs:
        print(geohash)
        ids.extend(extract_room_ids_from_geohash(geohash))
    print("[ extract room id end ]\n")

    print(f"[ total id : {len(ids)} ]\n")

    print("[ extract room info start ]")

    data = []

    for i, id in enumerate(ids):
        print(i, id)
        if i%5000 == 0:
            room = extract_room_info(id, delay=2)
        else:
            room = extract_room_info(id, delay=0)

        if room:
            data.append(room)
        
    print("[ extract room info end ]")

    df = pd.DataFrame(data)

    df.to_csv("zigbang_sample_v2.csv", encoding='utf-8', index=False)

    print("[ load csv end ]")