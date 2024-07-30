import Send from "./Send.js";

export const getFilter = (params) => {
  return Send({
    method: "get",
    url: `/getFilter`,
    params: params,
  });
};
