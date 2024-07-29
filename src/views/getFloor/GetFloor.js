import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import style from "./GetFloor.module.css";

const floorOptions = ["옥탑방", "반지하"];

const GetFloor = () => {
  const location = useLocation();
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [existingParams, setExistingParams] = useState('');

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    setExistingParams(searchParams.toString());
  }, [location.search]);

  const toggleOption = (option) => {
    setSelectedOptions(prevSelected =>
      prevSelected.includes(option)
        ? prevSelected.filter(opt => opt !== option)
        : [...prevSelected, option]
    );
  };

  const getNextUrl = () => {
    const selectedParams = new URLSearchParams(existingParams);
    selectedParams.set('selectedOptions', selectedOptions.join(','));
    return `/info?${selectedParams.toString()}`;
  };

  return (
    <>
      <h1 className={style.title}>옥탑, 반지하 입력 페이지 입니다.</h1>
      <section className={style.section}>
        <p className={style.question}>옥탑방이나 반지하 정보도 받으시겠어요?</p>
        <div className={style.options}>
          {floorOptions.map(option => (
            <div key={option} className={style.option} onClick={() => toggleOption(option)}>
              <input 
                type="checkbox" 
                checked={selectedOptions.includes(option)} 
                readOnly 
              />
              <span>{option}</span>
            </div>
          ))}
        </div>
      </section>
      <Link to={getNextUrl()} className={style.link}>이동</Link>
    </>
  );
};

export default GetFloor;
