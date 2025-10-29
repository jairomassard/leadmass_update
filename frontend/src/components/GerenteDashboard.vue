<template>
  <DashboardLayout :links="navLinks" />
</template>

<script>
import DashboardLayout from './DashboardLayout.vue';

export default {
  name: 'GerenteDashboard',
  components: { DashboardLayout },
  data() {
    return {
      navLinks: [
        { to: '/dashboard/gerente/leads', text: 'Leads', icon: 'fa fa-address-card' },
        { to: '/dashboard/gerente/estado-vendedores-supervisor', text: 'Estado Vendedores', icon: 'fa fa-users' },
        { to: '/dashboard/gerente/leads-expert', text: 'Leads Expertos', icon: 'fa fa-user-tie' },
        { to: '/dashboard/gerente/reportes', text: 'Reportes', icon: 'fa fa-chart-bar' },
      ],
    };
  },
};
</script>