<template>
    <div class="container mt-4">
      <h1 class="text-center mb-4">Leads Capturados por Experts</h1>
  
      <!-- Filtros al principio -->
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <label class="form-label">Filtrar por usuario expert:</label>
          <select class="form-select" v-model="filtroUsuarioExpert">
            <option value="">Todos</option>
            <option v-for="expert in expertos" :key="expert.id" :value="expert.id">
              {{ expert.nombre }}
            </option>
          </select>
        </div>
  
        <div class="col-md-4">
          <label class="form-label">Filtrar por fecha:</label>
          <input type="date" class="form-control" v-model="filtroFecha" />
        </div>
      </div>
  
      <!-- Botón para generar la consulta -->
      <div class="text-center mb-4">
        <button class="btn btn-primary" @click="generarConsulta">Generar Consulta</button>
      </div>
      
      <!-- Mostrar el conteo de registros obtenidos -->

      <div v-if="consultaGenerada" class="text-center mb-3">
         <p><strong>Total de registros encontrados: {{ totalRegistros }}</strong></p>
      </div>

      <!-- Tabla de resultados de leads -->
      <div v-if="consultaGenerada" class="table-responsive">
        <table class="table table-bordered">
          <thead class="table-dark">
            <tr>
              <th>Nombres</th>
              <th>Apellidos</th>
              <th>Identificación</th>
              <th>Teléfono</th>
              <th>Correo</th>
              <th>Fecha Lead</th>
              <th>Origen Lead</th>
              <th>Marca de Interés</th>
              <th>Modelo Interesado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lead in leadsFiltrados" :key="lead.id">
              <td>{{ lead.nombres }}</td>
              <td>{{ lead.apellidos }}</td>
              <td>{{ lead.identificacion }}</td>
              <td>{{ lead.telefono }}</td>
              <td>{{ lead.correo }}</td>
              <td>{{ lead.fecha_lead }}</td>
              <td>{{ lead.origen_lead }}</td>
              <td>{{ lead.marca_interes }}</td>
              <td>{{ lead.modelo_interesado }}</td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- Botón para regresar a la página de supervisión 
      <div class="text-center mt-4">
        <button class="btn btn-secondary" @click="regresarPaginaAnterior">Regresar</button>
      </div> -->
    </div>
  </template>
  
  <script>
  import axios from '../axios';
  
  export default {
    data() {
      return {
        leads: [],
        leadsFiltrados: [],
        expertos: [],
        consultaGenerada: false,
        filtroUsuarioExpert: '',
        filtroFecha: '',
        totalRegistros: 0, // Variable para el conteo de registros
      };
    },
    methods: {
      // Generar consulta en función de los filtros seleccionados
      generarConsulta() {
        const params = {
          expert_id: this.filtroUsuarioExpert || null,
          fecha: this.filtroFecha || null,
        };
  
        axios
          .get('/leads-capturados-expert', { params })
          .then(response => {
            this.leads = response.data;
            this.leadsFiltrados = [...this.leads];
            this.totalRegistros = this.leads.length; // Calcular el total de registros
            this.consultaGenerada = true;
            //this.cargarUsuariosExpert(); // Cargar lista de expertos solo si la consulta fue exitosa
          })
          .catch(error => {
            console.error("Error al generar la consulta de leads:", error);
          });
      },
      // Cargar los usuarios expertos desde el servidor
      cargarUsuariosExpert() {
        axios
          .get('/get-usuarios-expert')
          .then(response => {
            this.expertos = response.data;
          })
          .catch(error => {
            console.error("Error al cargar usuarios expertos:", error);
          });
      },
      formatFecha(fecha) {
        if (!fecha) return '';
        const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
        return new Date(fecha).toLocaleDateString('es-CO', options);
      },
      regresarPaginaAnterior() {
        this.$router.go(-1); // Navega a la página anterior
      },
    },
    mounted() {
      this.cargarUsuariosExpert(); // Cargar lista de expertos al montar el componente
    },
  };
  </script>
  
  <style scoped>
  .table-responsive {
    margin-top: 20px;
  }
  </style>
  
  