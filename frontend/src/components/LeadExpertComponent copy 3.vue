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
          <label for="telefono" class="form-label">Celular</label>
          <input type="text" v-model="lead.telefono" class="form-control" required/>
        </div>
        <div class="col-md-4">
          <label for="correo" class="form-label">Correo Electrónico</label>
          <input type="email" v-model="lead.correo" class="form-control" required/>
        </div>

        <!-- Tercera fila -->
        <div class="col-md-4">
          <label for="direccion" class="form-label">Dirección</label>
          <input type="text" v-model="lead.direccion" class="form-control" />
        </div>
        <div class="col-md-4">
          <label for="ciudad" class="form-label">Ciudad</label>
          <!--<input type="text" v-model="lead.ciudad" class="form-control" />  -->
          <select v-model="lead.ciudad" class="form-select" required>
            <option disabled value="">Selecciona una Ciudad</option>
            <option value="Bogota">Bogotá y alrededores</option>
            <!--<option value="Barranquilla">Barranquilla</option>
            <option value="Bucaramanga">Bucaramanga</option>
            <option value="Cali">Cali</option>
            <option value="Cartagena">Cartagena</option>
            <option value="Medellín">Medellín</option>
            <option value="Neiva">Neiva</option>
            <option value="Pereira">Pereira</option>
            <option value="Tunja">Tunja</option>
            <option value="Villavicencio">Villavicencio</option>-->
          </select>
        </div>
        <div class="col-md-4">
          <label for="origen_lead" class="form-label">Origen del Lead</label>
          <input type="text" v-model="lead.origen_lead" class="form-control" placeholder="Evento" />
        </div>

        <!-- Cuarta fila -->
        <div class="col-md-3">
          <label for="marca" class="form-label">Marca de Interés</label>
          <select v-model="lead.marca_interes" class="form-select">
            <option disabled value="">Selecciona una marca</option>
            <option v-for="marca in marcasDisponibles" :key="marca" :value="marca">
              {{ marca }}
            </option>
          </select>
        </div>
        <div class="col-md-3">
          <label for="modelo_interesado" class="form-label">Modelo Interesado</label>
          <select v-model="lead.modelo_interesado" class="form-select" required>
            <option disabled value="">Selecciona un modelo</option>
            <option value="Forester">Subaru-Forester</option>
            <option value="Evoltis">Subaru-Evoltis</option>
            <option value="Crosstrek">Subaru-Crosstrek</option>
            <option value="Outback">Subaru-Outback</option>
            <option value="WRX">Subaru-WRX</option>
            <option value="Swift">Suzuki-Swift</option>
            <option value="Baleno">Suzuki-Baleno</option>
            <option value="Grand Vitara">Suzuki-Grand Vitara</option>
            <option value="Jimny">Suzuki-Jimny</option>
            <option value="S-Cross">Suzuki-S-Cross</option>
            <option value="C3">Citroen-C3</option>
            <option value="C4 Cactus">Citroen-C4 Cactus</option>
            <option value="Aircross">Citroen-Aircross</option>
            <option value="C5 Aircross">Citroen-C5 Aircross</option>
            <option value="Tank 500">GWM-Tank 500</option>
            <option value="Tank 300">GWM-Tank 300</option>
            <option value="H6">GWM-H6</option>
            <option value="Ora">GWM-Ora</option>
            <option value="Jolion Pro">GWM-Jolion Pro</option>
            <option value="Jolion">GWM-Jolion</option>
            <option value="Poer">GWM-Poer</option>
            <option value="Wingle 5">GWM-Wingle 5</option>
            <option value="Wingle 7">GWM-Wingle 7</option>
          </select>
        </div>
        <div class="col-md-6">
          <label for="concesionario" class="form-label">Concesionario</label>   <!-- Selector de concesionario -->
          <select v-model="lead.concesionario_id" class="form-select" required>
            <option disabled value="">Seleccione un concesionario</option>
            <option v-for="concesionario in concesionarios" :key="concesionario.id" :value="concesionario.id">
              {{ concesionario.nombre_concesionario }}
            </option>
          </select>
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

        <!-- Firma digital y nuevo botón -->
        <div class="col-md-12 mt-4 d-flex justify-content-between">
          <div>
            <label for="firma_digital" class="form-label">Firma Digital</label>
            <div
              class="signature-pad-container border border-secondary rounded"
              style="width: 300px; height: 150px; background-color: #f8f9fa; margin: auto;">
              <canvas ref="signaturePad" style="display: block; width: 100%; height: 100%;"></canvas>
            </div>
            <button @click="limpiarFirma" class="btn btn-secondary mt-2">Limpiar Firma</button>
          </div>
          <!-- Botón de Consulta RNE -->
          <button
            @click="consultarRNE"
            :disabled="loading"
            :class="['btn', loading ? 'btn-secondary' : 'btn-warning']"
            style="height: 40px;">
            <span v-if="loading">
              <i class="spinner-border spinner-border-sm"></i> Consultando...
            </span>
            <span v-else>Consultar RNE</span>
          </button>
        </div>
      </div>

      <!-- Botones de guardar y limpiar -->
      <div class="text-center mt-4">
        <button @click="guardarLead" class="btn btn-success" :disabled="procesando">
          <span v-if="procesando">
            <i class="spinner-border spinner-border-sm"></i> Guardando...
          </span>
          <span v-else>Guardar</span>
        </button>
        <button @click="limpiarCampos" class="btn btn-secondary">Limpiar Campos</button>
      </div>

      <!-- Botón de salir -->
      <div class="text-center mt-4">
        <BotonesGlobalesSalir />
      </div>
    </div>

    <!-- Resultados de la consulta RNE -->
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
                <li>SMS: {{ resultadosRNE.telefono.opcionesContacto.sms ? "Sí" : "No" }}</li>
                <li>Aplicación: {{ resultadosRNE.telefono.opcionesContacto.aplicacion ? "Sí" : "No" }}</li>
                <li>Llamada: {{ resultadosRNE.telefono.opcionesContacto.llamada ? "Sí" : "No" }}</li>
              </ul>
            </td>
            <td>{{ resultadosRNE.telefono.tipo }}</td>
            <td>{{ resultadosRNE.telefono.fechaCreacion }}</td>
          </tr>
          <tr v-else>
            <td colspan="4" class="text-center">
              NO EXISTE REGISTRO PARA ESE NÚMERO TELEFÓNICO
            </td>
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
                <li>Correo Electrónico: {{ resultadosRNE.correo.opcionesContacto.correo_electronico ? "Sí" : "No" }}</li>
                <li>Aplicaciones: {{ resultadosRNE.correo.opcionesContacto.aplicacion ? "Sí" : "No" }}</li>
              </ul>
            </td>
            <td>{{ resultadosRNE.correo.fechaCreacion }}</td>
          </tr>
          <tr v-else>
            <td colspan="3" class="text-center">
              NO EXISTE REGISTRO PARA ESE CORREO
            </td>
          </tr>
        </tbody>
      </table>
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
        concesionario_id: "", // Nuevo campo para concesionario
        habeas_data: "",
        aceptacion_tratamiento_datos: "",
        estatus: "nuevo",  // Valor predeterminado para estatus
      },
      procesando: false, // ✅ Estado para evitar doble envío
      marcasDisponibles: [
        'Subaru', 'Suzuki', 'Citroen', ' Great wall'
      ],
      concesionarios: [], // Lista de concesionarios cargados desde el backend
      leadsCapturadosHoy: 0,  // Nuevo contador
      isDrawing: false, // Estado del dibujo
      ctx: null, // Contexto del canvas
      lastPos: { x: 0, y: 0 }, // Última posición del puntero
      resultadosRNE: null,
      loading: false // Controla el estado de carga del botón
    };
  },
  mounted() {
    this.contarLeadsHoy();
    this.inicializarFirma(); // Inicializa el canvas para la firma
    this.cargarConcesionarios(); // Cargar concesionarios al cargar el componente
  },
  methods: {
    async consultarRNE() {
      const { telefono, correo } = this.lead;

      if (!telefono && !correo) {
        alert("Por favor, ingrese un teléfono o un correo para realizar la consulta.");
        return;
      }


      this.loading = true; // Activar estado de carga

      try {
        const response = await axios.post("/consultar-rne-expert", { telefono, correo });
        this.resultadosRNE = response.data;
      } catch (error) {
        console.error("Error al consultar el RNE:", error);
        alert("Hubo un problema al realizar la consulta. Intente nuevamente.");
      } finally {
        this.loading = false; // Desactivar estado de carga
      }
    },
    async cargarConcesionarios() {
      try {
        const response = await axios.get('/get-concesionarios');
        this.concesionarios = response.data; // Asignar lista de concesionarios
      } catch (error) {
        console.error("Error al cargar concesionarios:", error);
        alert("No se pudieron cargar los concesionarios. Intente nuevamente.");
      }
    },
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
            localStorage.clear();
            this.$router.push('/login');
            return;
        }

        axios.get(`/get-leads-count-expert?user_id=${userId}`)
        .then(response => {
            console.log("✅ Cantidad de leads capturados hoy:", response.data.count);
            this.leadsCapturadosHoy = response.data.count;
        })
        .catch(error => {
            console.error("⚠️ Error al obtener la cantidad de leads de hoy:", error.response?.data || error);
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
        this.procesando = true; // ✅ Deshabilitar botón antes de enviar

        const canvas = this.$refs.signaturePad;
        const firmaDigital = canvas.toDataURL(); // Obtener imagen en Base64

        // Crear el objeto de lead con los datos actualizados
        const nuevoLead = {
          ...this.lead,
          concesionario_id: this.lead.concesionario_id, // Incluir concesionario seleccionado
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
      } finally {
        this.procesando = false; // ✅ Habilitar nuevamente el botón después de la respuesta
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
        this.resultadosRNE = null; // Reinicia los resultados de la consulta
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

  .spinner-border {
    vertical-align: middle;
    margin-right: 5px;
    }
</style>
  