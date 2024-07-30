import style from "./MainPage.module.css"
import { Link } from "react-router-dom";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";

const MainPage = () => {
  return (
    <div className={style["container"]}>
      <Header />
      <main className={style["main"]}>
        <div className={style["intro"]}>
          <h1>원하는 매물을 쉽게 찾으세요!</h1>
          <p>간단한 정보 입력으로 맞춤형 매물을 추천받으세요.</p>
          <Link to="/address" className={style["start-button"]}>시작하기</Link>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default MainPage;