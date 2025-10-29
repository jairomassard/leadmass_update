<template>
  <div class="d-flex">
    <!-- Sidebar -->
    <aside class="bg-dark text-white d-flex flex-column" style="min-width: 220px; min-height: 100vh;">
      <div class="p-3 border-bottom">
        <h4 class="mb-0">LeadMass</h4>
      </div>
      <nav class="nav flex-column p-2 flex-grow-1">
        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="nav-link text-white"
          active-class="active"
        >
          <i :class="link.icon" class="me-2"></i>
          <span>{{ link.text }}</span>
        </router-link>
      </nav>
      <div class="p-2">
        <button class="btn btn-danger w-100" @click="logout">Salir</button>
      </div>
    </aside>
    <!-- Content -->
    <main class="flex-grow-1 p-4" style="min-height: 100vh; background-color: #f8f9fa;">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'DashboardLayout',
  props: {
    links: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    logout() {
      // Limpiar almacenamiento y redirigir al login
      localStorage.clear();
      this.$router.push('/');
    },
  },
};
</script>

<style scoped>
.nav-link.active {
  background-color: #495057 !important;
}
</style>