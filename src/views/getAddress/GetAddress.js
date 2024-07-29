import style from "./GetAddress.module.css"
import {useNavigate} from "react-router-dom";
import {useRecoilValue, useSetRecoilState} from "recoil";
import {addressAtom} from "../../stores/addressAtom";
import {useState} from "react";

const GetAddress = () => {
  const setAddress = useSetRecoilState(addressAtom);
  const address = useRecoilValue(addressAtom);
  const [inputValue, setValue] = useState("");
  const navigate = useNavigate();

  const clickEvent = (e) => {
    e.preventDefault();
    setAddress({...address, address: inputValue});
    console.log(address);
    navigate("/address/cost");
  }

  return (
    <>
      <h1 className={style.title}>살고 싶은 동네를 입력해 주세요.</h1>
      <form className={style["form-container"]} action="">
        <div className={style["search-bar"]}>
          <input type="text" placeholder="군자역, 서초동..." onChange={e=> setValue(e.target.value)}/>
          <input type="submit" onClick={e => clickEvent(e)} value="O" />
        </div>
      </form>
      <div className={style.tip}>
        <p>tip</p>
        <p>아래와 같은 조합으로 검색하시면 됩니다.</p>
        <p>oo역, oo동, oo구</p>
      </div>
    </>
  );
};

export default GetAddress