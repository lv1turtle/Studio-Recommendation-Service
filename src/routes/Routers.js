import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import MainPage from "../views/main/MainPage";
import GetAddress from "../views/getAddress/GetAddress";
import GetCost from "../views/getCost/GetCost";
import GetFacility from "../views/getFacility/GetFacility";
import GetFloor from "../views/getFloor/GetFloor";
import ViewInfo from "../views/viewInfo/ViewInfo";

const Routers = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<MainPage />}></Route>
      <Route path="/address" element={<GetAddress />}></Route>
      <Route path="/address/cost" element={<GetCost />}></Route>
      <Route path="/address/cost/facility" element={<GetFacility />}></Route>
      <Route path="/address/cost/facility/floor" element={<GetFloor />}></Route>
      <Route path="/info" element={<ViewInfo />}></Route>
    </Routes>
  </BrowserRouter>
);

export default Routers;
