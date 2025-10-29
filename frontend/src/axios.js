// src/axios.js
import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8080' // Usa variable de entorno
});

export default instance;