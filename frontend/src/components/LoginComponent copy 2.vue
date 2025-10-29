<template>
  <div id="login">
    <!-- Imagen de encabezado -->
    <div class="header-image">
      <img src="/images/cabezote.jpg" alt="Cabezote" class="img-fluid w-100" />
    </div>

    <!-- Contenedor de inicio de sesión -->
    <div class="login-container">
      <h1 class="text-center">LeadsMass Retail</h1>
      <h3 class="text-center">Sistema de Manejo de Leads</h3>
      <h3 class="text-center mb-4"> </h3>

      <form @submit.prevent="login">
        <div class="mb-3">
          <input
            type="text"
            v-model="usuario"
            class="form-control"
            placeholder="Usuario"
            required
          />
        </div>
        <div class="mb-3">
          <input
            type="password"
            v-model="password"
            class="form-control"
            placeholder="Contraseña"
            required
          />
        </div>
        <button type="submit" class="btn btn-secondary w-100">Ingresar</button>
      </form>

      <p v-if="errorMessage" class="text-danger text-center mt-3">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import axios from '../axios'; // Importa desde el archivo configurado

export default {
  data() {
    return {
      usuario: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
  async login() {
    if (!this.usuario || !this.password) {
      this.errorMessage = "Por favor, completa ambos campos.";
      return;
    }

    try {
      const response = await axios.post('/login', {
        usuario: this.usuario,
        password: this.password
      });

      //console.log(response.data); // Verifica aquí si `tipo_usuario` muestra "expert"
      
      const { tipo_usuario, vendedor_id, id, nombres, apellidos, message } = response.data;

      this.errorMessage = '';
      alert(message);

      // Guardar el tipo de usuario y el nombre completo en localStorage
      localStorage.setItem('tipo_usuario', tipo_usuario);
      localStorage.setItem('vendedor_nombre_completo', `${nombres} ${apellidos}`);

      // Guardar el id del usuario en localStorage
      // ✅ Guardar el ID del usuario en localStorage correctamente
      if (id) {
        localStorage.setItem('id_usuario', id);
      } else {
        console.error("❌ Error: No se recibió un ID de usuario del backend.");
      }

      // Redirecciones según el tipo de usuario
      // Redirecciones según el tipo de usuario (usar nombres de rutas hijas)
      if (tipo_usuario === 'vendedor' && vendedor_id) {
        localStorage.setItem('vendedor_actual', vendedor_id);
        this.$router.push({ name: 'VendedorLeads' });   // 👈 directo a la vista de leads del vendedor
      } else if (tipo_usuario === 'supervisor') {
        localStorage.removeItem('vendedor_actual');
        this.$router.push({ name: 'GerenteLeads' });     // 👈 comparten vista con gerente
      } else if (tipo_usuario === 'gerente') {
        localStorage.removeItem('vendedor_actual');
        this.$router.push({ name: 'GerenteLeads' });     // 👈 directo a leads gerente
      } else if (tipo_usuario === 'administrador') {
        localStorage.removeItem('vendedor_actual');
        this.$router.push({ name: 'AdminLeads' });       // 👈 directo a leads de admin
      } else if (tipo_usuario === 'expert') {
        this.$router.push({ name: 'ExpertDashboard' });
      } else {
        this.errorMessage = "Tipo de usuario no reconocido. Por favor, contacta al administrador.";
      }
      } catch (error) {
        console.error("Error en el inicio de sesión:", error);
        this.errorMessage = "Credenciales incorrectas. Por favor, intenta de nuevo.";
      }
    }

  }
};
</script>

<style scoped>
.header-image img {
  width: 100%;
  height: auto;
}

.login-container {
  max-width: 400px;
  margin: 20px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 24px;
  margin-bottom: 10px;
}

h3 {
  font-size: 20px;
  margin-bottom: 20px;
}

.error-message {
  color: red;
  margin-top: 10px;
}
</style>
