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
      <h3 class="text-center mb-4"></h3>

      <form @submit.prevent="login">
        <!-- Usuario -->
        <div class="mb-3">
          <input
            type="text"
            v-model="usuario"
            class="form-control"
            placeholder="Usuario"
            required
          />
        </div>

        <!-- Contraseña con toggle -->
        <div class="mb-3 position-relative">
          <input
            :type="mostrarPassword ? 'text' : 'password'"
            v-model="password"
            class="form-control pe-5"
            placeholder="Contraseña"
            required
          />
          <span
            class="toggle-password"
            @click="mostrarPassword = !mostrarPassword"
          >
            <i :class="mostrarPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
          </span>
        </div>

        <button type="submit" class="btn btn-secondary w-100">Ingresar</button>
      </form>

      <p v-if="errorMessage" class="text-danger text-center mt-3">
        {{ errorMessage }}
      </p>

      <!-- Footer actualizado -->
      <p class="text-center mt-4 text-muted small">
        © 2025 Binaria Media Group SAS.
      </p>
    </div>
  </div>
</template>

<script>
import axios from "../axios";

export default {
  data() {
    return {
      usuario: "",
      password: "",
      errorMessage: "",
      mostrarPassword: false, // 👈 toggle para mostrar/ocultar contraseña
    };
  },
  methods: {
    async login() {
      if (!this.usuario || !this.password) {
        this.errorMessage = "Por favor, completa ambos campos.";
        return;
      }

      try {
        const response = await axios.post("/login", {
          usuario: this.usuario,
          password: this.password,
        });

        const { tipo_usuario, vendedor_id, id, nombres, apellidos, message } =
          response.data;

        this.errorMessage = "";
        alert(message);

        localStorage.setItem("tipo_usuario", tipo_usuario);
        localStorage.setItem(
          "vendedor_nombre_completo",
          `${nombres} ${apellidos}`
        );

        if (id) {
          localStorage.setItem("id_usuario", id);
        }

        if (tipo_usuario === "vendedor" && vendedor_id) {
          localStorage.setItem("vendedor_actual", vendedor_id);
          this.$router.push({ name: "VendedorLeads" });
        } else if (tipo_usuario === "supervisor") {
          localStorage.removeItem("vendedor_actual");
          this.$router.push({ name: "GerenteLeads" });
        } else if (tipo_usuario === "gerente") {
          localStorage.removeItem("vendedor_actual");
          this.$router.push({ name: "GerenteLeads" });
        } else if (tipo_usuario === "administrador") {
          localStorage.removeItem("vendedor_actual");
          this.$router.push({ name: "AdminLeads" });
        } else if (tipo_usuario === "expert") {
          this.$router.push({ name: "ExpertDashboard" });
        } else {
          this.errorMessage =
            "Tipo de usuario no reconocido. Por favor, contacta al administrador.";
        }
      } catch (error) {
        console.error("Error en el inicio de sesión:", error);
        this.errorMessage =
          "Credenciales incorrectas. Por favor, intenta de nuevo.";
      }
    },
  },
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

.toggle-password {
  position: absolute;
  top: 8px;
  right: 12px;
  cursor: pointer;
  font-size: 1.2em;
  color: #666;
}
</style>
