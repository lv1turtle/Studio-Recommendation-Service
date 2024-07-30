import style from "./ViewInfo.module.css"
import React, {useEffect} from "react";
import {getFilter} from "../../apis/Filter";
import {useRecoilValue} from "recoil";
import {addressAtom} from "../../stores/addressAtom";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";

const ViewInfo = () => {
  const address = useRecoilValue(addressAtom);
  useEffect(() => {
    getFilter(address).then((r)=> {
      console.log(r);
    }).catch((r) => {
      console.error(r);
    });
  }, []);

  return (
    <>
      <div className={style.container}>
        <Header />
        <main className={style.main}>
          <div className={style.card}>
            <h1 className={style.title}>매물 정보 제공 페이지 입니다.</h1>
          </div>
        </main>
        <Footer />
      </div>
    </>
  )
}

export default ViewInfo