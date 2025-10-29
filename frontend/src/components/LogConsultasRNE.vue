<template>
    <div class="container mt-4">
      <h1 class="text-center mb-4">Consultas Realizadas a la RNE</h1>
  
      <!-- Filtros -->
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <label class="form-label">Filtrar por Vendedor:</label>
          <select class="form-select" v-model="filtroVendedor">
            <option value="">Todos</option>
            <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">
              {{ vendedor.nombre }}
            </option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Filtrar por Fecha:</label>
          <input type="date" class="form-control" v-model="filtroFecha" />
        </div>
        <div class="col-md-3">
          <label class="form-label">Filtrar por Teléfono:</label>
          <input type="text" class="form-control" v-model="filtroTelefono" />
        </div>
        <div class="col-md-3">
          <label class="form-label">Filtrar por Correo:</label>
          <input type="email" class="form-control" v-model="filtroCorreo" />
        </div>
      </div>
  
      <!-- Botón para generar consulta -->
      <div class="text-center mb-4">
        <button class="btn btn-primary" @click="generarConsulta">Ver Consultas Realizadas</button>
        <button class="btn btn-secondary" @click="exportarCSV">Exportar CSV</button>
      </div>

      <!-- Botones de Navegación -->
      <div class="navigation-buttons text-center mt-4">
        <BotonesGlobales />
      </div>
  
      <!-- Tabla de resultados -->
      <div v-if="consultas.length" class="table-responsive">
        <table class="table table-bordered">
          <thead class="table-dark">
            <tr>
              <th>Vendedor</th>
              <th>Teléfono Consultado</th>
              <th>Correo Consultado</th>
              <th>Fecha Consulta</th>
              <th>Tipo</th>
              <th>SMS</th>
              <th>Aplicación</th>
              <th>Llamada</th>
              <th>Fecha Creación TEL</th>
              <th>Aplicación CORR</th>
              <th>Correo CORR</th>
              <th>Fecha Creación CORR</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="consulta in consultas" :key="consulta.id">
              <td>{{ consulta.vendedor }}</td>
              <td>{{ consulta.consulta_tel }}</td>
              <td>{{ consulta.consulta_corr }}</td>
              <td>{{ formatFecha(consulta.fecha_consulta) }}</td>
              <td>{{ consulta.tipo }}</td>
              <td>{{ consulta.sms }}</td>
              <td>{{ consulta.aplicacion }}</td>
              <td>{{ consulta.llamada }}</td>
              <td>{{ consulta.fecha_creacion_tel }}</td>
              <td>{{ consulta.aplicacion_corr }}</td>
              <td>{{ consulta.correo_corr }}</td>
              <td>{{ consulta.fecha_creacion_corr }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "../axios";
  import BotonesGlobales from './BotonesGlobales.vue';
  
  export default {
    data() {
      return {
        consultas: [],
        vendedores: [],
        filtroVendedor: "",
        filtroFecha: "",
        filtroTelefono: "",
        filtroCorreo: "",
      };
    },
    methods: {
      generarConsulta() {
        const params = {
          vendedor_id: this.filtroVendedor || null,
          fecha: this.filtroFecha || null,
          telefono: this.filtroTelefono || null,
          correo: this.filtroCorreo || null,
        };
  
        axios
          .get("/get-log-consultas-rne", { params })
          .then((response) => {
            this.consultas = response.data;
          })
          .catch((error) => {
            console.error("Error al generar la consulta:", error);
          });
      },
      exportarCSV() {
        const csvContent = this.consultas
          .map((consulta) =>
            [
              consulta.vendedor,
              consulta.consulta_tel,
              consulta.consulta_corr,
              consulta.fecha_consulta,
              consulta.tipo,
              consulta.sms,
              consulta.aplicacion,
              consulta.llamada,
              consulta.fecha_creacion_tel,
              consulta.aplicacion_corr,
              consulta.correo_corr,
              consulta.fecha_creacion_corr,
            ].join(";")
          )
          .join("\n");
  
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.setAttribute("download", "resultados_consultas_realizadas_RNE.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      },
      formatFecha(fecha) {
        if (!fecha) return "";
        const options = { year: "numeric", month: "2-digit", day: "2-digit" };
        return new Date(fecha).toLocaleDateString("es-CO", options);
      },
      cargarVendedores() {
        axios
          .get("/get-vendedores")
          .then((response) => {
            this.vendedores = response.data;
          })
          .catch((error) => {
            console.error("Error al cargar vendedores:", error);
          });
      },
    },
    mounted() {
      this.cargarVendedores();
    },
    components: {
      BotonesGlobales
  }
  };
  </script>
  