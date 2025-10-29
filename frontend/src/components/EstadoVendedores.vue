<template>
    <div>
      <!-- Botón Regresar que redirige según el rol 
      <button @click="regresar" class="btn btn-primary mb-3">Regresar</button>-->
      <h2>Estado de Conexión de Vendedores</h2>
      <button @click="obtenerEstadoVendedores">Verificar Conexión Vendedores</button>
  
      <table v-if="vendedores.length > 0" class="estado-vendedores">
        <thead>
          <tr>
            <th>Nombre del Vendedor</th>
            <th>Estado de Conexión</th>
            <th><button @click="refrescarEstadoVendedores">Refrescar</button></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="vendedor in vendedores" :key="vendedor.id">
            <td>{{ vendedor.nombre }}</td>
            <td>
              <span :class="vendedor.en_linea ? 'online' : 'offline'">
                {{ vendedor.en_linea ? 'En línea' : 'Fuera de línea' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  import axios from '../axios';
  
  export default {
    data() {
      return {
        vendedores: [],
        esAdministrador: false  // Variable para almacenar si el usuario es administrador
      };
    },
    created() {
      // Llamada inicial para verificar el rol del usuario
      axios.get('/user-info')
        .then(response => {
          this.esAdministrador = response.data.es_administrador;
        })
        .catch(error => {
          console.error("Error al obtener el rol del usuario:", error);
        });
    },
    methods: {
      obtenerEstadoVendedores() {
        axios.get('/estado-vendedores')
          .then(response => {
            this.vendedores = response.data.vendedores;
          })
          .catch(error => {
            console.error("Error al obtener el estado de los vendedores:", error);
          });
      },
      refrescarEstadoVendedores() {
        this.obtenerEstadoVendedores();
      },
      regresar() {
        // Redirigir según el rol del usuario
        if (this.esAdministrador) {
          this.$router.push('/menu');  // Redirigir al menú del administrador
        } else {
          this.$router.push('/leads-supervisor');  // Redirigir a la página de supervisión de leads
        }
      }
    }
  };
  </script>
  
  <style>
  .estado-vendedores {
    width: 100%;
    border-collapse: collapse;
  }
  .estado-vendedores th, .estado-vendedores td {
    border: 1px solid #ddd;
    padding: 8px;
  }
  .estado-vendedores th {
    background-color: #f2f2f2;
  }
  .online {
    color: green;
    font-weight: bold;
  }
  .offline {
    color: red;
    font-weight: bold;
  }
  </style>
  
  