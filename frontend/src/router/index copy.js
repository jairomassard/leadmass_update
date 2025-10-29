import { createRouter, createWebHistory } from 'vue-router';
import LoginComponent from '../components/LoginComponent.vue';
import ParametrizacionComponent from '../components/ParametrizacionComponent.vue';
import LeadsVendedorComponent from '../components/LeadsVendedorComponent.vue';
import SupervisorLeadsComponent from '../components/SupervisorLeadsComponent.vue';
import GestionEliminacionLeadsComponent from '../components/GestionEliminacionLeadsComponent.vue';
import LeadExpertComponent from '../components/LeadExpertComponent.vue';
import EstadoVendedores from '../components/EstadoVendedores.vue';
import EstadoVendedoresSupervisor from '../components/EstadoVendedoresSupervisor.vue';
import EstadoLeadsExpertComponent from '../components/EstadoLeadsExpertComponent.vue';
import LogConsultasRNE from '../components/LogConsultasRNE.vue';
import GerenteLeadsComponent from '../components/GerenteLeadsComponent.vue';
import LogsAuditoriaLeads from '../components/LogsAuditoriaLeads.vue';
import ParametrizacionGeneralComponent from '../components/ParametrizacionGeneralComponent.vue';
import TestDriveForm from '../components/TestDriveForm.vue';

// Nuevos layouts para dashboards de roles
import AdminDashboard from '../components/AdminDashboard.vue';
import GerenteDashboard from '../components/GerenteDashboard.vue';
import VendedorDashboard from '../components/VendedorDashboard.vue';


const routes = [
  { path: '/', component: LoginComponent },
  // Tableros unificados por rol
  {
    path: '/dashboard/admin',
    component: AdminDashboard,
    children: [
      { path: '', redirect: 'leads' },
      { path: 'leads', component: () => import('../components/LeadsComponent.vue') },
      { path: 'eliminacion-leads', component: GestionEliminacionLeadsComponent },
      { path: 'reportes', component: () => import('../components/ReportesComponent.vue') },
      { path: 'parametrizacion', component: ParametrizacionComponent },
      { path: 'estado-vendedores', component: EstadoVendedores },
      { path: 'log-consultas-rne', component: LogConsultasRNE },
      { path: 'logs-auditoria', component: LogsAuditoriaLeads },
      { path: 'parametrizacion-general', component: ParametrizacionGeneralComponent },
      { path: 'usuarios', component: () => import('../components/AdminUsuariosComponent.vue') },
    ],
  },
  {
    path: '/dashboard/gerente',
    component: GerenteDashboard,
    children: [
      { path: '', redirect: 'leads' },
      { path: 'leads', component: GerenteLeadsComponent },
      { path: 'estado-vendedores-supervisor', component: EstadoVendedoresSupervisor },
      { path: 'leads-expert', component: EstadoLeadsExpertComponent },
      { path: 'reportes', component: () => import('../components/ReportesComponent.vue') },
    ],
  },
  {
    path: '/dashboard/vendedor',
    component: VendedorDashboard,
    children: [
      { path: '', redirect: 'leads' },
      { path: 'leads', component: LeadsVendedorComponent },
      { path: 'test-drive-form', component: TestDriveForm },
    ],
  },
  // Ruta individual para expertos: permanece como página independiente
  { path: '/expert-dashboard', component: LeadExpertComponent },
  // Rutas heredadas para compatibilidad (se pueden eliminar en el futuro)
  { path: '/leads', component: () => import('../components/LeadsComponent.vue') },
  //{ path: '/leads-vendedor', component: LeadsVendedorComponent },
  { path: '/leads-supervisor', component: SupervisorLeadsComponent },
  { path: '/admin-usuarios', component: () => import('../components/AdminUsuariosComponent.vue') },
  { path: '/reportes', component: () => import('../components/ReportesComponent.vue') },
  { path: '/parametrizacion', component: ParametrizacionComponent },
  { path: '/eliminacion-leads', component: GestionEliminacionLeadsComponent },
  { path: '/estado-vendedores', component: EstadoVendedores },
  { path: '/estado-vendedores-supervisor', component: EstadoVendedoresSupervisor },
  { path: '/leads-expert', component: EstadoLeadsExpertComponent },
  { path: '/log-consultas-rne', component: LogConsultasRNE },
  //{ path: '/leads-gerente', component: GerenteLeadsComponent },
  { path: '/logs-auditoria', component: LogsAuditoriaLeads },
  { path: '/parametrizacion-general', component: ParametrizacionGeneralComponent },
  { path: '/test-drive-form', component: TestDriveForm },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;








