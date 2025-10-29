<template>
  <div>
    <button @click="logout">Salir del Programa</button>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  methods: {
    goToMenu() {
      // Obtenemos el tipo de usuario almacenado en localStorage
      const tipoUsuario = localStorage.getItem('tipo_usuario');
      
      // Redirigir a la página correcta según el tipo de usuario
      if (tipoUsuario === 'administrador') {
        this.$router.push('/menu');  // Redirigir al menú principal del administrador
      } else if (tipoUsuario === 'supervisor') {
        this.$router.push('/menu-supervisor');  // Redirigir al menú del supervisor
      } else if (tipoUsuario === 'vendedor') {
        this.$router.push('/menu-vendedor');  // Redirigir al menú del vendedor
      }
    },
    logout() {
      const tipoUsuario = localStorage.getItem('tipo_usuario');

      if (tipoUsuario === 'vendedor') {
        const vendedorId = localStorage.getItem('vendedor_actual');
        
        axios.post('/update-vendedor-estado', {
          vendedor_id: vendedorId,
          estado: false
        })
        .then(() => {
          console.log("Vendedor marcado como fuera de línea al salir.");
        })
        .catch(error => {
          console.error("Error al marcar al vendedor como fuera de línea:", error);
        });
      }

      localStorage.removeItem('tipo_usuario');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
button {
  margin: 10px;
  padding: 10px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background-color: #2980b9;
}
</style>
