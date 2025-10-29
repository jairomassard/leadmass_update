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

      <!-- Checkbox para habilitar webhooks -->
      <div class="form-check mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="habilitarWebhook" 
          v-model="configuracion.habilitar_webhook" 
        />
        <label class="form-check-label" for="habilitarWebhook">
          Habilitar envío de Webhooks
        </label>
      </div>

      <!-- Campos para Webhooks -->
      <div v-if="configuracion.habilitar_webhook">
        <div class="mb-3">
          <label for="webhook_interno" class="form-label">Webhook Interno</label>
          <input type="text" v-model="configuracion.webhook_interno" class="form-control">
        </div>
        <div class="mb-3">
          <label for="webhook_make" class="form-label">Webhook Make</label>
          <input type="text" v-model="configuracion.webhook_make" class="form-control">
        </div>
        <div class="mb-3">
          <label for="webhook_zapier" class="form-label">Webhook Zapier</label>
          <input type="text" v-model="configuracion.webhook_zapier" class="form-control">
        </div>
      </div>

      <!-- Botón para guardar cambios -->
      <div class="text-center">
        <button @click="guardarConfiguracion" class="btn btn-primary">Guardar Configuración</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      configuracion: {
        enviar_correo: false,
        destinatarios: "",
        habilitar_webhook: false,
        webhook_interno: "",
        webhook_make: "",
        webhook_zapier: ""
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

  