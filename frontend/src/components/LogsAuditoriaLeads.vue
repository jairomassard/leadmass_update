<template>
    <div class="container mt-4">
      <h1 class="text-center mb-4">Logs de Auditoría</h1>

      <!-- Botones de Navegación -->
      <div class="navigation-buttons text-center mt-4">
        <BotonesGlobales />
      </div>
  
      <!-- Botón de exportación -->
      <div class="text-center mt-4">
        <button class="btn btn-info" @click="exportLogs">Exportar a CSV</button>
      </div>

      <!-- Filtros de búsqueda -->
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <label for="filterUser" class="form-label">Filtrar por usuario:</label>
          <select v-model="filterUser" id="filterUser" class="form-select">
            <option value="">Todos</option>
            <option v-for="user in users" :key="user.id" :value="user.id">
              {{ user.name }}
            </option>
          </select>
        </div>
        <div class="col-md-4">
          <label for="filterAction" class="form-label">Filtrar por acción:</label>
          <select v-model="filterAction" id="filterAction" class="form-select">
            <option value="">Todos</option>
            <option value="Creación">Creación</option>
            <option value="Actualización">Actualización</option>
            <option value="Eliminación">Eliminación</option>
          </select>
        </div>
        <div class="col-md-4">
          <label for="filterDate" class="form-label">Filtrar por fecha:</label>
          <input type="date" v-model="filterDate" id="filterDate" class="form-control" />
        </div>
      </div>
  
      <!-- Tabla de Logs -->
      <div class="table-responsive">
        <table class="table table-bordered table-striped">
          <thead class="table-dark">
            <tr>
              <th>ID</th>
              <th>Fecha y Hora</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Campo Modificado</th>
              <th>Valor Anterior</th>
              <th>Valor Nuevo</th>
              <th>Comentarios</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in filteredLogs" :key="log.id">
              <td>{{ log.id }}</td>
              <td>{{ log.fecha_hora }}</td>
              <td>{{ log.usuario }}</td>
              <td>{{ log.accion }}</td>
              <td>{{ log.campo_modificado || '-' }}</td>
              <td>{{ log.valor_anterior || '-' }}</td>
              <td>{{ log.valor_nuevo || '-' }}</td>
              <td>{{ log.comentarios }}</td>
            </tr>
          </tbody>
        </table>
      </div>
  

    </div>
  </template>
  
  <script>
  import axios from '../axios';
  import BotonesGlobales from './BotonesGlobales.vue';
  
  export default {
    data() {
      return {
        logs: [], // Almacena los registros de auditoría
        users: [], // Almacena los usuarios disponibles para el filtro
        filterUser: '',
        filterAction: '',
        filterDate: ''
      };
    },
    computed: {
      filteredLogs() {
        return this.logs.filter(log => {
          const matchesUser = this.filterUser ? log.usuario_id === Number(this.filterUser) : true;
          const matchesAction = this.filterAction ? log.accion === this.filterAction : true;
          const matchesDate = this.filterDate ? log.fecha_hora.split(' ')[0] === this.filterDate : true;
  
          return matchesUser && matchesAction && matchesDate;
        });
      }
    },
    methods: {
      fetchLogs() {
        axios.get('/get-logs')
          .then(response => {
            this.logs = response.data.logs;
            this.users = response.data.users;
          })
          .catch(error => {
            console.error("Error al obtener los logs:", error);
            alert("No se pudieron cargar los logs de auditoría.");
          });
      },
      exportLogs() {
        const csvContent = [
          ['ID', 'Fecha y Hora', 'Usuario', 'Acción', 'Campo Modificado', 'Valor Anterior', 'Valor Nuevo', 'Comentarios'],
          ...this.filteredLogs.map(log => [
            log.id, log.fecha_hora, log.usuario, log.accion, log.campo_modificado || '-',
            log.valor_anterior || '-', log.valor_nuevo || '-', log.comentarios
          ])
        ].map(row => row.join(';')).join('\n');
  
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'logs_auditoria.csv';
        link.click();
      }
    },
    created() {
      this.fetchLogs();
    },
    components: {
      BotonesGlobales
    }
  };
  </script>
  
  <style scoped>
  .table {
    font-size: 0.9em;
  }
  </style>
  