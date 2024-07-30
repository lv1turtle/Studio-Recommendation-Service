import axios from 'axios'
axios.defaults.withCredentials = true;
const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    // 'Access-Control-Allow-Origin': '*'
},
})

instance.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

instance.interceptors.response.use(
  (response) => {
    return response
  },

  (error) => {
    return Promise.reject(error)
  },
)

export default instance
