// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';

// Componentes principales
import LoginComponent from '../components/LoginComponent.vue';
import ParametrizacionComponent from '../components/ParametrizacionComponent.vue';
import GestionEliminacionLeadsComponent from '../components/GestionEliminacionLeadsComponent.vue';
import LeadExpertComponent from '../components/LeadExpertComponent.vue';
import EstadoVendedores from '../components/EstadoVendedores.vue';
import EstadoVendedoresSupervisor from '../components/EstadoVendedoresSupervisor.vue';
import EstadoLeadsExpertComponent from '../components/EstadoLeadsExpertComponent.vue';
import LogConsultasRNE from '../components/LogConsultasRNE.vue';
import GerenteLeadsComponent from '../components/GerenteLeadsComponent.vue';
import LeadsVendedorComponent from '../components/LeadsVendedorComponent.vue';
import LogsAuditoriaLeads from '../components/LogsAuditoriaLeads.vue';
import ParametrizacionGeneralComponent from '../components/ParametrizacionGeneralComponent.vue';
import TestDriveForm from '../components/TestDriveForm.vue';

// Dashboards
import AdminDashboard from '../components/AdminDashboard.vue';
import GerenteDashboard from '../components/GerenteDashboard.vue';
import VendedorDashboard from '../components/VendedorDashboard.vue';

const routes = [
  { path: '/', name: 'Login', component: LoginComponent },

  // 🔹 RUTA PÚBLICA para formulario de Test Drive
  { path: '/test-drive-form', name: 'PublicTestDrive', component: TestDriveForm },

  // Admin
  {
    path: '/dashboard/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    children: [
      { path: '', redirect: { name: 'AdminLeads' } },
      { path: 'leads', name: 'AdminLeads', component: () => import('../components/LeadsComponent.vue') },
      { path: 'eliminacion-leads', name: 'AdminEliminacionLeads', component: GestionEliminacionLeadsComponent },
      { path: 'reportes', name: 'AdminReportes', component: () => import('../components/ReportesComponent.vue') },
      { path: 'parametrizacion', name: 'AdminParametrizacion', component: ParametrizacionComponent },
      { path: 'estado-vendedores', name: 'AdminEstadoVendedores', component: EstadoVendedores },
      { path: 'log-consultas-rne', name: 'AdminLogRNE', component: LogConsultasRNE },
      { path: 'logs-auditoria', name: 'AdminLogsAuditoria', component: LogsAuditoriaLeads },
      { path: 'parametrizacion-general', name: 'AdminParametrizacionGeneral', component: ParametrizacionGeneralComponent },
      { path: 'usuarios', name: 'AdminUsuarios', component: () => import('../components/AdminUsuariosComponent.vue') },

    ],
  },

  // Gerente
  {
    path: '/dashboard/gerente',
    name: 'GerenteDashboard',
    component: GerenteDashboard,
    children: [
      { path: '', redirect: { name: 'GerenteLeads' } },
      { path: 'leads', name: 'GerenteLeads', component: GerenteLeadsComponent },
      { path: 'estado-vendedores-supervisor', name: 'GerenteEstadoVendedores', component: EstadoVendedoresSupervisor },
      { path: 'leads-expert', name: 'GerenteLeadsExpert', component: EstadoLeadsExpertComponent },
      { path: 'reportes', name: 'GerenteReportes', component: () => import('../components/GerenteReportes.vue') }
    ],
  },

  // Vendedor
  {
    path: '/dashboard/vendedor',
    name: 'VendedorDashboard',
    component: VendedorDashboard,
    children: [
      { path: '', redirect: { name: 'VendedorLeads' } },
      { path: 'leads', name: 'VendedorLeads', component: LeadsVendedorComponent },
      // 👇 TestDriveForm ya NO va aquí, porque será público
    ],
  },

  // Expert (página independiente)
  { path: '/expert-dashboard', name: 'ExpertDashboard', component: LeadExpertComponent },

  // Catch-all → login
  { path: '/:pathMatch(.*)*', redirect: { name: 'Login' } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
