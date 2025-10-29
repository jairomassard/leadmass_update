<template>
  <DashboardLayout :links="navLinks" />
</template>

<script>
import DashboardLayout from './DashboardLayout.vue';

export default {
  name: 'VendedorDashboard',
  components: { DashboardLayout },
  data() {
    return {
      navLinks: [
        { to: '/dashboard/vendedor/leads', text: 'Mis Leads', icon: 'fa fa-address-card' },
        //{ to: '/dashboard/vendedor/test-drive-form', text: 'Registrar Test Drive', icon: 'fa fa-car' },
      ],
    };
  },
};
</script>