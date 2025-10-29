<template>
  <div id="app" class="container mt-5">
    <!-- Título principal -->
    <h1 class="text-center mb-4">Cargue y Gestión de Leads</h1>

    <!-- Totalizadores -->
    <div v-if="totalLeads !== null" class="row text-center mb-4">
      <div class="col-md-6">
        <div class="card p-3">
          <h5>Total Leads</h5>
          <p class="display-6">{{ totalLeads }}</p>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card p-3">
          <h5>Total Leads Nuevos Sin Asignar</h5>
          <p class="display-6">{{ totalLeadsNuevosSinAsignar }}</p>
        </div>
      </div>
      
    </div>

    <!-- Botón para consultar leads -->
    <div class="text-center mb-4">
      <button class="btn btn-primary" @click="consultarLeads">Consultar Leads</button>
    </div>

    <!-- Navegación entre leads -->
    <div v-if="leadActual" class="d-flex justify-content-center align-items-center mb-4">
      <button @click="leadAnterior" class="btn btn-outline-secondary me-3">← Anterior</button>
      <span class="position-indicator mx-3 text-nowrap">
        {{ currentIndex + 1 }} de {{ leads.length }}
      </span>
      <button @click="leadSiguiente" class="btn btn-outline-secondary ms-3">Siguiente →</button>
    </div>

    <!-- Campos del lead -->
    <div v-if="leadActual" class="card p-4 mb-4">
      <h4>Información del Lead</h4>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label>Nombres</label>
          <input v-model="leadActual.nombres" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Apellidos</label>
          <input v-model="leadActual.apellidos" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Identificación</label>
          <input v-model="leadActual.identificacion" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Teléfono</label>
          <input v-model="leadActual.telefono" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Dirección</label>
          <input v-model="leadActual.direccion" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Ciudad</label>
          <input v-model="leadActual.ciudad" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Correo</label>
          <input v-model="leadActual.correo" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Fecha Lead</label>
          <input v-model="leadActual.fecha_lead" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Origen Lead</label>
          <input v-model="leadActual.origen_lead" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Marca de Interés</label>
          <input v-model="leadActual.marca_interes" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Modelo Interesado</label>
          <input v-model="leadActual.modelo_interesado" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-6 mb-3">
          <label>Estatus</label>
          <input v-model="leadActual.estatus" :disabled="!editMode" class="form-control" />
        </div>
        <div class="col-md-3 mb-3" v-if="editMode || leadActual">
          <label>Asignado</label>
          <select v-model="leadActual.asignado" :disabled="!editMode" class="form-select">
            <option :value="true">True</option>
            <option :value="false">False</option>
          </select>
        </div>
        <div class="col-md-3 mb-3">
          <label>Test Drive</label>
          <select v-model="leadActual.test_drive" :disabled="!editMode" class="form-select">
            <option value="No">No</option>
            <option value="Si">Si</option>
          </select>
        </div>
        <div class="col-md-3 mb-3">
          <label>Habeas Data</label>
          <select v-model="leadActual.habeas_data" :disabled="!editMode" class="form-select" required>
            <option value="Si">Si</option>
            <option value="No">No</option>
          </select>
        </div>
        <!-- Campo de Tratamiento de Datos -->
        <div class="col-md-3 mb-3">
          <label>Tratamiento de Datos</label>
          <select v-model="leadActual.aceptacion_tratamiento_datos" :disabled="!editMode" class="form-select" required>
            <option value="Si">Si</option>
            <option value="No">No</option>
          </select>
        </div>
      </div>
      
      <!-- Botones de edición -->
      <div class="text-center mt-3">
        <button v-if="!editMode" class="btn btn-warning" @click="habilitarEdicion">Editar</button>
        <button v-if="editMode" class="btn btn-success" @click="guardarCambios">Guardar</button>
      </div>
    </div>

    <!-- Botón para agregar nuevo lead -->
    <div class="text-center mb-4">
      <button class="btn btn-secondary" @click="nuevoLead">Nuevo Lead</button>
    </div>

    <!-- Cargar leads desde archivo -->
    <div class="card p-4 mb-4">
      <h4>Cargar Leads desde archivo</h4>
      <input type="file" class="form-control mb-3" @change="seleccionarArchivo" />
      <button class="btn btn-primary" @click="cargarLeadsDesdeArchivo">Cargar desde archivo</button>
    </div>

    <!-- Botón para descargar archivo modelo -->
    <div class="text-center mb-4">
      <button class="btn btn-info" @click="descargarPlantilla">Descargar Archivo Plantilla Modelo</button>
      <p class="mt-2">Descargar y modificar contenido del archivo modelo. Seguir la estructura y no cambiar el orden de las columnas.</p>
    </div>

    <BotonesGlobales />
  </div>
</template>

<script>
import axios from '../axios';
import BotonesGlobales from './BotonesGlobales.vue';

export default {
  name: "LeadsComponent",
  data() {
    return {
      leads: [],
      currentIndex: 0,
      leadActual: null,
      editMode: false,
      archivo: null,
      totalLeads: null,
      totalLeadsNuevosSinAsignar: null
    };
  },
  methods: {
    consultarLeads() {
      axios.get('/get-leads')
        .then(response => {
          this.leads = response.data;
          this.leadActual = this.leads[this.currentIndex];
          this.totalLeads = this.leads.length;
          this.totalLeadsNuevosSinAsignar = this.leads.filter(lead => lead.estatus === 'nuevo' && !lead.asignado).length;
        })
        .catch(error => {
          console.error("Error al obtener los leads:", error);
        });
    },
    leadAnterior() {
      if (this.currentIndex > 0) {
        this.currentIndex--;
        this.leadActual = this.leads[this.currentIndex];
      }
    },
    leadSiguiente() {
      if (this.currentIndex < this.leads.length - 1) {
        this.currentIndex++;
        this.leadActual = this.leads[this.currentIndex];
      }
    },
    habilitarEdicion() {
      this.editMode = true;
    },
    guardarCambios() {
      const usuarioId = localStorage.getItem('id_usuario'); // Recuperar el usuario_id del localStorage
      if (!usuarioId) {
        alert("Error: Sesión no válida. Por favor, inicia sesión nuevamente.");
        this.$router.push('/'); // Redirigir al login
        return;
      }

      // Incluir el usuario_id en la solicitud al backend
      axios.post('/update-lead', { ...this.leadActual, usuario_id: usuarioId })
        .then(() => {
          alert('Cambios guardados exitosamente');
          this.editMode = false;
          this.consultarLeads(); // Actualizar la lista de leads
        })
        .catch(error => {
          console.error("Error al guardar los cambios:", error.response ? error.response.data : error);
          alert("No se pudo guardar el lead.");
        });
    },
    nuevoLead() {
      this.leadActual = {
        nombres: '',
        apellidos: '',
        identificacion: '',
        telefono: '',
        direccion: '',
        ciudad: '',
        correo: '',
        fecha_lead: new Date().toISOString().split('T')[0], // Fecha actual en formato YYYY-MM-DD
        origen_lead: '',
        marca_interes: '',
        modelo_interesado: '',
        estatus: '',
        asignado: false,
        habeas_data: 'No'  // Campo predeterminado
      };
      this.editMode = true;
    },
    seleccionarArchivo(event) {
      this.archivo = event.target.files[0];
    },

    async validarArchivoAntesDeEnviar() {
        if (!this.archivo) {
            alert("Por favor, seleccione un archivo antes de cargar.");
            return false;
        }

        const contenido = await this.leerArchivo(this.archivo);

        // Dividir en filas y extraer encabezados
        const filas = contenido.split('\n').map(fila => fila.trim());
        const encabezados = filas[0].split(';').map(header => header.trim().toLowerCase());

        // Encabezados esperados
        const encabezadosEsperados = [
          'nombres',
          'apellidos',
          'identificacion',
          'telefono',
          'direccion',
          'ciudad',
          'correo',
          'fecha_lead',
          'origen_lead',
          'marca_interes',
          'modelo_interesado',
          'estatus',
          'asignado',
          'test_drive',
          'habeas_data',
          'aceptacion_tratamiento_datos'
        ];

        // Verificar si coinciden
        const faltantes = encabezadosEsperados.filter(enc => !encabezados.includes(enc));
        if (faltantes.length > 0) {
            alert(`El archivo no contiene los encabezados necesarios: ${faltantes.join(', ')}. Verifique la plantilla.`);
            return false;
        }

        // Validar cada fila (opcional, dependiendo de tu lógica)
        for (let i = 1; i < filas.length; i++) {
            if (!filas[i]) continue; // Saltar filas vacías
            const columnas = filas[i].split(';').map(col => col.trim());

            // Validar datos específicos (si es necesario)
            const fechaLead = columnas[encabezados.indexOf('fecha_lead')];
            if (fechaLead && !/^\d{4}-\d{2}-\d{2}$/.test(fechaLead)) {
                alert(`Error en la fila ${i + 1}: La fecha '${fechaLead}' no es válida. Use el formato AAAA-MM-DD.`);
                return false;
            }
        }

        return true;
    },
    leerArchivo(archivo) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = () => resolve(reader.result);
            reader.onerror = (error) => {
                console.error("Error leyendo el archivo:", error);
                alert("No se pudo leer el archivo. Verifique el formato y los permisos.");
                reject(error);
            };

            reader.readAsText(archivo, 'utf-8');
        });
    },

    async cargarLeadsDesdeArchivo() {
        const usuarioId = localStorage.getItem('id_usuario'); // Recuperar el usuario_id del localStorage
        if (!usuarioId) {
          alert("Sesión no válida. Por favor, inicia sesión nuevamente.");
          this.$router.push('/'); // Redirigir al login
          return;
        }

        const esValido = await this.validarArchivoAntesDeEnviar();
        if (!esValido) return;

        const formData = new FormData();
        formData.append('file', this.archivo);
        formData.append('usuario_id', usuarioId);

        axios.post('/upload-leads', formData)
            .then(response => {
              const { message, rechazos } = response.data;

              // Extraer información del mensaje del backend
              const leadsCargados = message.match(/Leads cargados: (\d+)/)[1];
              const leadsRechazados = message.match(/Leads rechazados: (\d+)/)[1];

              alert(
                `Resumen de la carga de leads:\n` +
                `- Leads cargados: ${leadsCargados}\n` +
                `- Leads rechazados: ${leadsRechazados}\n` +
                `-- Rechazos por Habeas Data: ${rechazos.habeas_data}\n` +
                `-- Rechazos por Tratamiento de Datos: ${rechazos.tratamiento_datos}`
              );

              this.consultarLeads(); // Actualizar la lista de leads
            })
            .catch(error => {
                if (error.response && error.response.data.error) {
                    alert(error.response.data.error); // Mostrar mensaje de error del backend
                    console.error("Error al cargar leads desde archivo:", error.response ? error.response.data : error);
                } else {
                    alert("Ocurrió un error al cargar el archivo. Intente nuevamente cargar los leads rechazados.");
                }
            });
    },
    descargarPlantilla() {
      const enlace = document.createElement('a');
      enlace.href = '/static/leads_plantilla_de_cargue.csv'; // URL relativa en local
      enlace.download = 'leads_plantilla_de_cargue.csv';
      enlace.click();
    }
  },
  components: {
    BotonesGlobales  // Aquí importamos BotonesGlobales correctamente
  }
};
</script>

<style scoped>
.container {
  max-width: 900px;
}

h1 {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.card {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.card h4 {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
}

.card p {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

button {
  width: 100%;
}

.download-template p {
  font-size: 0.9em;
  color: #555;
}

.position-indicator {
  font-size: 1em;
  font-weight: bold;
  white-space: nowrap;
}

</style>

     

