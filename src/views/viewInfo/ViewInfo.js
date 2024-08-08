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
  const [data, setData] = useState([]);
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
                <p>해당하는 매물이 없습니다!</p> */
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