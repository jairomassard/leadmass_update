<template>
    <div id="lead-expert" class="container mt-4">
      <!-- Imagen de encabezado -->
      <div class="header-image">
        <img src="/images/cabezote.jpg" alt="Cabezote" class="img-fluid w-100" />
      </div>
        
      <h1 class="text-center mt-5 mb-4">Formulario de Registro de Leads</h1>
  
      <!-- Contador de leads capturados hoy -->
    <div class="contador-leads">
      <h4>Leads registrados hoy: {{ leadsCapturadosHoy }}</h4>
    </div>

      <!-- Formulario para captura de leads -->
      <div class="form-leads">
        <div class="row g-3">
          <div class="col-md-6">
            <label for="nombres" class="form-label">Nombres</label>
            <input type="text" v-model="lead.nombres" class="form-control" required />
          </div>
          <div class="col-md-6">
            <label for="apellidos" class="form-label">Apellidos</label>
            <input type="text" v-model="lead.apellidos" class="form-control" required />
          </div>
  
          <div class="col-md-4">
            <label for="identificacion" class="form-label">Identificación</label>
            <input type="text" v-model="lead.identificacion" class="form-control" />
          </div>
          <div class="col-md-4">
            <label for="telefono" class="form-label">Teléfono</label>
            <input type="text" v-model="lead.telefono" class="form-control" />
          </div>
          <div class="col-md-4">
            <label for="correo" class="form-label">Correo Electrónico</label>
            <input type="email" v-model="lead.correo" class="form-control" />
          </div>
  
          <div class="col-md-4">
            <label for="direccion" class="form-label">Dirección</label>
            <input type="text" v-model="lead.direccion" class="form-control" />
          </div>
          <div class="col-md-4">
            <label for="ciudad" class="form-label">Ciudad</label>
            <input type="text" v-model="lead.ciudad" class="form-control" />
          </div>
  
          <div class="col-md-4">
            <label for="marca" class="form-label">Marca de Interés</label>
            <select v-model="lead.marca_interes" class="form-select">
              <option disabled value="">Selecciona una marca</option>
              <option v-for="marca in marcasDisponibles" :key="marca" :value="marca">
                {{ marca }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label for="modelo_interesado" class="form-label">Modelo Interesado</label>
            <input type="text" v-model="lead.modelo_interesado" class="form-control" />
          </div>
          <div class="col-md-4">
            <label for="origen_lead" class="form-label">Origen del Lead</label>
            <input type="text" v-model="lead.origen_lead" class="form-control" placeholder="Evento" />
          </div>
          <div class="col-md-4">
            <label for="habeas_data" class="form-label">Habeas Data</label>
            <select v-model="lead.habeas_data" class="form-select" required>
                <option disabled value="">Seleccione una opción</option>
                <option value="Si">Si</option>
                <option value="No">No</option>
            </select>
            </div>
        </div>



  
        <!-- Botones de guardar y limpiar -->
        <div class="text-center mt-4">
          <button @click="guardarLead" class="btn btn-success me-3">Guardar</button>
          <button @click="limpiarCampos" class="btn btn-secondary">Limpiar Campos</button>
        </div>
  
        <!-- Botón de salir -->
        <div class="text-center mt-4">
          <BotonesGlobalesSalir />
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from '../axios';
  import BotonesGlobalesSalir from './BotonesGlobalesSalir.vue';
  

  export default {
  data() {
    return {
      lead: {
        nombres: "",
        apellidos: "",
        identificacion: "",
        telefono: "",
        direccion: "",
        ciudad: "",
        correo: "",
        fecha_lead: this.obtenerFechaActual(),
        origen_lead: "Evento", // Valor predeterminado
        marca_interes: "",
        modelo_interesado: "",
        estatus: "nuevo",  // Valor predeterminado para estatus
      },
      marcasDisponibles: [
        'Mercedez-benz', 'Range Rover', 'Defender', 'Discovery', 'Jaguar',
        'DFSK', 'Seres', 'Subaru', 'Citroen', 'DS Automóviles', 'Suzuki',
        'Develon', 'Dieci', 'Hino', 'Mack', 'Hangcha', 'Komatsu', 'Linde',
        'Still', 'XCMG', 'JAC', 'Great Wall'
      ],
      leadsCapturadosHoy: 0  // Nuevo contador
    };
  },
  mounted() {
  this.contarLeadsHoy();
  },
  methods: {
    obtenerFechaActual() {
      return axios.get('/get-current-time')
      .then(response => response.data.date)
      .catch(error => {
        console.error("Error al obtener la fecha actual:", error);
        return ""; // Devuelve un valor vacío en caso de error
      });
    },
    contarLeadsHoy() {
        const userId = localStorage.getItem('id_usuario');
        if (!userId) {
            alert("No se encontró el usuario. Por favor, inicie sesión nuevamente.");
            return;
        }

        axios.get(`/get-leads-count-expert?user_id=${userId}`)
            .then(response => {
            this.leadsCapturadosHoy = response.data.count;
            })
            .catch(error => {
            console.error("Error al obtener la cantidad de leads de hoy:", error);
            });
    },
    async guardarLead() {
      if (this.lead.habeas_data !== "Si") {
         alert("Para capturar este lead, la opción de Habeas Data debe estar marcada como 'Si'.");
         return;
      }  
      const userId = localStorage.getItem('id_usuario');
      if (!userId) {
        alert("No se encontró el usuario. Por favor, inicie sesión nuevamente.");
        return;
      }

      try {
        const fechaActual = await this.obtenerFechaActual();
        const nuevoLead = {
          ...this.lead,
          fecha_lead: fechaActual,
          estatus: "nuevo",
          capturado_por: userId,
        };

        await axios.post("/add-lead", nuevoLead);
        alert("Lead guardado exitosamente.");
        this.limpiarCampos();
        this.contarLeadsHoy(); // Actualizar el contador después de guardar
      } catch (error) {
        console.error("Error al guardar el lead:", error);
        alert("Hubo un error al guardar el lead.");
      }
    },
    async limpiarCampos() {
      try {
        const fechaActual = await this.obtenerFechaActual();
        this.lead = {
          nombres: "",
          apellidos: "",
          identificacion: "",
          telefono: "",
          direccion: "",
          ciudad: "",
          correo: "",
          fecha_lead: fechaActual,
          origen_lead: "Evento",
          marca_interes: "",
          modelo_interesado: "",
          estatus: "nuevo"  // Reestablece el estatus a "nuevo"
        };
      } catch (error) {
        console.error("Error al obtener la fecha actual:", error);
      }
    },
  },
  components: {
    BotonesGlobalesSalir
  }
};
  </script>
  
  <style scoped>
  .contador-leads {
  margin-bottom: 15px;
}
  .form-leads {
    margin-top: 20px;
  }
  
  button {
    cursor: pointer;
  }
  
  .btn-success, .btn-secondary {
  width: 150px;
  }
  
  
  label {
    font-weight: bold;
  }
  
  h1 {
    color: #333;
    font-size: 1.5em;
    text-align: center;
  }
  </style>
  