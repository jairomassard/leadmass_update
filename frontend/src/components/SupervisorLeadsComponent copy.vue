<template>
  <div id="supervisor-leads" class="container mt-4">
    <h1 class="text-center mb-4">Supervisión y Reporte de Leads</h1>

    <!-- Botón para cargar contenido de la tabla -->
    <div class="text-center mb-4">
      <button class="btn btn-primary" @click="generarContenidoTabla">Generar Contenido Tabla</button>
    </div>

    <!-- Sección de Gráfico de Embudo y Totalizadores -->
    <div class="row mb-4">
      <!-- Gráfico de Embudo (Columna 8) -->
      <div class="col-md-8">
        <div class="chart-container d-flex justify-content-center">
          <v-chart :option="chartOptions" style="width: 100%; height: 350px;" />
        </div>
      </div>

      <!-- Totalizadores y Últimas Conexiones (Columna 4) -->
      <div class="col-md-4">
        <div class="totalizadores border p-3 rounded">
          <p>Total leads en sistema: <strong>{{ totalLeadsAsignados }}</strong></p>
          <p>Total leads Nuevos: <strong>{{ totalLeadsNuevos }}</strong></p>
          <p>Total leads asignados: <strong>{{ totalLeadsAsignadosEstado }}</strong></p>
          <p>Total leads en seguimiento: <strong>{{ totalLeadsEnSeguimiento }}</strong></p>
          <p>Total leads cerrados: <strong>{{ totalLeadsCerrados }}</strong></p>
          <p>Total leads culminados en venta: <strong>{{ totalLeadsCulminadosEnVenta }}</strong></p>
          <p>Total leads con Test Drive: <strong>{{ totalLeadsConTestDrive }}</strong></p>
          <p>Última conexión del vendedor: <strong>{{ tiempoUltimaConexion }}</strong></p>
          <p>Última puesta en línea: <strong>{{ ultimaPuestaOnline }}</strong></p>
        </div>
      </div>
    </div>

    <!-- Sección de Botones de Exportación y Acciones -->
    <div class="d-flex justify-content-center mb-4">
      <button class="btn btn-success me-2" @click="exportarReporte('pdf')">Exportar PDF</button>
      <button class="btn btn-info me-2" @click="exportarReporte('csv')">Exportar CSV</button>
      <router-link to="/estado-vendedores-supervisor" class="btn btn-secondary me-2">
        Verificar Conexión Vendedores
      </router-link>
      <router-link to="/leads-expert" class="btn btn-secondary">
        Ver Leads Capturados por Expertos
      </router-link>
    </div>

    <!-- Botón de Salir -->
    <div class="navigation-buttons text-center mb-4">
      <BotonesGlobalesSalir />
    </div>

    <!-- Filtros de Búsqueda -->

    <div class="filtros mb-4 row g-3" v-if="contenidoGenerado">
      <div class="col-md-4">
        <label class="form-label">Filtrar por vendedor:</label>
        <select class="form-select" v-model="filtroVendedor" @change="filtrarLeads">
          <option value="">Todos</option>
          <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">
            {{ vendedor.nombre }}
          </option>
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">Filtrar por estado:</label>
        <select class="form-select" v-model="filtroEstado" @change="filtrarLeads">
          <option value="">Todos</option>
          <option value="nuevo">Nuevo</option>
          <option value="asignado">Asignado</option>
          <option value="en seguimiento">En Seguimiento</option>
          <option value="cerrado">Cerrado</option>
          <option value="culmina en venta">Culmina en Venta</option>
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">Filtrar por Test Drive:</label>
        <select class="form-select" v-model="filtroTestDrive" @change="filtrarLeads">
          <option value="">Todos</option>
          <option value="Si">Si</option>
          <option value="No">No</option>
        </select>
      </div>
    </div>

    <!-- Tabla de Leads -->
    <div class="table-responsive" v-if="contenidoGenerado">
      <table class="table table-bordered table-striped">
        <thead class="table-dark">
          <tr>
            <th v-for="header in headers" :key="header" :style="{ width: columnWidths[header] }">
              <div class="resizable-header" @mousedown="startResize($event, header)">
                {{ header }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lead in leadsFiltrados" :key="lead.id">
            <td>{{ lead.nombres }}</td>
            <td>{{ lead.apellidos }}</td>
            <td>{{ lead.identificacion }}</td>
            <td>{{ lead.telefono }}</td>
            <td>{{ lead.direccion }}</td>
            <td>{{ lead.ciudad }}</td>
            <td>{{ lead.correo }}</td>
            <td>{{ lead.fecha_lead }}</td>
            <td>{{ lead.origen_lead }}</td>
            <td>{{ lead.marca_interes }}</td>
            <td>{{ lead.modelo_interesado }}</td>
            <td>{{ lead.estatus }}</td>
            <td>{{ lead.test_drive }}</td>
            <td>{{ lead.seguimientos }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script>
import axios from '../axios';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { FunnelChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import BotonesGlobalesSalir from './BotonesGlobalesSalir.vue';

use([TitleComponent, TooltipComponent, LegendComponent, FunnelChart, CanvasRenderer]);

export default {
  components: {
    VChart,
    BotonesGlobalesSalir
  },
  data() {
    return {
      headers: [
        "Nombres", "Apellidos", "Identificación", "Teléfono", "Dirección", "Ciudad", "Correo", "Fecha Lead",
        "Origen Lead", "Marca de Interés", "Modelo Interesado", "Estatus", "Test Drive", "Seguimientos"
      ],
      leads: [],
      leadsFiltrados: [],
      filtroVendedor: '',
      filtroEstado: '',
      filtroTestDrive: '',
      vendedores: [],
      totalLeadsAsignados: 0,
      totalLeadsNuevos: 0,
      totalLeadsAsignadosEstado: 0,
      totalLeadsEnSeguimiento: 0,
      totalLeadsCerrados: 0,
      totalLeadsCulminadosEnVenta: 0,
      totalLeadsConTestDrive: 0,
      tiempoUltimaConexion: '',
      ultimaPuestaOnline: '',
      contenidoGenerado: false, // Controla la visibilidad del contenido
      columnWidths: {},   // Anchos de columna inicializados
      resizingColumn: null,
      initialX: 0,
      initialWidth: 0,
      chartOptions: {
        tooltip: { trigger: 'item' },
        legend: { top: 'bottom' },
        series: [
          {
            type: 'funnel',
            left: '10%',
            width: '80%',
            sort: 'descending',
            label: {
              show: true,
              position: 'inside'
            },
            data: [
              { value: this.totalLeadsAsignados, name: 'En sistema' },
              { value: this.totalLeadsNuevos, name: 'Nuevo' },
              { value: this.totalLeadsEnSeguimiento, name: 'En seguimiento' },
              { value: this.totalLeadsCerrados, name: 'Cerrados' },
              { value: this.totalLeadsCulminadosEnVenta, name: 'Culminados en venta' },
              //{ value: this.totalLeadsAsignadosEstado, name: 'Asignados' },
            ],
          },
        ],
      },
    };
  },
  methods: {
    generarContenidoTabla() {
      this.cargarLeads();
      this.contenidoGenerado = true;
    },
    cargarLeads() {
      axios.get('/get-all-leads')
        .then((response) => {
          this.leads = response.data;
          this.filtrarLeads();
        })
        .catch(error => {
          console.error("Error al cargar leads:", error);
        });
    },
    cargarVendedores() {
      axios.get('/get-vendedores')
        .then((response) => {
          this.vendedores = response.data;
        })
        .catch(error => {
          console.error("Error al cargar vendedores:", error);
        });
    },
    filtrarLeads() {
      this.leadsFiltrados = this.leads.filter((lead) => {
        return (
          (!this.filtroVendedor || lead.asignado_a === parseInt(this.filtroVendedor)) &&
          (!this.filtroEstado || lead.estatus === this.filtroEstado) &&
          (!this.filtroTestDrive || lead.test_drive === this.filtroTestDrive)
        );
      });
      this.calcularTotalizadores();
    },
    calcularTotalizadores() {
      this.totalLeadsAsignados = this.leadsFiltrados.length;
      this.totalLeadsNuevos = this.leadsFiltrados.filter(lead => lead.estatus === 'nuevo').length;
      this.totalLeadsEnSeguimiento = this.leadsFiltrados.filter(lead => lead.estatus === 'en seguimiento').length;
      this.totalLeadsCerrados = this.leadsFiltrados.filter(lead => lead.estatus === 'cerrado').length;
      this.totalLeadsCulminadosEnVenta = this.leadsFiltrados.filter(lead => lead.estatus === 'culmina en venta').length;
      this.totalLeadsAsignadosEstado = this.leadsFiltrados.filter(lead => lead.estatus === 'asignado').length;
      this.totalLeadsConTestDrive = this.leadsFiltrados.filter(lead => lead.test_drive === 'Si').length;
      //this.updateChartData();

      if (this.filtroVendedor) {
        axios.get(`/tiempo-ultima-conexion?vendedor=${this.filtroVendedor}`)
          .then(response => {
            this.tiempoUltimaConexion = response.data.fecha_ultima_conexion;
            this.ultimaPuestaOnline = response.data.ultima_puesta_online;
          })
          .catch(error => {
            console.error("Error al obtener fecha desde la última conexión:", error);
          });
      } else {
        this.tiempoUltimaConexion = 'N/A';
        this.ultimaPuestaOnline = 'N/A';
      }
    },
    //updateChartData() {
      //this.chartOptions.series[0].data = [
        //{ value: this.totalLeadsNuevos, name: 'Nuevos' },
        //{ value: this.totalLeadsAsignados, name: 'En sistema' },
        //{ value: this.totalLeadsEnSeguimiento, name: 'En seguimiento' },
        //{ value: this.totalLeadsCerrados, name: 'Cerrados' },
        //{ value: this.totalLeadsCulminadosEnVenta, name: 'Culminados en venta' },
        //{ value: this.totalLeadsAsignadosEstado, name: 'Asignados' },
      //];
    //},
    guardarLead(lead) {
      axios.post('/update-lead', lead)
        .then(() => {
          alert('Lead actualizado');
        })
        .catch(error => {
          console.error("Error al guardar el lead:", error);
        });
    },
    exportarReporte(formato) {
      axios.post('/exportar-reporte', {
        leads: this.leadsFiltrados,
        vendedor: this.filtroVendedor ? parseInt(this.filtroVendedor) : null,
        filtro_estado: this.filtroEstado || null,
        filtroTestDrive: this.filtroTestDrive || null,
        formato: formato
      }, { responseType: 'blob' })
        .then(response => {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `reporte_leads.${formato}`);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        })
        .catch(error => {
          console.error("Error al exportar reporte:", error);
        });
    }
  },
  created() {
    this.cargarVendedores(); // Carga vendedores cuando se crea el componente
  }
};
</script>


<style scoped>
.table-responsive {
  margin-top: 20px;
  overflow-x: auto; /* Habilita el desplazamiento horizontal en dispositivos móviles */
  -webkit-overflow-scrolling: touch; /* Mejora el desplazamiento en dispositivos iOS */
}

/* Mantén los estilos actuales de la tabla */
.table-responsive .table {
  table-layout: auto; /* Cambia de fixed a auto para que las columnas no sean forzadas a un tamaño fijo */
  width: 100%;
}

.table th, .table td {
  white-space: normal; /* Permite ajuste de texto en varias líneas */
  overflow: visible; /* Evita el recorte del texto */
  text-overflow: unset; /* No se corta el texto */
  padding: 8px; /* Espaciado interno */
  text-align: left; /* Alineación del texto */
  vertical-align: middle; /* Centrado vertical */
  word-wrap: break-word; /* Ajusta palabras largas */
}

/* Estilo para el encabezado con redimensionamiento */
.table-responsive .table th div.resizable-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: col-resize;
}

.table-responsive .table th {
  position: relative;
}

.table-responsive .table th div.resizable-header::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 5px;
  cursor: col-resize;
  background-color: transparent;
}

.chart-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.controls .totalizadores p {
  font-size: 1em;
  color: #333;
  margin: 5px 0;
  font-weight: bold;
}

/* Ajusta el tamaño de los campos de entrada y texto */
.resizable-input,
.resizable-textarea {
  font-size: 0.95em; /* Tamaño de fuente ajustado para los campos */
  padding: 5px; /* Espacio interno de los campos */
  resize: horizontal; /* Permite redimensionar solo horizontalmente */
  overflow: auto; /* Asegura el comportamiento correcto al redimensionar */
  min-width: 50px; /* Ancho mínimo para mejor visualización */
}

/* Estilo específico para el área de texto de seguimiento */
.seguimiento-textarea {
  resize: vertical; /* Permite redimensionar solo verticalmente */
  max-width: 150px; /* Ancho máximo para mantener la tabla compacta */
  min-height: 80px;
}

.export-button {
  margin-right: 10px;
}
</style>