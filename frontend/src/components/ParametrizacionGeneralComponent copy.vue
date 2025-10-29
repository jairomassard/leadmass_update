<template>
    <div class="container mt-5">
      <h1 class="text-center">Parametrización General</h1>
  
      <div class="mt-4">
        <!-- Checkbox para habilitar o deshabilitar el envío de correos -->
        <div class="form-check mb-3">
          <input 
            class="form-check-input" 
            type="checkbox" 
            id="enviarCorreo" 
            v-model="configuracion.enviar_correo" 
          />
          <label class="form-check-label" for="enviarCorreo">
            Habilitar envío de correos electrónicos
          </label>
        </div>
  
        <!-- Campo para destinatarios -->
        <div class="mb-3">
          <label for="destinatarios" class="form-label">Destinatarios</label>
          <input 
            type="text" 
            id="destinatarios" 
            v-model="configuracion.destinatarios" 
            class="form-control" 
            placeholder="Ingrese correos separados por coma" 
            :disabled="!configuracion.enviar_correo" 
          />
        </div>
  
        <!-- Botón para guardar cambios -->
        <div class="text-center">
          <button @click="guardarConfiguracion" class="btn btn-primary">Guardar Configuración</button>
        </div>
      </div>
    </div>

    <!-- Botones de Navegación -->
    <div class="navigation-buttons text-center mt-4">
      <BotonesGlobales />
    </div>
  </template>
  
  <script>
  import axios from '../axios';
  import BotonesGlobales from './BotonesGlobales.vue';
  
  export default {
    components: {
        BotonesGlobales
    },
    data() {
      return {
        configuracion: {
          enviar_correo: false,
          destinatarios: ""
        }
      };
    },
    mounted() {
      this.cargarConfiguracion();
    },
    methods: {
      async cargarConfiguracion() {
        try {
          const response = await axios.get('/get-configuracion-general');
          this.configuracion = response.data;
        } catch (error) {
          console.error("Error al cargar la configuración:", error);
        }
      },
      async guardarConfiguracion() {
        try {
          await axios.post('/update-configuracion-general', this.configuracion);
          alert("Configuración guardada correctamente.");
        } catch (error) {
          console.error("Error al guardar la configuración:", error);
          alert("Ocurrió un error al guardar la configuración.");
        }
      }
    }
  };
  </script>
  