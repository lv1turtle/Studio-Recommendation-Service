// src/Map.js
import {useEffect, useRef} from "react";

const NaverMap = ({latitude, longitude}) => {
  const mapRef = useRef(null);
  const lat = latitude// 위도 숫자로 넣어주기
  const lng = longitude// 경도 숫자로 넣어주기

  useEffect(() => {
    const { naver } = window;
    if (mapRef.current && naver) {
      const location = new naver.maps.LatLng(lat, lng);
      const map = new naver.maps.Map(mapRef.current, {
        center: location,
        zoom: 17, // 지도 확대 정도
      });
      new naver.maps.Marker({
        position: location,
        map,
      });
    }
  }, [latitude, longitude]);

  return (
    <div ref={mapRef} style={{ width: "500px", height: "500px" }}></div>
  );
}
export default NaverMap;