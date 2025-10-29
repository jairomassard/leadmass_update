<template>
  <div id="supervisor-leads" class="container mt-4">
    <h1 class="text-center mb-4">Reporte de Leads</h1>

    <!-- Botón para cargar contenido de la tabla -->
    <div class="text-center mb-4">
      <button class="btn btn-secondary" @click="generarContenidoTabla">Generar Contenido Tabla</button>
    </div>

    <!-- Gráfico de Embudo-->
    <div class="chart-container mb-4 d-flex justify-content-center">
      <v-chart :option="chartOptions" style="width: 100%; height: 350px;" />
    </div>

    <!-- Botones de Exportación y Totalizadores -->
    <div class="controls d-flex justify-content-between align-items-center mb-4">
      <div>
        <button class="btn btn-success me-2" @click="exportarReporte('pdf')">Exportar PDF</button>
        <button class="btn btn-info" @click="exportarReporte('csv')">Exportar CSV</button>
      </div>
      <div class="totalizadores">
        <p>Total leads en sistema: <strong>{{ totalLeadsAsignados }}</strong></p>
        <p>Total leads Nuevos: <strong>{{ totalLeadsNuevos }}</strong></p>
        <p>Total leads en seguimiento: <strong>{{ totalLeadsEnSeguimiento }}</strong></p>
        <p>Total leads cerrados: <strong>{{ totalLeadsCerrados }}</strong></p>
        <p>Total leads culminados en venta: <strong>{{ totalLeadsCulminadosEnVenta }}</strong></p>
        <p>Total leads asignados: <strong>{{ totalLeadsAsignadosEstado }}</strong></p>
        <p>Última conexión del vendedor: <strong>{{ formatearFecha(tiempoUltimaConexion) }}</strong></p>
        <p>Última puesta en línea: <strong>{{ formatearFecha(ultimaPuestaOnline) }}</strong></p>
      </div>
    </div>

    <!-- Botones de Navegación -->
    <div class="navigation-buttons text-center mt-4">
      <BotonesGlobales />
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
            <th>Nombres</th>
            <th>Apellidos</th>
            <th>Identificación</th>
            <th>Teléfono</th>
            <th>Dirección</th>
            <th>Ciudad</th>
            <th>Correo</th>
            <th>Fecha Lead</th>
            <th>Origen Lead</th>
            <th>Marca de Interés</th>
            <th>Modelo Interesado</th>
            <th>Estatus</th>
            <th>Test Drive</th>
            <th>Seguimientos</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lead in leadsFiltrados" :key="lead.id">
            <td><span>{{ lead.nombres }}</span></td>
            <td><span>{{ lead.apellidos }}</span></td>
            <td><span>{{ lead.identificacion }}</span></td>
            <td><span>{{ lead.telefono }}</span></td>
            <td><span>{{ lead.direccion }}</span></td>
            <td><span>{{ lead.ciudad }}</span></td>
            <td><span>{{ lead.correo }}</span></td>
            <td><span>{{ formatearFecha(lead.fecha_lead) }}</span></td>
            <td><span>{{ lead.origen_lead }}</span></td>
            <td><span>{{ lead.marca_interes }}</span></td>
            <td><span>{{ lead.modelo_interesado }}</span></td>
            <td><span>{{ lead.estatus }}</span></td>
            <td><span>{{ lead.test_drive }}</span></td>
            <td><span>{{ lead.seguimientos }}</span></td>
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
import BotonesGlobales from './BotonesGlobales.vue';

use([TitleComponent, TooltipComponent, LegendComponent, FunnelChart, CanvasRenderer]);

export default {
  components: {
    VChart,
    BotonesGlobales
  },
  data() {
    return {
      leads: [],
      leadsFiltrados: [],
      filtroVendedor: '',
      filtroEstado: '',
      filtroTestDrive: '',
      vendedores: [],
      totalLeadsAsignados: 0,
      totalLeadsNuevos: 0,
      totalLeadsEnSeguimiento: 0,
      totalLeadsCerrados: 0,
      totalLeadsCulminadosEnVenta: 0,
      totalLeadsAsignadosEstado: 0,
      tiempoUltimaConexion: '',
      ultimaPuestaOnline: '',
      contenidoGenerado: false, // Controla la visibilidad del contenido
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
    formatearFecha(fecha) {
      if (!fecha) return "N/A"; // Manejo de fechas vacías
      // Validar formato esperado "YYYY-MM-DD"
      const regex = /^\d{4}-\d{2}-\d{2}$/;
      if (!regex.test(fecha)) {
        console.warn(`Formato de fecha no reconocido: ${fecha}`);
        return fecha; // Devolver la fecha como está si no coincide con el formato esperado
      }
    
      // Convertir a formato "DD/MM/YYYY"
      const [year, month, day] = fecha.split("-");
      return `${day}/${month}/${year}`;
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
      this.updateChartData();

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
    updateChartData() {
      this.chartOptions.series[0].data = [
        { value: this.totalLeadsAsignados, name: 'En sistema' },
        { value: this.totalLeadsNuevos, name: 'Nuevo' },
        { value: this.totalLeadsEnSeguimiento, name: 'En seguimiento' },
        { value: this.totalLeadsCerrados, name: 'Cerrados' },
        { value: this.totalLeadsCulminadosEnVenta, name: 'Culminados en venta' },
      ];
    },
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

.table-responsive {
  margin-top: 20px;
}

/* Tamaño de fuente reducido para toda la tabla y sus celdas */
.table-responsive .table,
.table-responsive .table th,
.table-responsive .table td {
  font-size: 0.9em; /* Ajusta el tamaño de fuente en toda la tabla */
  padding: 8px; /* Espacio entre celdas */
}

/* Estilo para los campos de entrada, selectores y área de texto en la tabla */
.table-responsive .table input,
.table-responsive .table select,
.table-responsive .table textarea {
  font-size: 0.9em; /* Tamaño de fuente ajustado para los campos */
  padding: 5px; /* Espacio interno de los campos */
}

/* Estilo específico para el área de texto de seguimiento */
.seguimiento-textarea {
  resize: both; /* Permite redimensionar en ambas direcciones */
  min-width: 100px;
  min-height: 80px;
}

.export-button {
  margin-right: 10px;
}
</style>
