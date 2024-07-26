import style from "./MainPage.module.css"
import {Link} from "react-router-dom";

const MainPage = () => {
  return (
    <>
      <h1 className={style.title}>다바방</h1>
      <Link to="/address">이동</Link>
    </>
  )
}

export default MainPage