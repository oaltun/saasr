import AppRoutes from "./AppRoutes";
import { baseUrl } from "./core/config/urls";
import usePageTracking from "./core/hooks/usePageTracking";

// axios settings
import Axios from "axios";
import { getToken } from "./auth/utils/auth";

Axios.defaults.baseURL = baseUrl;

Axios.interceptors.request.use(
  config => {
    config.headers = config.headers ?? {};
    config.headers['Authorization'] = `Bearer ${getToken()}`;
    return config;
  },
  error => {
    console.log("Axios.interceptors.request.use: We got an error:")
    console.log(error)
    return Promise.reject(error);
  }
);

Axios.interceptors.response.use(function (response) {
  // satus code 2xx
  return response;
}, function (error) {
  // Any status codes that falls outside the range of 2xx cause this function to trigger
  // Do something with response error
  console.log("Axios.interceptors.response.use: We got an error:")
  console.log(error)
  const obj = Promise.reject(error);
  return obj;
});



function App() {
  usePageTracking();


  return (<AppRoutes />);
}

export default App;
