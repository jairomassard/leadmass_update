<template>
  <div>
    <button @click="goToMenu">Menú Principal</button>
    <button @click="logout">Salir del Programa</button>
  </div>
</template>

<script>
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
      // Limpiar cualquier información de sesión si es necesario
      localStorage.removeItem('tipo_usuario');  // Limpiar el tipo de usuario del almacenamiento local
      this.$router.push('/');  // Redirigir a la página de login
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
