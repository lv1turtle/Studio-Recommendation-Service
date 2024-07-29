import style from "./GetCost.module.css";
import { Link } from "react-router-dom";
import ReactSlider from "react-slider";
import React, { useState } from "react";
import {useRecoilValue, useSetRecoilState} from "recoil";
import {addressAtom} from "../../stores/addressAtom";

const GetCost = () => {
  const [deposit, setDeposit] = useState([0, 15000]);
  const [rent, setRent] = useState([0, 600]);
  
  const setAddress = useSetRecoilState(addressAtom);
  const address = useRecoilValue(addressAtom);
  const [test,setTest] = useState("");

  const clickEvent = (e) => {
    e.preventDefault();
    setAddress({...address, test: test});
    console.log(address);
    // navigate("/address/cost");
  }
  return (
    <>
      <h1 className={style.title}>예상 보증금, 월세를 지정해주세요.</h1>
      <form action="">
        <input type="text" onChange={e=> setTest(e.target.value)}/>
        <input type="submit" onClick={clickEvent} value="O"/>
      </form>
      <div className={style["cost-container"]}>
        <div className={style["slider-container"]}>
          <div className={style["slider-label"]}>
            <span>가격</span>
            <label>
              <input type="checkbox" />
              관리비 포함
            </label>
          </div>
          <div className={style["slider-label"]}>
            <span>보증금(전세금)</span>
            <span>무제한</span>
          </div>
          <ReactSlider
            className={style.slider}
            thumbClassName="thumb"
            trackClassName="track"
            defaultValue={[0, 15000]}
            min={0}
            max={15000}
            step={100}
            onChange={(value) => setDeposit(value)}
          />
          <div className={style["slider-label"]}>
            <span>최소</span>
            <span>{deposit[1]}만원</span>
          </div>
          <div className={style["slider-label"]}>
            <span>월세</span>
            <span>무제한</span>
          </div>
          <ReactSlider
            className={style.slider}
            thumbClassName="thumb"
            trackClassName="track"
            defaultValue={[0, 600]}
            min={0}
            max={600}
            step={10}
            onChange={(value) => setRent(value)}
          />
          <div className={style["slider-label"]}>
            <span>최소</span>
            <span>{rent[1]}만원</span>
          </div>
        </div>
      </div>
      <Link to="/address/cost/facility">이동</Link>
    </>
  );
};

export default GetCost