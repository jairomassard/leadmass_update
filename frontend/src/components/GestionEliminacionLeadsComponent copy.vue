<template>
  <div id="supervisor-leads" class="container mt-4">
    <h1 class="text-center mb-4">Gestión y Eliminación de Leads</h1>

    <!-- Botón para cargar contenido de la tabla -->
    <div class="text-center mb-4">
      <button class="btn btn-secondary" @click="generarContenidoTabla">Generar Contenido Tabla</button>
    </div>

    <!-- Gráfico de embudo -->
    <div class="chart-container mb-4 d-flex justify-content-center">
      <v-chart :option="chartOptions" style="width: 60%; height: 300px;" />
    </div>

    <!-- Totalizadores -->
    <div class="controls d-flex justify-content-between align-items-center mb-4">
      <div class="totalizadores">
        <p>Total leads en sistema: <strong>{{ totalLeadsAsignados }}</strong></p>
        <p>Total leads Nuevos: <strong>{{ totalLeadsNuevos }}</strong></p>
        <p>Total leads en seguimiento: <strong>{{ totalLeadsEnSeguimiento }}</strong></p>
        <p>Total leads cerrados: <strong>{{ totalLeadsCerrados }}</strong></p>
        <p>Total leads culminados en venta: <strong>{{ totalLeadsCulminadosEnVenta }}</strong></p>
        <p>Total leads asignados: <strong>{{ totalLeadsAsignadosEstado }}</strong></p>
        <p>Última conexión del vendedor: <strong>{{ tiempoUltimaConexion }}</strong></p>
        <p>Última puesta en línea: <strong>{{ ultimaPuestaOnline }}</strong></p>
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
            <th v-for="header in headers" :key="header" :style="{ width: columnWidths[header] }">
              <div class="resizable-header" @mousedown="startResize($event, header)">
                {{ header }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lead in leadsFiltrados" :key="lead.id">
            <td><input :value="getLeadValue(lead, 'nombres')" @input="setLeadValue(lead, 'nombres', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'apellidos')" @input="setLeadValue(lead, 'apellidos', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'identificacion')" @input="setLeadValue(lead, 'identificacion', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'telefono')" @input="setLeadValue(lead, 'telefono', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'direccion')" @input="setLeadValue(lead, 'direccion', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'ciudad')" @input="setLeadValue(lead, 'ciudad', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'correo')" @input="setLeadValue(lead, 'correo', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'fecha_lead')" @input="setLeadValue(lead, 'fecha_lead', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'origen_lead')" @input="setLeadValue(lead, 'origen_lead', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'marca_interes')" @input="setLeadValue(lead, 'marca_interes', $event.target.value)" class="form-control" /></td>
            <td><input :value="getLeadValue(lead, 'modelo_interesado')" @input="setLeadValue(lead, 'modelo_interesado', $event.target.value)" class="form-control" /></td>
            <td>
              <select :value="getLeadValue(lead, 'estatus')" @change="setLeadValue(lead, 'estatus', $event.target.value)" class="form-select">
                <option value="nuevo">Nuevo</option>
                <option value="asignado">Asignado</option>
                <option value="en seguimiento">En Seguimiento</option>
                <option value="cerrado">Cerrado</option>
                <option value="culmina en venta">Culmina en Venta</option>
              </select>
            </td>
            <td>
              <select :value="getLeadValue(lead, 'test_drive')" @change="setLeadValue(lead, 'test_drive', $event.target.value)" class="form-select">
                <option value="No">No</option>
                <option value="Si">Si</option>
              </select>
            </td>
            <td>
              <textarea :value="getLeadValue(lead, 'seguimientos')" @input="setLeadValue(lead, 'seguimientos', $event.target.value)" class="form-control seguimiento-textarea"></textarea>
            </td>
            <td>
              <button class="btn btn-primary me-2" @click="guardarLead(lead)">Guardar</button>
              <button class="btn btn-danger" @click="eliminarLead(lead.id)">Eliminar</button>
            </td>
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
      headers: [
        "Nombres", "Apellidos", "Identificación", "Teléfono", "Dirección", "Ciudad", "Correo", "Fecha Lead",
        "Origen Lead", "Marca de Interés", "Modelo Interesado", "Estatus", "Test Drive", "Seguimientos", "Acciones"
      ],
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
      resizingColumn: null,
      initialX: 0,
      initialWidth: 0,
      columnWidths: {},  // Aquí inicializamos los anchos de columna
      chartOptions: {
        tooltip: { trigger: 'item' },
        legend: { top: 'bottom' },
        series: [{
          type: 'funnel',
          left: '10%',
          width: '80%',
          sort: 'descending',
          label: { show: true, position: 'inside' },
          data: []
        }],
      },
    };
  },
  methods: {
    getLeadValue(lead, property) {
      return lead && lead[property] ? lead[property] : '';
    },
    setLeadValue(lead, property, value) {
      if (lead) {
        lead[property] = value;
      }
    },
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
        .catch((error) => {
          console.error("Error al cargar leads:", error);
        });
    },
    cargarVendedores() {
      axios.get('/get-vendedores')
        .then((response) => {
          this.vendedores = response.data;
        })
        .catch((error) => {
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
            console.error("Error al obtener fecha de la última conexión:", error);
          });
      } else {
        this.tiempoUltimaConexion = 'N/A';
        this.ultimaPuestaOnline = 'N/A';
      }
    },
    updateChartData() {
      this.chartOptions.series[0].data = [
        { value: this.totalLeadsAsignados, name: 'En sistema' },
        { value: this.totalLeadsNuevos, name: 'Nuevos' },
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
    eliminarLead(leadId) {
      if (confirm("¿Estás seguro de que deseas eliminar este lead?")) {
        axios.post('/delete-lead', { lead_id: leadId })
          .then(response => {
            alert(response.data.message);
            this.cargarLeads();
          })
          .catch(error => {
            console.error("Error al eliminar el lead:", error);
            alert("No se pudo eliminar el lead.");
          });
      }
    },
    startResize(event, header) {
      this.resizingColumn = header;
      this.initialX = event.clientX;
      this.initialWidth = this.columnWidths[header] || this.$el.querySelectorAll("th")[this.headers.indexOf(header)].offsetWidth;
      document.addEventListener("mousemove", this.resizeColumn);
      document.addEventListener("mouseup", this.stopResize);
    },
    resizeColumn(event) {
      if (!this.resizingColumn) return;
      const deltaX = event.clientX - this.initialX;
      const newWidth = Math.max(this.initialWidth + deltaX, 50) + "px"; // Min width 50px
      this.columnWidths = { ...this.columnWidths, [this.resizingColumn]: newWidth }; // Actualización directa del objeto
    },
    stopResize() {
      document.removeEventListener("mousemove", this.resizeColumn);
      document.removeEventListener("mouseup", this.stopResize);
      this.resizingColumn = null;
    },
  },
  created() {
    this.cargarVendedores(); // Carga vendedores cuando se crea el componente
  }
};
</script>

<style scoped>
.table-responsive .table th div.resizable-header {
  display: inline-block;
  width: 100%;
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

.table-responsive {
  margin-top: 20px;
}

/* Tamaño de fuente reducido para toda la tabla y sus celdas */
.table-responsive .table,
.table-responsive .table th,
.table-responsive .table td {
  font-size: 0.95em; /* Ajusta el tamaño de fuente en toda la tabla */
  padding: 8px; /* Espacio entre celdas */
}

/* Estilo para los campos de entrada, selectores y área de texto en la tabla */
.table-responsive .table input,
.table-responsive .table select,
.table-responsive .table textarea {
  font-size: 0.95em; /* Tamaño de fuente ajustado para los campos */
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
