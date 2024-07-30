import style from "./GetCost.module.css";
import {Link, useNavigate} from "react-router-dom";
import ReactSlider from "react-slider";
import React, { useState } from "react";
import {useRecoilValue, useSetRecoilState} from "recoil";
import {addressAtom} from "../../stores/addressAtom";
import Checkbox from "../../common/checkbox/Checkbox";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";

const GetCost = () => {
  const setAddress = useSetRecoilState(addressAtom);
  const address = useRecoilValue(addressAtom);
  const [minDeposit, setMinDeposit] = useState(0);
  const [maxDeposit, setMaxDeposit] = useState(20000);
  const [minRent, setMinRent] = useState(0);
  const [maxRent, setMaxRent] = useState(150);
  const [checkFee, setCheckFee] = useState(false);
  const navigate = useNavigate();

  const changeDeposit = (value) => {
    setMinDeposit(value[0]);
    setMaxDeposit(value[1]);
  }
  const changeRent = (value) => {
    setMinRent(value[0]);
    setMaxRent(value[1]);
  }
  const clickEvent = () => {
    setAddress({
      ...address,
      min_deposit: minDeposit,
      max_deposit: maxDeposit,
      min_rent: minRent,
      max_rent: maxRent,
      include_maintenance_fee : checkFee,
    });
    navigate("/address/cost/facility");
  }

  return (
    <>
      <div className={style["container"]}>
        <Header />
        <main className={style["main"]}>
          <div className={style["intro"]}>
            <h1>원하는 보증금, 월세 범위를 설정해주세요!</h1>
            <div style={{ textAlign: "left", margin: "10px" }}>단위: 만원</div>
            <div className={style["slider-container"]}>
              <div className={style["slider-label"]}>
                <span className={style["cost-text"]}>보증금</span>
                <div className={style["slider-label"]}>
                  <div className={style["slider"]}>
                    <ReactSlider
                      thumbClassName={style["thumb"]}
                      trackClassName={style["track"]}
                      defaultValue={[0, 20000]}
                      min={0}
                      max={20000}
                      step={100}
                      renderThumb={(props, state) => <div {...props}>{state.valueNow}</div>}
                      onChange={changeDeposit}
                    />
                  </div>
                  <div className={style["value-container"]}>
                    <span>최소</span>
                    <span>최대</span>
                  </div>
                </div>
              </div>
              <div className={style["slider-label"]}>
                <div className={style["rent-header"]}>
                  <span className={style["cost-text"]}>월세</span>
                  <Checkbox checked={checkFee} onChange={setCheckFee}>
                    관리비 포함
                  </Checkbox>
                </div>
                <div className={style["slider"]}>
                  <ReactSlider
                    thumbClassName={style["thumb"]}
                    trackClassName={style["track"]}
                    defaultValue={[0, 150]}
                    min={0}
                    max={150}
                    step={5}
                    renderThumb={(props, state) => <div {...props}>{state.valueNow}</div>}
                    onChange={changeRent}
                  />
                </div>
                <div className={style["value-container"]}>
                  <span>최소</span>
                  <span>최대</span>
                </div>
              </div>
            </div>
            <button className={style["move-button"]} onClick={clickEvent}>이동</button>
          </div>
        </main>
        <Footer />
      </div>
    </>
  );
};

export default GetCost