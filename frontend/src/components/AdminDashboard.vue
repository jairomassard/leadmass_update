<template>
  <!-- Usamos el layout genérico y pasamos la lista de enlaces -->
  <DashboardLayout :links="navLinks" />
</template>

<script>
import DashboardLayout from './DashboardLayout.vue';

export default {
  name: 'AdminDashboard',
  components: { DashboardLayout },
  data() {
    return {
      navLinks: [
        { to: '/dashboard/admin/leads', text: 'Leads', icon: 'fa fa-address-card' },
        { to: '/dashboard/admin/eliminacion-leads', text: 'Gestión y Eliminación', icon: 'fa fa-trash' },
        { to: '/dashboard/admin/reportes', text: 'Reportes', icon: 'fa fa-chart-bar' },
        { to: '/dashboard/admin/parametrizacion', text: 'Parametrización', icon: 'fa fa-cogs' },
        { to: '/dashboard/admin/estado-vendedores', text: 'Estado Vendedores', icon: 'fa fa-users' },
        { to: '/dashboard/admin/log-consultas-rne', text: 'Consultas RNE', icon: 'fa fa-history' },
        { to: '/dashboard/admin/logs-auditoria', text: 'Logs Auditoría', icon: 'fa fa-book' },
        { to: '/dashboard/admin/parametrizacion-general', text: 'Parametrización General', icon: 'fa fa-sliders-h' },
        { to: '/dashboard/admin/usuarios', text: 'Usuarios', icon: 'fa fa-user-cog' },
      ],
    };
  },
};
</script>

<!-- El CSS adicional para este dashboard puede ir aquí si se necesita -->