import {recoilPersist} from "recoil-persist";
import {atom} from "recoil";

const {persistAtom} = recoilPersist({
  key: 'address',
  storage: localStorage
});

const addressAtom = atom({
  key: 'addressAtom',
  default: {},
  effects_UNSTABLE: [persistAtom]
});

export {addressAtom}