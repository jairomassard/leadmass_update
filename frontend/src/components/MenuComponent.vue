<template>
  <div class="container mt-5">
    <!-- Contenedor centralizado -->
    <div class="text-center">
      <!-- Título del menú principal -->
      <h1 class="mb-4">LeadMass</h1>
      <h2 class="mb-4">Sistema de Manejo de Leads</h2>
      <h3 class="mb-4">Menú Principal</h3>

      <!-- Opciones de navegación -->
      <div class="d-grid gap-3 col-6 mx-auto">
        
        
        <!-- Mostrar solo si el usuario es administrador -->
        <router-link to="/admin-usuarios" class="btn btn-secondary btn-lg">Administración de Usuarios</router-link>
        
        <router-link to="/leads" class="btn btn-secondary btn-lg">Cargue y Gestión de Leads</router-link>

        <!-- Nueva opción de eliminación de leads -->
        <router-link to="/eliminacion-leads" class="btn btn-secondary btn-lg">Gestión y Eliminación de Leads</router-link>

        <router-link to="/reportes" class="btn btn-secondary btn-lg">Reportes de Leads</router-link>
        
        <router-link to="/parametrizacion" class="btn btn-secondary btn-lg">Parametrización de Concesionarios</router-link>
        
        <router-link to="/estado-vendedores" class="btn btn-secondary btn-lg">Verificar Conexión Vendedores</router-link>

        <router-link to="/log-consultas-rne" class="btn btn-secondary btn-lg">Registro Consultas Realizadas al RNE</router-link>

        <router-link to="/logs-auditoria" class="btn btn-secondary btn-lg">Logs de Auditoría</router-link>

        <router-link to="/parametrizacion-general" class="btn btn-secondary btn-lg">Parametrización General</router-link>

        <!-- Botón de cerrar sesión -->
        <button @click="logout" class="btn btn-danger btn-lg mt-4">Salir del Programa</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      esAdministrador: false
    };
  },
  created() {
    // Verificar si el usuario es administrador
    axios.get('/user-info')
      .then(response => {
        this.esAdministrador = response.data.es_administrador;
      })
      .catch(error => {
        console.error("Error al obtener información del usuario:", error);
      });
  },
  methods: {
    logout() {
      this.$router.push('/');  // Redirigir a la página de login al salir del programa
    }
  }
};
</script>

<style scoped>
/* Ajustes específicos para el título */
h1, h3 {
  color: #333;
}
</style>

