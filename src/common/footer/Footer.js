import style from "./Footer.module.css";
import {Link} from "react-router-dom";

const Footer = () => {
  return (
    <>
      <footer className={style["footer"]}>
        <p>© 2024 바로방. All rights reserved.</p>
        <div className={style["footer-link"]}>
          <Link to="/terms">이용 약관</Link>
          <Link to="/privacy">개인정보처리방침</Link>
          <Link to="/contact">연락처</Link>
        </div>
      </footer>
    </>
  )
}

export default Footer