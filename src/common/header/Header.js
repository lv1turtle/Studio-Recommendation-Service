import style from "./Header.module.css";
import {Link} from "react-router-dom";

const Header = () => {
  return (
    <>
      <header className={style["header"]}>
        <div className={style["logo"]}><Link to="/">바로방</Link></div>
        <nav className={style["nav"]}>
          <Link to="/faq">FAQ</Link>
          <Link to="/contact">문의하기</Link>
        </nav>
      </header>
    </>
  )
}

export default Header