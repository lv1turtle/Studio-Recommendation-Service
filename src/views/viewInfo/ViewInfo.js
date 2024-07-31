import style from "./ViewInfo.module.css"
import React, {useEffect, useState} from "react";
import {getFilter} from "../../apis/Filter";
import {useRecoilValue} from "recoil";
import {addressAtom} from "../../stores/addressAtom";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";
import NaverMap from "../../common/map/NaverMap";

const ViewInfo = () => {
  const address = useRecoilValue(addressAtom);
  const [data, setData] = useState([
    // {
    //   "id": 6,
    //   "room_id": "663a26a2aaf4ba266766abc6",
    //   "platform": "다방",
    //   "service_type": "원룸",
    //   "title": "O성북천변 신축급 풀옵션원룸O성신여대역도보4분거리O",
    //   "floor": "반지층",
    //   "area": 38.56,
    //   "deposit": 3000,
    //   "rent": 45,
    //   "maintenance_fee": 0,
    //   "address": "서울특별시 성북구 삼선동4가 370",
    //   "latitude": 37.5905265987,
    //   "longitude": 127.0160011626,
    //   "property_link": "https://www.dabangapp.com/room/663a26a2aaf4ba266766abc6",
    //   "registration_number": "11110-2024-00013",
    //   "agency_name": "미래공인중개사사무소",
    //   "agent_name": "이경숙",
    //   "subway_count": 5,
    //   "nearest_subway_distance": 288,
    //   "store_count": 45,
    //   "nearest_store_distance": 68,
    //   "cafe_count": 390,
    //   "nearest_cafe_distance": 385,
    //   "market_count": 1,
    //   "nearest_market_distance": 192,
    //   "restaurant_count": 792,
    //   "nearest_restaurant_distance": 193,
    //   "hospital_count": 147,
    //   "nearest_hospital_distance": 344,
    //   "image_link": "https://d1774jszgerdmk.cloudfront.net/512/6625bcd0-96ec-4d14-8823-2a987b70e1d1"
    // },
    // {
    //   "id": 1,
    //   "room_id": "668faa24e2865a39fa49adca",
    //   "platform": "다방",
    //   "service_type": "원룸",
    //   "title": "V.신축급넓은방 V.채광굿 V.즉입가능",
    //   "floor": "반지층",
    //   "area": 19.83,
    //   "deposit": 4000,
    //   "rent": 10,
    //   "maintenance_fee": 6,
    //   "address": "서울특별시 성북구 석관동 338-22",
    //   "latitude": 37.6060813892881,
    //   "longitude": 127.051588783806,
    //   "property_link": "https://www.dabangapp.com/room/668faa24e2865a39fa49adca",
    //   "registration_number": "가-92280000-공인2527",
    //   "agency_name": "현탑공인중개사사무소",
    //   "agent_name": "정현연",
    //   "subway_count": 3,
    //   "nearest_subway_distance": 249,
    //   "store_count": 16,
    //   "nearest_store_distance": 131,
    //   "cafe_count": 131,
    //   "nearest_cafe_distance": 979,
    //   "market_count": 1,
    //   "nearest_market_distance": 1125,
    //   "restaurant_count": 68,
    //   "nearest_restaurant_distance": 346,
    //   "hospital_count": 57,
    //   "nearest_hospital_distance": 834,
    //   "image_link": "https://d1774jszgerdmk.cloudfront.net/512/koOP4QkN1Lc_JyOqT52jZ"
    // }
  ]); // 데이터를 저장할 상태 변수 추가

  useEffect(() => {
    getFilter(address).then((response) => {
      console.log(response);
      setData(response.data); // 데이터 상태 업데이트
    }).catch((error) => {
      console.error(error);
    });
  }, [address]); // address가 변경될 때마다 useEffect 실행

  return (
    <>
      <div className={style.container}>
        <Header />
        <main className={style.main}>
          {data.length > 0 ? (
            data.map((item, index) => (
              <div key={index} className={style.card}>
                <h3>{item.title}</h3>
                <img src={item.image_link} alt="매물 사진"/>
                <h4>가격정보</h4>
                <div className={style.line}><b>월세</b> <p>{item.deposit}/{item.rent}</p></div>
                <div className={style.line}><b>관리비</b> <p>{item.maintenance_fee}만원</p></div>
                <h4>상세정보</h4>
                <div className={style.line}><b>방</b> <p>{item.service_type}</p></div>
                <div className={style.line}><b>평수</b><p>{item.area}m²/ 약{(item.area / 3.31).toFixed(1)}평</p> </div>
                {/* <div className={style.line}><b>평수</b> <p>{item.area}m²/{item.area/3.31}평</p> </div> */}
                <div className={style.line}><b>층</b> <p>{item.floor}</p></div>
                <div className={style.line}><b>주소</b> <p>{item.address}</p></div>
                <div className={style.line}><b>매물 링크</b> <a href={item.property_link}>{item.property_link}</a></div>
                <h4>위치 및 주변 편의 시설</h4>
                <NaverMap latitude={item.latitude} longitude={item.longitude} />
                {Number(item.subway_count) > 0 ? <>
                  <div className={style.line}>
                    <b>지하철</b>
                    <div className={style.line2}>
                      <p>{item.subway_count}개</p>
                      <span>/</span>
                      <p>{item.nearest_subway_distance}m</p>
                    </div>
                  </div>
                  <div><b></b> </div>
                </> : <></>}
                {Number(item.store_count) > 0 ? <>
                  <div className={style.line}>
                    <b>편의점</b>
                    <div className={style.line2}>
                      <p>{item.store_count}개</p>
                      <span>/</span>
                      <p>{item.nearest_store_distance}m</p>
                    </div>
                  </div>
                  <div><b></b> </div>
                </> : <></>}
                {Number(item.cafe_count) > 0 ? <>
                  <div className={style.line}>
                    <b>카페</b>
                    <div className={style.line2}>
                      <p>{item.cafe_count}개</p>
                      <span>/</span>
                      <p>{item.nearest_cafe_distance}m</p>
                    </div>
                  </div>
                  <div><b></b> </div>
                </> : <></>}
                {Number(item.market_count) > 0 ? <>
                  <div className={style.line}>
                    <b>대형마트</b>
                    <div className={style.line2}>
                      <p>{item.market_count}개</p>
                      <span>/</span>
                      <p>{item.nearest_market_distance}m</p>
                    </div>
                  </div>
                  <div><b></b> </div>
                </> : <></>}
                {Number(item.restaurant_count) > 0 ? <>
                  <div className={style.line}>
                    <b>음식점</b>
                    <div className={style.line2}>
                      <p>{item.restaurant_count}개</p>
                      <span>/</span>
                      <p>{item.nearest_restaurant_distance}m</p>
                    </div>
                  </div>
                  <div><b></b> </div>
                </> : <></>}
                {Number(item.hospital_count) > 0 ? <>
                <div className={style.line}>
                  <b>병원</b>
                  <div className={style.line2}>
                    <p>{item.hospital_count}개</p>
                    <span>/</span>
                    <p>{item.nearest_hospital_distance}m</p>
                  </div>
                </div>
                <div><b></b> </div>
              </> : <></>}
              </div>
            ))
          ) : (
            <div className={style.card}>
              <p>데이터를 불러오는 중...</p>
            </div>
          )}
        </main>
        <Footer />
      </div>
    </>
  );
};

export default ViewInfo;