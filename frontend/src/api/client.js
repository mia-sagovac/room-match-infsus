import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api",
});

// JWT iz localstoragea
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// auto log outtan na 401 Unauthorized error, ukloni token i korisnika iz localstoragea i preusmjeri na login stranicu
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("korisnik");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;
