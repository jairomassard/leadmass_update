import { createApp } from 'vue';
import App from './App.vue';  // Importa el componente principal App
import router from './router';  // Importa el router
import "bootstrap-icons/font/bootstrap-icons.css";

const app = createApp(App);  // Crea la aplicación con App.vue
app.use(router);  // Usa el router
app.mount('#app');  // Monta la app


