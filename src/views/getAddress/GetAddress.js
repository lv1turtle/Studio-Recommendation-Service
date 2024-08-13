import style from "./GetAddress.module.css"
import {useNavigate} from "react-router-dom";
import {useRecoilValue, useSetRecoilState} from "recoil";
import {addressAtom} from "../../stores/addressAtom";
import {useForm} from "react-hook-form";
import Header from "../../common/header/Header";
import Footer from "../../common/footer/Footer";

const GetAddress = () => {
  const setAddress = useSetRecoilState(addressAtom);
  const address = useRecoilValue(addressAtom);
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  const onSubmit = (data) => {
    setAddress({...address, address: data.address});
    navigate("/address/cost");
  }

  return (
    <>
      <div className={style["container"]}>
        <Header />
        <main className={style.main}>
          <div className={style.card}>
            <h1 className={style.title}>살고 싶은 동네를 입력해 주세요.</h1>
            <form className={style["form-container"]} onSubmit={handleSubmit(onSubmit)}>
              <div className={style["search-bar"]}>
                <input type="text" {...register("address", {required: true})} />
                {errors.address && <span>동네를 입력해 주세요.</span>}
                <input type="submit" value="O"/>
              </div>
            </form>
            <div className={style.tip}>
              <p>tip</p>
              <p>아래와 같은 조합으로 검색하시면 됩니다.</p>
              <p>군자동, 서초구, 잠실</p>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </>
  );
};

export default GetAddress