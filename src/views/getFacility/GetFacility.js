import React, { useState } from 'react';
import styles from "./GetFacility.module.css";
import {Link, useNavigate} from "react-router-dom";
import Checkbox from "../../common/checkbox/Checkbox";
import CheckboxGroup from "../../common/checkbox/CheckboxGroup";
import {useRecoilValue, useSetRecoilState} from "recoil";
import {addressAtom} from "../../stores/addressAtom";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";

const facilitiesList = [
  "대형마트",
  "편의점",
  "지하철역",
  "음식점",
  "카페",
  "병원"
];

const GetFacility = () => {
  const setAddress = useSetRecoilState(addressAtom);
  const address = useRecoilValue(addressAtom);
  const [selectedFacilities, setSelectedFacilities] = useState([]);
  const navigate = useNavigate();

  const clickEvent = () => {
    setAddress({
      ...address,
      facilities : selectedFacilities,
    });
    navigate("/address/cost/facility/floor");
    console.log(address)
  }

  return (
    <>
      <div className={styles.container}>
        <Header />
        <main className={styles.main}>
          <div className={styles.card}>
            <h1 className={styles.title}>편의시설 입력 페이지 입니다.</h1>
            <section className={styles.section}>
              <p className={styles.question}>주변에 있었으면 하는 편의시설이 있나요?</p>
              <div className={styles.facilities}>
                <CheckboxGroup
                  label="편의 시설"
                  values={selectedFacilities}
                  onChange={setSelectedFacilities}
                >
                  <Checkbox value="대형마트">대형마트</Checkbox>
                  <Checkbox value="편의점">편의점</Checkbox>
                  <Checkbox value="지하철">지하철역</Checkbox>
                  <Checkbox value="음식점">음식점</Checkbox>
                  <Checkbox value="카페">카페</Checkbox>
                  <Checkbox value="병원">병원</Checkbox>
                </CheckboxGroup>
              </div>
              <button onClick={clickEvent} className={styles["move-button"]}>이동</button>
            </section>
          </div>
        </main>
        <Footer />
      </div>
    </>
  );
};

export default GetFacility;
