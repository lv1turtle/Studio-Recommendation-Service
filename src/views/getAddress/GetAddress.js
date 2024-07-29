import style from "./GetAddress.module.css"
import {postRegister} from "../../apis/Users";
import { Link } from "react-router-dom";

const getAddress = () => {
  const onSubmit = (data, event) => {
    event.preventDefault();
    postRegister(data)
      .then((r) => {
        alert("회원 가입이 되었습니다");
      })
      .catch((r) => {
        alert("아이디나 비밀번호를 확인해 주세요.");
        console.log("Register Post Error : " + r);
      });
  };

  return (
    <>
      <h1 className={style.title}>살고 싶은 동네를 입력해 주세요.</h1>
      <form className={style["form-container"]} onSubmit={(e) => onSubmit("name", e)}>
        <div className={style["search-bar"]}>
          <input type="text" placeholder="군자역, 서초동..." />
          <input type="submit" value="O" />
        </div>
      </form>
      <div className={style.tip}>
        <p>tip</p>
        <p>아래와 같은 조합으로 검색하시면 됩니다.</p>
        <p>oo역, oo동, oo구</p>
      </div>
      <Link to="/address/cost">이동</Link>
    </>
  );
};

export default getAddress