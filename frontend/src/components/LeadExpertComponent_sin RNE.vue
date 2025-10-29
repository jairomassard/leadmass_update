<template>
  <div id="lead-expert" class="container mt-4">
    <!-- Imagen de encabezado -->
    <div class="header-image">
      <img src="/images/cabezote.jpg" alt="Cabezote" class="img-fluid w-100" />
    </div>

    <h1 class="text-center mt-5 mb-4">Formulario de Registro de Leads</h1>

    <!-- Contador de leads capturados hoy -->
    <div class="contador-leads text-center mb-4">
      <h4>Leads registrados hoy: {{ leadsCapturadosHoy }}</h4>
    </div>

    <!-- Formulario para captura de leads -->
    <div class="form-leads">
      <div class="row g-3">
        <!-- Primera fila -->
        <div class="col-md-6">
          <label for="nombres" class="form-label">Nombres</label>
          <input type="text" v-model="lead.nombres" class="form-control" required />
        </div>
        <div class="col-md-6">
          <label for="apellidos" class="form-label">Apellidos</label>
          <input type="text" v-model="lead.apellidos" class="form-control" required />
        </div>

        <!-- Segunda fila -->
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

        <!-- Tercera fila -->
        <div class="col-md-4">
          <label for="direccion" class="form-label">Dirección</label>
          <input type="text" v-model="lead.direccion" class="form-control" />
        </div>
        <div class="col-md-4">
          <label for="ciudad" class="form-label">Ciudad</label>
          <input type="text" v-model="lead.ciudad" class="form-control" />
        </div>
        <div class="col-md-4">
          <label for="origen_lead" class="form-label">Origen del Lead</label>
          <input type="text" v-model="lead.origen_lead" class="form-control" placeholder="Evento" />
        </div>

        <!-- Cuarta fila -->
        <div class="col-md-6">
          <label for="marca" class="form-label">Marca de Interés</label>
          <select v-model="lead.marca_interes" class="form-select">
            <option disabled value="">Selecciona una marca</option>
            <option v-for="marca in marcasDisponibles" :key="marca" :value="marca">
              {{ marca }}
            </option>
          </select>
        </div>
        <div class="col-md-6">
          <label for="modelo_interesado" class="form-label">Modelo Interesado</label>
          <input type="text" v-model="lead.modelo_interesado" class="form-control" />
        </div>

        <!-- Quinta fila -->
        <div class="col-md-6">
          <label for="habeas_data" class="form-label">Habeas Data</label>
          <select v-model="lead.habeas_data" class="form-select" required>
            <option disabled value="">Seleccione una opción</option>
            <option value="Si">Si</option>
            <option value="No">No</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">Autorización de Tratamiento de Datos:</label>
          <select v-model="lead.aceptacion_tratamiento_datos" class="form-select" required>
            <option disabled value="">Seleccione una opción</option>
            <option value="Si">Sí</option>
            <option value="No">No</option>
          </select>
          <small class="text-muted">
            <a href="https://drive.google.com/file/d/1Rpa3i4vL46cfTy8yRntNj3Fwrn0vnPpz/view?usp=sharing" target="_blank">
              Ver términos de autorización
            </a>
          </small>
        </div>

        <!-- Firma digital -->
        <div class="col-md-12 mt-4">
          <label for="firma_digital" class="form-label">Firma Digital</label>
          <div class="signature-pad-container border border-secondary rounded" style="width: 300px; height: 150px; background-color: #f8f9fa; margin: auto;">
            <canvas ref="signaturePad" style="display: block; width: 100%; height: 100%;"></canvas>
          </div>
          <button @click="limpiarFirma" class="btn btn-secondary mt-2">Limpiar Firma</button>
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
        habeas_data: "",
        aceptacion_tratamiento_datos: "",
        estatus: "nuevo",  // Valor predeterminado para estatus
      },
      marcasDisponibles: [
        'Mercedez-benz', 'Range Rover', 'Defender', 'Discovery', 'Jaguar',
        'DFSK', 'Seres', 'Subaru', 'Citroen', 'DS Automóviles', 'Suzuki',
        'Develon', 'Dieci', 'Hino', 'Mack', 'Hangcha', 'Komatsu', 'Linde',
        'Still', 'XCMG', 'JAC', 'Great Wall'
      ],
      leadsCapturadosHoy: 0,  // Nuevo contador
      isDrawing: false, // Estado del dibujo
      ctx: null, // Contexto del canvas
      lastPos: { x: 0, y: 0 }, // Última posición del puntero
    };
  },
  mounted() {
    this.contarLeadsHoy();
    this.inicializarFirma(); // Inicializa el canvas para la firma
  },
  methods: {
    inicializarFirma() {
      const canvas = this.$refs.signaturePad;
      this.ctx = canvas.getContext("2d");

      // Fijar dimensiones del canvas
      canvas.width = 300; // Ancho en píxeles
      canvas.height = 150; // Alto en píxeles

      // Configurar estilo del pincel
      this.ctx.strokeStyle = "black";
      this.ctx.lineWidth = 2;

      // Configurar eventos del canvas
      canvas.addEventListener("mousedown", this.iniciarDibujo);
      canvas.addEventListener("mousemove", this.dibujar);
      canvas.addEventListener("mouseup", this.terminarDibujo);
      canvas.addEventListener("mouseout", this.terminarDibujo);
      canvas.addEventListener("touchstart", this.iniciarDibujo);
      canvas.addEventListener("touchmove", this.dibujar);
      canvas.addEventListener("touchend", this.terminarDibujo);
    },
    iniciarDibujo(event) {
      event.preventDefault();
      const pos = this.obtenerPosicion(event);
      this.isDrawing = true;
      this.lastPos = pos;
    },
    dibujar(event) {
      event.preventDefault();
      if (!this.isDrawing) return;

      const pos = this.obtenerPosicion(event);
      this.ctx.beginPath();
      this.ctx.moveTo(this.lastPos.x, this.lastPos.y);
      this.ctx.lineTo(pos.x, pos.y);
      this.ctx.stroke();
      this.lastPos = pos;
    },
    terminarDibujo(event) {
      event.preventDefault();
      this.isDrawing = false;
    },
    obtenerPosicion(event) {
      const canvas = this.$refs.signaturePad;
      const rect = canvas.getBoundingClientRect();

      // Manejar posición para touch o mouse
      if (event.touches && event.touches[0]) {
        return {
          x: event.touches[0].clientX - rect.left,
          y: event.touches[0].clientY - rect.top,
        };
      } else {
        return {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
        };
      }
    },
    limpiarFirma() {
      const canvas = this.$refs.signaturePad;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    },
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
      // Validación de autorizaciones
      if (this.lead.habeas_data !== "Si" || this.lead.aceptacion_tratamiento_datos !== "Si") {
        alert("Debes aceptar tanto el Habeas Data como los términos de tratamiento de datos para guardar este lead.");
        return;
      }

      // Validación del usuario
      const userId = localStorage.getItem('id_usuario');
      if (!userId) {
        alert("No se encontró el usuario. Por favor, inicie sesión nuevamente.");
        return;
      }

      try {
        const canvas = this.$refs.signaturePad;
        const firmaDigital = canvas.toDataURL(); // Obtener imagen en Base64

        // Crear el objeto de lead con los datos actualizados
        const nuevoLead = {
          ...this.lead,
          firma_digital: firmaDigital,
          fecha_lead: await this.obtenerFechaActual(),
          estatus: "nuevo",
          capturado_por: userId,
        };

        // Enviar el lead al backend
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
          habeas_data: "",
          aceptacion_tratamiento_datos: "",
          estatus: "nuevo"  // Reestablece el estatus a "nuevo"
        };
        this.limpiarFirma();
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
  