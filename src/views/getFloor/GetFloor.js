import React, {useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import style from "./GetFloor.module.css";
import Checkbox from "../../common/checkbox/Checkbox";
import CheckboxGroup from "../../common/checkbox/CheckboxGroup";
import {useRecoilValue, useSetRecoilState} from "recoil";
import {addressAtom} from "../../stores/addressAtom";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";

const GetFloor = () => {
  const [floor, setFloor] = useState([]);
  const setAddress = useSetRecoilState(addressAtom);
  const address = useRecoilValue(addressAtom);
  const navigate = useNavigate();

  const clickEvent = () => {
    setAddress({
      ...address,
      floor_options : floor,
    });
    console.log(address)
    navigate("/info");
  }
  return (
    <>
      <div className={style.container}>
        <Header />
        <main className={style.main}>
          <div className={style.card}>
            <h1 className={style.title}>옥탑, 반지하 입력 페이지 입니다.</h1>
            <section className={style.section}>
              <p className={style.question}>옥탑방이나 반지하 정보도 받으시겠어요?</p>
              <div className={style.options}>
                <CheckboxGroup
                  label={"옥탑, 반지하 정보"}
                  values={floor}
                  onChange={setFloor}
                >
                  <Checkbox value="옥탑">옥탑방</Checkbox>
                  <Checkbox value="반지하">반지하</Checkbox>
                </CheckboxGroup>
              </div>
            </section>
            <button onClick={clickEvent} className={style["move-button"]}>이동</button>
          </div>
        </main>
        <Footer />
      </div>
    </>
  );
};

export default GetFloor;
