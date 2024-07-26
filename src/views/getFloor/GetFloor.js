import style from "./GetFloor.module.css"
import { Link } from "react-router-dom";
const GetFloor = () => {
  return (
    <>
      <h1 className={style.title}>옥탑, 반지하 입력 페이지 입니다.</h1>
      <Link to="/info">이동</Link>
    </>
  )
}

export default GetFloor