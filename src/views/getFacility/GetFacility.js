import React, { useState } from 'react';
import styles from "./GetFacility.module.css";
import { Link } from "react-router-dom";

const facilitiesList = [
  "대형마트",
  "편의점",
  "지하철역",
  "음식점",
  "카페",
  "병원"
];

const GetFacility = () => {
  const [selectedFacilities, setSelectedFacilities] = useState([]);

  const toggleFacility = (facility) => {
    setSelectedFacilities(prevSelected =>
      prevSelected.includes(facility)
        ? prevSelected.filter(f => f !== facility)
        : [...prevSelected, facility]
    );
  };

  return (
    <>
      <h1 className={styles.title}>편의시설 입력 페이지 입니다.</h1>
      <section className={styles.section}>
        <p className={styles.question}>주변에 있었으면 하는 편의시설이 있나요?</p>
        <div className={styles.facilities}>
          {facilitiesList.map(facility => (
            <div key={facility} className={styles.facility} onClick={() => toggleFacility(facility)}>
              <input 
                type="checkbox" 
                checked={selectedFacilities.includes(facility)} 
                readOnly 
              />
              <span>{facility}</span>
            </div>
          ))}
        </div>
      </section>
      <Link 
        to={{
          pathname: "/address/cost/facility/floor",
          search: `?selectedFacilities=${selectedFacilities.join(',')}`
        }}
        className={styles.link}
      >
        이동
      </Link>
    </>
  );
};

export default GetFacility;
