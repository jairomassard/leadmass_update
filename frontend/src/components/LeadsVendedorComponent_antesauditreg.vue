<template>
  <div id="app" class="container mt-4">
    <h1 class="text-center mb-4">Gestión de Leads</h1>

    <!-- Botón para ponerse en línea o fuera de línea -->
    <div class="text-center mb-4">
      <button @click="toggleEnLinea" :class="['btn', 'btn-toggle', enLinea ? 'btn-success' : 'btn-danger']">
        {{ enLinea ? 'En línea' : 'Fuera de línea' }}
      </button>

      
    </div>

    
    <!-- Totalizadores -->
    <div v-if="totalLeads !== null" class="row text-center mb-4">
      <div class="col mb-4" v-for="(title, index) in totalTitles" :key="index">
        <div class="card shadow-sm total-card">
          <div class="card-body">
            <h5 class="card-title" style="font-size: 0.9em">{{ title }}</h5>
            <p class="card-text fs-5 fw-bold">{{ totalValues[index] }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Selectores de Filtro -->
    <div class="row mb-4">
      <div class="col-md-6">
        <label class="form-label">Filtrar por Estatus</label>
        <select v-model="filtroEstatus" @change="filtrarLeads" class="form-select">
          <option value="">Todos</option>
          <option value="asignado">Asignado</option>
          <option value="en seguimiento">En Seguimiento</option>
          <option value="cerrado">Cerrado</option>
          <option value="culmina en venta">Culmina en Venta</option>
        </select>
      </div>
      <div class="col-md-6">
        <label class="form-label">Filtrar por Test Drive</label>
        <select v-model="filtroTestDrive" @change="filtrarLeads" class="form-select">
          <option value="">Todos</option>
          <option value="Si">Si</option>
          <option value="No">No</option>
        </select>
      </div>
    </div>

    <!-- Navegación entre leads -->
    <div v-if="leadActual" class="text-center mb-4">
      <button @click="leadAnterior" class="btn btn-outline-primary me-2">← Anterior</button>
      <span class="position-indicator">
        {{ currentIndex + 1 }} de {{ leads.length }}
      </span>
      <button @click="leadSiguiente" class="btn btn-outline-primary">Siguiente →</button>
    </div>

    <!-- Formulario de edición de lead -->
    <div v-if="leadActual" class="form-leads">
      <div class="row g-3">
        <div v-for="(label, index) in leadLabels" :key="index" class="col-md-4">
          <label class="form-label">{{ label.text }}</label>
          <input v-model="leadActual[label.field]" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-4">
          <label class="form-label">Estatus</label>
          <select v-model="leadActual.estatus" :disabled="!editMode" class="form-select">
            <option value="asignado">Asignado</option>
            <option value="en seguimiento">En Seguimiento</option>
            <option value="cerrado">Cerrado</option>
            <option value="culmina en venta">Culmina en Venta</option>
          </select>
        </div>

        <div class="col-4">
          <label class="form-label">Test Drive</label>
          <select v-model="leadActual.test_drive" :disabled="!editMode" class="form-select">
            <option value="No">No</option>
            <option value="Si">Si</option>
          </select>
        </div>
      </div>


      <!-- Campo de Seguimientos -->
      <div class="row g-3 mt-3">
        <div class="col-12">
          <label class="form-label">Seguimientos</label>
          <textarea v-model="leadActual.seguimientos" :disabled="!editMode" class="form-control"></textarea>
        </div>
      </div>

      <!-- Botones de edición y consulta -->
      <div class="text-center mt-4">
          <!-- Botón "Consultar RNE" -->
          <button 
              @click="consultarRNE" 
              :disabled="loading" 
              :class="['btn', loading ? 'btn-secondary' : 'btn-info']"
          >
              <span v-if="loading">
                  <i class="spinner-border spinner-border-sm"></i> Consultando...
              </span>
              <span v-else>Consulta al RNE</span>
          </button>
      </div>

      <!-- Botones de edición y guardado -->
      <div class="text-center mt-4">
        <button v-if="!editMode" @click="habilitarEdicion" class="btn btn-primary">Editar</button>
        <button v-if="editMode" @click="guardarCambios" class="btn btn-success">Guardar</button>
      </div>
    </div>

    <!-- Mensaje cuando no hay leads asignados -->
    <div v-else class="text-center mt-4">
      <p class="text-muted">No hay leads asignados actualmente.</p>
    </div>

    <!-- Resultados de la consulta al RNE -->
    <div v-if="resultadosRNE" class="mt-4">
        <h5 class="text-center">Resultado para Teléfono</h5>
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Número Telefónico</th>
              <th>Acepta ser contactado por:</th>
              <th>Tipo</th>
              <th>Fecha Registro en RNE</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="resultadosRNE.telefono">
              <td>{{ resultadosRNE.telefono.llave }}</td>
              <td>
                <ul>
                  <!-- Corregir el acceso a las opciones de contacto -->
                  <li>SMS: {{ resultadosRNE.telefono.opcionesContacto.sms ? 'Sí' : 'No' }}</li>
                  <li>Aplicación: {{ resultadosRNE.telefono.opcionesContacto.aplicacion ? 'Sí' : 'No' }}</li>
                  <li>Llamada: {{ resultadosRNE.telefono.opcionesContacto.llamada ? 'Sí' : 'No' }}</li>
                </ul>
              </td>
              <td>{{ resultadosRNE.telefono.tipo }}</td>
              <td>{{ resultadosRNE.telefono.fechaCreacion }}</td>
            </tr>
            <tr v-else>
              <td colspan="4" class="text-center">NO EXISTE REGISTRO PARA ESE NÚMERO TELEFÓNICO</td>
            </tr>
          </tbody>
        </table>

        <h5 class="text-center mt-4">Resultado para Correo</h5>
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Correo</th>
              <th>Acepta ser contactado por:</th>
              <th>Fecha Registro en RNE</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="resultadosRNE.correo">
              <td>{{ resultadosRNE.correo.llave }}</td>
              <td>
                <ul>
                  <li>Correo Electrónico: {{ resultadosRNE.correo.opcionesContacto.correo_electronico ? 'Sí' : 'No' }}</li>
                  <li>Aplicaciones: {{ resultadosRNE.correo.opcionesContacto.aplicacion ? 'Sí' : 'No' }}</li>
                </ul>
              </td>
              <td>{{ resultadosRNE.correo.fechaCreacion }}</td>
            </tr>
            <tr v-else>
              <td colspan="3" class="text-center">NO EXISTE REGISTRO PARA ESE CORREO</td>
            </tr>
          </tbody>
        </table>
    </div>
    
    <!-- Botones globales para navegación -->
    <div class="text-center mt-4">
      <BotonesGlobalesSalir />
    </div>
  </div>
</template>

<script>
import axios from '../axios';
import BotonesGlobalesSalir from './BotonesGlobalesSalir.vue';

export default {
  data() {
    return {
      leads: [],
      leadsFiltrados: [], // Lista filtrada de leads
      currentIndex: 0,
      leadActual: null,
      resultadosRNE: null, // Aquí guardamos los resultados
      loading: false, // Estado de carga
      editMode: false,
      totalLeads: 0,
      totalLeadsAsignado: 0,
      totalLeadsEnSeguimiento: 0,
      totalLeadsCerrados: 0,
      totalLeadsCulminadosEnVenta: 0,
      totalTestDrive: 0,
      enLinea: false,
      vendedorId: null,

      // Variables de filtro
      filtroEstatus: "",
      filtroTestDrive: "",
      
      leadLabels: [
        { text: "Nombres", field: "nombres" },
        { text: "Apellidos", field: "apellidos" },
        { text: "Teléfono", field: "telefono" },
        { text: "Dirección", field: "direccion" },
        { text: "Ciudad", field: "ciudad" },
        { text: "Correo", field: "correo" },
        { text: "Fecha Lead", field: "fecha_lead" },
        { text: "Origen Lead", field: "origen_lead" },
        { text: "Marca de Interés", field: "marca_interes" },
        { text: "Modelo Interesado", field: "modelo_interesado" }
        
      ],

      totalTitles: [
        "Leads del Vendedor",
        "Asignado",
        "En Seguimiento",
        "Cerrados",
        "Cierre en Venta",
        "Con Test Drive"

      ],
     };
  },

  computed: {
    totalValues() {
      return [
        this.totalLeads,
        this.totalLeadsAsignado,
        this.totalLeadsEnSeguimiento,
        this.totalLeadsCerrados,
        this.totalLeadsCulminadosEnVenta,
        this.totalTestDrive
      ];
    }
  },

  methods: {
    iniciarPing() {
      this.pingInterval = setInterval(() => {
        if (this.enLinea) {
          axios.post(`/update-vendedor-estado`, {
            vendedor_id: this.vendedorId,
            estado: true
          })
          .then(() => {
            console.log("Ping enviado para mantener el estado en línea.");
          })
          .catch(error => {
            console.error("Error en el ping de estado en línea:", error);
          });
        }
      }, 1800000); // Enviar ping cada 30 minutos
    },
    detenerPing() {
      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
      }
    },

    consultarLeads() {
      this.vendedorId = localStorage.getItem('vendedor_actual');

      if (!this.vendedorId) {
        console.error("No se encontró el vendedor_id en localStorage.");
        return;
      }

      axios.get(`/get-leads-vendedor?vendedor=${this.vendedorId}`)
        .then(response => {
          this.leads = response.data.map(lead => ({
            ...lead,
            fecha_lead: this.formatearFechaColombia(lead.fecha_lead) // Ajustar fecha a formato Colombia
          }));
          this.leadsFiltrados = [...this.leads]; // Inicializa leadsFiltrados
          if (this.leadsFiltrados.length) {
            this.leadActual = this.leadsFiltrados[this.currentIndex];
          }
          this.updateTotalizadores();
        })
        .catch(error => {
          console.error("Error al obtener los leads:", error);
        });
    },

    formatearFechaColombia(fechaISO) {
      if (!fechaISO) return "";
      const opciones = { year: "numeric", month: "2-digit", day: "2-digit" };
      const fecha = new Date(fechaISO);
      return fecha.toLocaleDateString("es-CO", opciones); // Formato "DD/MM/AAAA"
    },

    desformatearFechaColombia(fechaColombia) {
      if (!fechaColombia) return null;
      const [dia, mes, anio] = fechaColombia.split("/");
      return `${anio}-${mes}-${dia}`; // Convertir a formato "YYYY-MM-DD"
    },

    enviarNotificacionCorreo(destinatarioCorreo, asunto, mensaje) {
      axios.post('/test-email', {
        destinatario: destinatarioCorreo,
        asunto: asunto,
        mensaje: mensaje
      })
      .then(() => {
        console.log("Notificación de correo enviada correctamente.");
      })
      .catch(error => {
        console.error("Error al enviar la notificación de correo:", error);
      });
    },

    updateTotalizadores() {
      this.totalLeads = this.leads.length;
      this.totalLeadsAsignado = this.leads.filter(lead => lead.estatus === 'asignado').length;
      this.totalLeadsEnSeguimiento = this.leads.filter(lead => lead.estatus === 'en seguimiento').length;
      this.totalLeadsCerrados = this.leads.filter(lead => lead.estatus === 'cerrado').length;
      this.totalLeadsCulminadosEnVenta = this.leads.filter(lead => lead.estatus === 'culmina en venta').length;
      this.totalTestDrive = this.leads.filter(lead => lead.test_drive === 'Si').length; // Calcular el total de TestDrive
    },

    filtrarLeads() {
      // Filtrar según ambos selectores de filtro
      this.leadsFiltrados = this.leads.filter((lead) => {
        const coincideEstatus = !this.filtroEstatus || lead.estatus === this.filtroEstatus;
        const coincideTestDrive = !this.filtroTestDrive || lead.test_drive === this.filtroTestDrive;
        return coincideEstatus && coincideTestDrive;
      });

      // Reiniciar la navegación y asignar el primer lead que cumple el filtro
      this.currentIndex = 0;
      this.leadActual = this.leadsFiltrados[this.currentIndex] || null;
    },

    async consultarRNE() {
      if (!this.leadActual) return;
      const { telefono, correo } = this.leadActual;
      const vendedorId = localStorage.getItem("vendedor_actual"); // Asegúrate de tomar el vendedor_id del almacenamiento

      this.loading = true; // Activar indicador de carga
      try {
        const response = await axios.post('/consultar-rne', {
          telefono,
          correo,
          vendedor_id: vendedorId // Enviar vendedor_id junto con la consulta
        });
        this.resultadosRNE = response.data;
      } catch (error) {
        console.error("Error al consultar el RNE:", error);
        alert("Error al consultar el RNE.");
      } finally {
        this.loading = false; // Desactivar indicador de carga
      }
    },


    leadAnterior() {
      this.resultadosRNE = null; // Limpiar resultados al cambiar de lead
      if (this.currentIndex > 0) {
        this.currentIndex--;
        this.leadActual = this.leadsFiltrados[this.currentIndex];
      }
    },
    leadSiguiente() {
      this.resultadosRNE = null; // Limpiar resultados al cambiar de lead
      if (this.currentIndex < this.leadsFiltrados.length - 1) {
        this.currentIndex++;
        this.leadActual = this.leadsFiltrados[this.currentIndex];
      }
    },
    habilitarEdicion() {
      this.editMode = true;
    },
    guardarCambios() {
      const leadParaGuardar = {
        ...this.leadActual,
        fecha_lead: this.desformatearFechaColombia(this.leadActual.fecha_lead) // Convertir al formato ISO para backend
      };

      axios.post('/update-lead', leadParaGuardar)
        .then(() => {
          alert('Cambios guardados exitosamente');
          this.editMode = false;

          const index = this.leads.findIndex(lead => lead.id === this.leadActual.id);
          if (index !== -1) {
            this.leads.splice(index, 1, { ...this.leadActual });
          }
          this.updateTotalizadores();
          this.asignarNuevoLead();
        })
        .catch(error => {
          console.error("Error al guardar los cambios:", error);
        });
    },

    asignarNuevoLead() {
      // Verificar si el vendedor está en línea antes de asignar un nuevo lead
      if (!this.enLinea) {
          console.log("El vendedor está fuera de línea. No se asignará un nuevo lead.");
          return;
      }
      
      console.log("Solicitando asignación de un nuevo lead...");
      
      // Verificar si ya hay un lead asignado antes de solicitar uno nuevo
      const leadAsignado = this.leads.find(lead => lead.estatus === "asignado");
      
      if (leadAsignado) {
        console.log("El vendedor ya tiene un lead asignado. No se solicitará otro lead.");
        return;
      }

      axios.post(`/asignar-lead`, { vendedor_id: this.vendedorId })
        .then(response => {
          console.log("Respuesta del backend:", response.data);
          const nuevoLead = response.data.lead_asignado;
          if (nuevoLead) {
            nuevoLead.estatus = "asignado";
            nuevoLead.test_drive = nuevoLead.test_drive || "No"; // Establece "No" si está vacío
            this.leads.unshift(nuevoLead);
            this.currentIndex = 0;
            this.leadActual = this.leads[this.currentIndex];
            this.updateTotalizadores();
            alert("¡Nuevo lead asignado! Revisa los detalles del lead en la lista."); // Mostrar una alerta en pantalla
            console.log("Nuevo lead recibido:", nuevoLead);  // Agregamos un log para ver el lead recibido
          } else {
            console.log("No hay nuevos leads para asignar en este momento.");
          }
        })
        .catch(error => {
          console.error("Error al asignar el nuevo lead:", error.response ? error.response.data : error);
        });
    },

    toggleEnLinea() {
      this.enLinea = !this.enLinea;

      axios.post(`/update-vendedor-estado`, {
        vendedor_id: this.vendedorId,
        estado: this.enLinea
      }).then(() => {
        console.log(`Estado del vendedor ${this.enLinea ? 'En línea' : 'Fuera de línea'}`);

        if (this.enLinea) {
          const leadAsignado = this.leads.find(lead => lead.estatus === "asignado"); // Verificar si ya tiene un lead asignado

          if (!leadAsignado) {
            this.asignarNuevoLead();
          } else {
            alert("Ya tiene un lead asignado. Por favor, termine de trabajar en ese lead antes de recibir uno nuevo.");
          }
        }
      }).catch(error => console.error("Error al actualizar el estado del vendedor:", error));
    },
    //función para marcar fuera de línea antes de cerrar la ventana
    marcarFueraDeLinea() {
      if (this.enLinea) {
        axios.post(`/update-vendedor-estado`, {
          vendedor_id: this.vendedorId,
          estado: false
        })
        .then(() => {
          console.log("Vendedor marcado como fuera de línea antes de cerrar la ventana.");
        })
        .catch(error => {
          console.error("Error al marcar al vendedor como fuera de línea:", error);
        });
      }
    }


  },
  
  
  created() {

    this.consultarLeads();
    window.addEventListener("beforeunload", this.marcarFueraDeLinea);
    this.iniciarPing();  // Inicia el "ping"
  },

  beforeUnmount() {
    window.removeEventListener("beforeunload", this.marcarFueraDeLinea);
    this.detenerPing();  // Detiene el "ping" cuando se desmonta

  },

  components: {
    BotonesGlobalesSalir
  }
};
</script>

<style scoped>
.welcome-message {
  text-align: left;
  font-size: 1.2em;
  color: #333;
  margin: 10px 0 20px;
}

.position-indicator {
  margin: 0 15px; /* Ajusta el margen horizontal según tu preferencia */
}

.total-box {
  padding: 10px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
}

.form-leads {
  margin-top: 20px;
}

.form-leads .row .form-group {
  margin-bottom: 15px;
}

textarea {
  resize: none;
  min-height: 100px;
}

button {
  cursor: pointer;
}

.btn-toggle {
    width: 640px; /* Ajustar este valor según el tamaño deseado */
    height: 50px; /* Aumentar la altura del botón */
    font-size: 1.2em; /* Esto hace el Tamaño de texto más grande */
    font-weight: bold; /* Texto en negrita */
}

/* Estilos para la tabla de totalizadores */
.row.text-center .card {
  background-color: #e9ecef;
  border-radius: 10px;
}

/* Ajustar el ancho de las columnas para una misma línea */
.row.text-center .col-md-2 {
  min-width: 150px;
}

.total-card {
  min-width: 150px; /* Establece un tamaño mínimo uniforme */
  min-height: 120px; /* Establece un alto mínimo uniforme */
  display: flex;
  align-items: center; /* Alineación vertical */
  justify-content: center; /* Alineación horizontal */
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
  padding: 10px;
  margin: auto;
}

/* Estilos para la tabla de Leads */
.leads-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.leads-table th,
.leads-table td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
}

.leads-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.leads-table td input,
.leads-table td select,
.leads-table td textarea {
  width: 100%;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
