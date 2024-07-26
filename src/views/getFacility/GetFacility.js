import style from "./GetFacility.module.css"
import { Link } from "react-router-dom";

const GetFacility = () => {
  return (
    <>
          <h1 className={style.title}>편의시설 입력 페이지 입니다.</h1>
          <Link to="/address/cost/facility/floor">이동</Link>
    </>
  )
}

export default GetFacility