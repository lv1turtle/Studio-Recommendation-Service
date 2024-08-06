import style from "./ViewInfo.module.css"
import React, { useEffect, useState } from "react";
import { getFilter } from "../../apis/Filter";
import { useRecoilValue } from "recoil";
import { addressAtom } from "../../stores/addressAtom";
import {Link} from "react-router-dom";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";
import NaverMap from "../../common/map/NaverMap";

const ViewInfo = () => {
  const address = useRecoilValue(addressAtom);
  const [show,setShow] = useState(true);
  const [data, setData] = useState([
    {
      "id": 6,
      "room_id": "663a26a2aaf4ba266766abc6",
      "platform": "다방",
      "service_type": "원룸",
      "title": "O성북천변 신축급 풀옵션원룸O성신여대역도보4분거리O",
      "floor": "반지층",
      "area": 38.56,
      "deposit": 3000,
      "rent": 45,
      "is_safe" : true,
      "maintenance_fee": 0,
      "address": "서울특별시 성북구 삼선동4가 370",
      "latitude": 37.5905265987,
      "longitude": 127.0160011626,
      "property_link": "https://www.dabangapp.com/room/663a26a2aaf4ba266766abc6",
      "registration_number": "11110-2024-00013",
      "agency_name": "미래공인중개사사무소",
      "agent_name": "이경숙",
      "subway_count": 5,
      "nearest_subway_distance": 288,
      "store_count": 45,
      "nearest_store_distance": 68,
      "cafe_count": 390,
      "nearest_cafe_distance": 385,
      "market_count": 1,
      "nearest_market_distance": 192,
      "restaurant_count": 792,
      "nearest_restaurant_distance": 193,
      "hospital_count": 147,
      "nearest_hospital_distance": 344,
      "image_link": "https://d1774jszgerdmk.cloudfront.net/512/6625bcd0-96ec-4d14-8823-2a987b70e1d1"
    },
    {
      "id": 1,
      "room_id": "668faa24e2865a39fa49adca",
      "platform": "다방",
      "service_type": "원룸",
      "is_safe" : true,
      "title": "V.신축급넓은방 V.채광굿 V.즉입가능",
      "floor": "반지층",
      "area": 19.83,
      "deposit": 4000,
      "rent": 10,
      "maintenance_fee": 6,
      "address": "서울특별시 성북구 석관동 338-22",
      "latitude": 37.6060813892881,
      "longitude": 127.051588783806,
      "property_link": "https://www.dabangapp.com/room/668faa24e2865a39fa49adca",
      "registration_number": "가-92280000-공인2527",
      "agency_name": "현탑공인중개사사무소",
      "agent_name": "정현연",
      "subway_count": 3,
      "nearest_subway_distance": 249,
      "store_count": 16,
      "nearest_store_distance": 131,
      "cafe_count": 131,
      "nearest_cafe_distance": 979,
      "market_count": 1,
      "nearest_market_distance": 1125,
      "restaurant_count": 68,
      "nearest_restaurant_distance": 346,
      "hospital_count": 57,
      "nearest_hospital_distance": 834,
      "image_link": "https://d1774jszgerdmk.cloudfront.net/512/koOP4QkN1Lc_JyOqT52jZ"
    },
    {
      "id": 8,
      "room_id": "6699f57dce80bf7a322861fe",
      "platform": "다방",
      "service_type": "투룸",
      "is_safe" : true,
      "title": "깔끔하게 리모델링 된 넉넉한 사이즈의 투룸",
      "floor": "반지층",
      "area": 35.0,
      "deposit": 1000,
      "rent": 60,
      "maintenance_fee": 0,
      "address": "서울특별시 동대문구 휘경동 293-39",
      "latitude": 37.586663853953,
      "longitude": 127.059876457558,
      "property_link": "https://www.dabangapp.com/room/6699f57dce80bf7a322861fe",
      "registration_number": "11230-2022-00018",
      "agency_name": "명성공인중개사사무소",
      "agent_name": "정우진",
      "subway_count": 3,
      "nearest_subway_distance": 383,
      "store_count": 39,
      "nearest_store_distance": 46,
      "cafe_count": 246,
      "nearest_cafe_distance": 308,
      "market_count": 1,
      "nearest_market_distance": 1217,
      "restaurant_count": 182,
      "nearest_restaurant_distance": 332,
      "hospital_count": 48,
      "nearest_hospital_distance": 504,
      "image_link": "https://d1774jszgerdmk.cloudfront.net/512/hos0_vEalaOzAGxMNMfoo"
    },
    {
      "id": 2,
      "room_id": "669732bed387a56c3c0fa1fe",
      "platform": "다방",
      "service_type": "원룸",
      "is_safe" : true,
      "title": "역인근저렴한 원룸",
      "floor": "반지층",
      "area": 22.0,
      "deposit": 1000,
      "rent": 30,
      "maintenance_fee": 7,
      "address": "서울특별시 강서구 화곡동 1057-10",
      "latitude": 37.5441078065253,
      "longitude": 126.841854623417,
      "property_link": "https://www.dabangapp.com/room/669732bed387a56c3c0fa1fe",
      "registration_number": "11500-2017-00168",
      "agency_name": "황금공인중개사사무소",
      "agent_name": "한미영",
      "subway_count": 2,
      "nearest_subway_distance": 299,
      "store_count": 46,
      "nearest_store_distance": 33,
      "cafe_count": 193,
      "nearest_cafe_distance": 555,
      "market_count": 1,
      "nearest_market_distance": 1270,
      "restaurant_count": 379,
      "nearest_restaurant_distance": 224,
      "hospital_count": 150,
      "nearest_hospital_distance": 295,
      "image_link": "https://d1774jszgerdmk.cloudfront.net/512/4b898255-aed2-4b55-8555-62849f12e2dd"
    },
    {
      "id": 7,
      "room_id": "6697214cb921952792c54d4e",
      "platform": "다방",
      "service_type": "원룸",
      "is_safe" : true,
      "title": "V.신축급최고 V.주택가입구안전 V.옷장수납큼",
      "floor": "2층",
      "area": 16.5,
      "deposit": 8000,
      "rent": 25,
      "maintenance_fee": 7,
      "address": "서울특별시 성북구 하월곡동 15-7",
      "latitude": 37.6028268408843,
      "longitude": 127.043274233827,
      "property_link": "https://www.dabangapp.com/room/6697214cb921952792c54d4e",
      "registration_number": "가-92280000-공인2527",
      "agency_name": "현탑공인중개사사무소",
      "agent_name": "정현연",
      "subway_count": 2,
      "nearest_subway_distance": 196,
      "store_count": 20,
      "nearest_store_distance": 144,
      "cafe_count": 124,
      "nearest_cafe_distance": 202,
      "market_count": 3,
      "nearest_market_distance": 311,
      "restaurant_count": 241,
      "nearest_restaurant_distance": 187,
      "hospital_count": 69,
      "nearest_hospital_distance": 132,
      "image_link": "https://d1774jszgerdmk.cloudfront.net/512/zkyzhvKGOpyLrjbhxrIyY"
    },
    {
      "id": 4,
      "room_id": "664ac91211f76523d44168e1",
      "platform": "다방",
      "service_type": "원룸",
      "is_safe" : true,
      "title": "V.신축급최고 V. KIST추천 V.주택가안심",
      "floor": "3층",
      "area": 16.5,
      "deposit": 5000,
      "rent": 38,
      "maintenance_fee": 7,
      "address": "서울특별시 성북구 하월곡동 15-7",
      "latitude": 37.6028268408843,
      "longitude": 127.043274233827,
      "property_link": "https://www.dabangapp.com/room/664ac91211f76523d44168e1",
      "registration_number": "가-92280000-공인2527",
      "agency_name": "현탑공인중개사사무소",
      "agent_name": "정현연",
      "subway_count": 2,
      "nearest_subway_distance": 196,
      "store_count": 20,
      "nearest_store_distance": 144,
      "cafe_count": 124,
      "nearest_cafe_distance": 202,
      "market_count": 3,
      "nearest_market_distance": 311,
      "restaurant_count": 241,
      "nearest_restaurant_distance": 187,
      "hospital_count": 69,
      "nearest_hospital_distance": 132,
      "image_link": "https://d1774jszgerdmk.cloudfront.net/512/woD5nqXZFrrH_K_Xahb0z"
    }
  ]);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(5);

  useEffect(() => {
    console.log(address);
    getFilter(address).then((response) => {
      console.log(response);
      setData(response.data);
      setTotalPages(response.data.length);
    }).catch((error) => {
      console.error(error);
    });
  }, [address]);

  const handlePageClick = (page) => {
    setCurrentPage(page);
  };

  const handlePrevPage = () => {
    setCurrentPage((prevPage) => Math.max(prevPage - 1, 0));
  };

  const handleNextPage = () => {
    setCurrentPage((prevPage) => Math.min(prevPage + 1, totalPages - 1));
  };

  const renderPagination = () => {
    const pageNumbers = [];
    const maxPageNumbers = 5;
    const halfPageNumbers = Math.floor(maxPageNumbers / 2);
    
    let startPage = Math.max(0, currentPage - halfPageNumbers);
    let endPage = Math.min(totalPages - 1, currentPage + halfPageNumbers);

    if (currentPage <= halfPageNumbers) {
      endPage = Math.min(totalPages - 1, maxPageNumbers - 1);
    } else if (currentPage + halfPageNumbers >= totalPages - 1) {
      startPage = Math.max(0, totalPages - maxPageNumbers);
    }

    for (let i = startPage; i <= endPage; i++) {
      pageNumbers.push(
        <button
          key={i}
          className={currentPage === i ? style.active : ""}
          onClick={() => handlePageClick(i)}
        >
          {i + 1}
        </button>
      );
    }

    if (startPage > 0) {
      pageNumbers.unshift(<span key="start-ellipsis">...</span>);
      pageNumbers.unshift(
        <button key={0} onClick={() => handlePageClick(0)}>
          1
        </button>
      );
    }

    if (endPage < totalPages - 1) {
      pageNumbers.push(<span key="end-ellipsis">...</span>);
      pageNumbers.push(
        <button key={totalPages - 1} onClick={() => handlePageClick(totalPages - 1)}>
          {totalPages}
        </button>
      );
    }

    return (
      <div className={style.pagination}>
        <button onClick={handlePrevPage} disabled={currentPage === 0}>
          이전
        </button>
        {pageNumbers}
        <button onClick={handleNextPage} disabled={currentPage === totalPages - 1}>
          다음
        </button>
      </div>
    );
  };

  return (
    <>
      <div className={style.container}>
        <Header />
        <main className={style.main}>
          {data.length > 0 ? (
            <div>
              <div className={style.filterBox}>
                <h3 className={show ? style.show : style.noshow}>현재 적용된 옵션</h3>
                <p className={show ? style.show : style.noshow}>위치 : {address.address}</p>
                <p className={show ? style.show : style.noshow}>보증금 : {address.min_deposit}만원 ~ {address.max_deposit}만원</p>
                <p className={show ? style.show : style.noshow}>월세 : {address.min_rent}만원 ~ {address.max_rent}만원</p>
                <p className={show ? style.show : style.noshow}>관리비 포함 여부 : {address.include_maintenance_fee ? "O" : "X"}</p>
                {address.facilities.length > 0 ? <p className={show ? style.show : style.noshow}>주변 시설 : {
                  address.facilities.map((item,index) => index === address.facilities.length -1 ? <span>{item}</span> : <span>{item}, </span>)
                }</p> : <></>}
                {address.floor_options.length > 0 ? <p className={show ? style.show : style.noshow}>반지하/옥탑 제외 여부 : {
                  address.floor_options.map((item,index) => index === address.floor_options.length-1 ? <span>{item} 제외</span> : <span>{item} 제외, </span>)
                }</p> : <></>}
                <div className={style.toggleButton} onClick={() => setShow(!show)}><img src={show ? `${process.env.PUBLIC_URL}/arrow.svg`:`${process.env.PUBLIC_URL}/arrow-down.svg`} alt=""/></div>
              </div>
              <div className={style.card}>
                {currentPage < 3 ? <img className={style.crown} src={`${process.env.PUBLIC_URL}/crown.svg`} alt=""/> : <></>}
                <b className={style.rank}>{currentPage + 1}위!</b>
                <h3>{data[currentPage].title}</h3>
                <img src={data[currentPage].image_link} alt="매물 사진"/>
                <h4>가격정보</h4>
                <div className={style.line}><b>보증금/월세</b> <p>{data[currentPage].deposit}/{data[currentPage].rent}</p>
                </div>
                <div className={style.line}><b>관리비</b> <p>{data[currentPage].maintenance_fee}만원</p></div>
                <h4>상세정보</h4>
                <div className={style.line}><b>안심 중개사</b> <p>{data[currentPage].is_safe ? "O" : "X"}</p></div>
                <div className={style.line}><b>방</b> <p>{data[currentPage].service_type}</p></div>
                <div className={style.line}><b>평수</b><p>{data[currentPage].area}m²/
                  약{(data[currentPage].area / 3.31).toFixed(1)}평</p></div>
                <div className={style.line}><b>층</b> <p>{data[currentPage].floor}</p></div>
                <div className={style.line}><b>주소</b> <p>{data[currentPage].address}</p></div>
                <div className={style.line}><b>매물 링크</b> <a target="_blank"
                                                            href={data[currentPage].property_link}>{data[currentPage].property_link}</a>
                </div>
                <h4>위치 및 주변 편의 시설</h4>
                {data[currentPage].latitude && data[currentPage].longitude && (
                  <NaverMap latitude={data[currentPage].latitude} longitude={data[currentPage].longitude}/>
                )}
                {Number(data[currentPage].subway_count) > 0 && (
                  <div className={style.line}>
                    <b>가장 가까운 지하철</b>
                    <div className={style.line2}>
                      <p>{data[currentPage].nearest_subway_distance}m</p>
                    </div>
                  </div>
                )}
                {Number(data[currentPage].store_count) > 0 && (
                  <div className={style.line}>
                    <b>가장 가까운 편의점</b>
                    <div className={style.line2}>
                      <p>{data[currentPage].nearest_store_distance}m</p>
                    </div>
                  </div>
                )}
                {Number(data[currentPage].cafe_count) > 0 && (
                  <div className={style.line}>
                    <b>가장 가까운 카페</b>
                    <div className={style.line2}>
                      <p>{data[currentPage].nearest_cafe_distance}m</p>
                    </div>
                  </div>
                )}
                {Number(data[currentPage].market_count) > 0 && (
                  <div className={style.line}>
                    <b>가장 가까운 대형마트</b>
                    <div className={style.line2}>
                      <p>{data[currentPage].nearest_market_distance}m</p>
                    </div>
                  </div>
                )}
                {Number(data[currentPage].restaurant_count) > 0 && (
                  <div className={style.line}>
                    <b>가장 가까운 음식점</b>
                    <div className={style.line2}>
                      <p>{data[currentPage].nearest_restaurant_distance}m</p>
                    </div>
                  </div>
                )}
                {Number(data[currentPage].hospital_count) > 0 && (
                  <div className={style.line}>
                    <b>가장 가까운 병원</b>
                    <div className={style.line2}>
                      <p>{data[currentPage].nearest_hospital_distance}m</p>
                    </div>
                  </div>
                )}
              </div>
              {renderPagination()}
            </div>
          ) : (
            <div className={style.card}>
                <p>해당하는 매물이 없습니다!</p>
                <p>다시 검색해 주세요.</p>
                <div className={style["logo"]}><Link to="/">돌아가기</Link></div>
            </div>
          )}
        </main>
        <Footer/>
      </div>
    </>
  );
};

export default ViewInfo;