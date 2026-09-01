// src/axios.js
import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8080', // Usa variable de entorno
  withCredentials: true // Necesario para que el navegador envíe la cookie de sesión
});

// Si el backend responde 401 (sesión vencida o no autenticado), volvemos al login.
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401 && window.location.pathname !== '/') {
      localStorage.clear();
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default instance;