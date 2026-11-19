import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://auto-connect-htzc.onrender.com/api",
});

// Har request mein token lagao
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default API;