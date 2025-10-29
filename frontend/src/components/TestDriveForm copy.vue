<template>
    <div id="test-drive-form" class="container mt-4">
      <div class="header-image">
        <img src="/images/cabezote.jpg" alt="Cabezote" class="img-fluid w-100" />
      </div>
  
      <h1 class="text-center mt-5 mb-4">Formulario de Agendamiento Test Drive</h1>
  
      <div class="form-test-drive">
        <div v-if="mensajeConfirmacion" class="text-center mt-4 alert alert-success">
            {{ mensajeConfirmacion }}
            <p>Esta página se cerrará en {{ contador }} segundos...</p>
        </div>

        <div v-else>
            <div class="row g-3">
            <div class="col-md-6">
                <label for="nombres" class="form-label fw-bold">Nombres</label>
                <input type="text" v-model="lead.nombres" class="form-control" required />
            </div>
            <div class="col-md-6">
                <label for="apellidos" class="form-label fw-bold">Apellidos</label>
                <input type="text" v-model="lead.apellidos" class="form-control" required />
            </div>
    
            <div class="col-md-4">
                <label for="identificacion" class="form-label fw-bold">Identificación</label>
                <input 
                    type="text"
                    v-model="lead.identificacion"
                    class="form-control"
                    required
                    @input="validarNumeros('identificacion')"
                />
                <small v-if="errores.identificacion" class="text-danger">Debe ingresar solo números.</small>
            </div>

            <div class="col-md-4">
                <label for="telefono" class="form-label fw-bold">Celular</label>
                <input 
                    type="text"
                    v-model="lead.telefono"
                    class="form-control"
                    required
                    @input="validarNumeros('telefono')"
                />
                <small v-if="errores.telefono" class="text-danger">Debe ingresar solo números.</small>
            </div>
            <div class="col-md-4">
                <label for="correo" class="form-label fw-bold">Correo Electrónico</label>
                <input type="email" v-model="lead.correo" class="form-control" required />
            </div>
    
            <div class="col-md-6">
                <label for="ciudad" class="form-label fw-bold">Ciudad</label>
                <select v-model="lead.ciudad" class="form-select" required>
                <option disabled value="">Selecciona una Ciudad</option>
                <option v-for="ciudad in ciudades" :key="ciudad" :value="ciudad">{{ ciudad }}</option>
                </select>
            </div>
    
            <div class="col-md-6">
                <label for="marca" class="form-label fw-bold">Marca de Interés</label>
                <select v-model="lead.marca_interes" class="form-select" required>
                <option disabled value="">Selecciona una marca</option>
                <option value="Subaru">Subaru</option>
                <option value="Suzuki">Suzuki</option>
                <option value="Citroen">Citroen</option>
                <option value="Great Wall">Great Wall</option>
                </select>
            </div>
    
            <div class="col-md-8">
                <label class="form-label fw-bold">Autorización de Tratamiento de Datos y Habeas Data:</label>
                <select v-model="lead.habeas_data" class="form-select" required>
                <option disabled value="">Seleccione una opción</option>
                <option value="Si">Si</option>
                <option value="No">No</option>
                </select>
                <small class="text-muted">
                <a :href="obtenerEnlaceAutorizacion()" target="_blank" @click="marcarVisitaEnlace">
                    Ver términos de autorización
                </a>
                </small>
            </div>
            </div>
    
            <div class="mensaje-legal mt-3 p-2 border rounded">
            <p class="fw-bold">Consideraciones legales:</p>
            <p>1. El registro no garantiza la disponibilidad del vehículo para pruebas.</p>
            <p>2. Los vehículos se entregan en Bogotá en la sede Morato.</p>
            <p>3. Otros términos y condiciones aplican.</p>
            </div>
    
            <!-- Botón Guardar y Salir con animación -->
            <div class="text-center mt-4">
            <button @click="guardarLead" class="btn btn-success" :disabled="!formularioCompleto || procesando">
                <span v-if="procesando">
                <i class="spinner-border spinner-border-sm"></i> Guardando...
                </span>
                <span v-else>Guardar y Salir</span>
            </button>
            </div>
    

        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from '../axios';
  
  export default {
    data() {
      return {
        lead: {
          nombres: "",
          apellidos: "",
          identificacion: "",
          telefono: "",
          correo: "",
          ciudad: "",
          marca_interes: "",
          habeas_data: "",
          aceptacion_tratamiento_datos: "Si", // Se envía junto con habeas_data
            origen_lead: "Canal digital" // Valor fijo
        },
        marcasDisponibles: ["Subaru", "Suzuki", "Citroen", "Great Wall"],
        ciudades: ["Bogotá y Municipios Cercanos"],  // para mas ciudades poner: , "Medellín"
        mensajeConfirmacion: "",
        contador: 10,
        enlaceVisitado: false, // Variable para rastrear si hizo clic en el enlace
        procesando: false, // ✅ Estado para evitar doble envío
        errores: {
            identificacion: false,
            telefono: false
        }
      };
    },
    computed: {
      formularioCompleto() {
        return (
          this.lead.nombres &&
          this.lead.apellidos &&
          this.lead.identificacion &&
          this.lead.telefono &&
          this.lead.correo &&
          this.lead.ciudad &&
          this.lead.marca_interes &&
          this.lead.habeas_data === "Si" &&
          this.enlaceVisitado // Ahora el usuario debe visitar el enlace
        );
      }
    },
    methods: {
      obtenerEnlaceAutorizacion() {
        if (this.lead.marca_interes === "Subaru" || this.lead.marca_interes === "Citroen") {
          return "https://www.binariamedia.co";
        } else if (this.lead.marca_interes === "Suzuki" || this.lead.marca_interes === "Great Wall") {
          return "https://www.iqspaces.com.co";
        }
        return "#";
      },
      marcarVisitaEnlace() {
        this.enlaceVisitado = true; // Se marca como visitado cuando hace clic
      },
      validarNumeros(campo) {
        if (this.lead && this.lead[campo]) {
            this.lead[campo] = this.lead[campo].replace(/\D/g, ""); // Elimina cualquier letra ingresada
            this.errores[campo] = isNaN(Number(this.lead[campo])) || this.lead[campo].trim() === ""; // Verifica si hay caracteres no numéricos
        }
      },
      async guardarLead() {
        if (!this.formularioCompleto || this.procesando) {
            alert("Debe completar todos los campos, aceptar la Autorización de Tratamiento de Datos y Habeas Data y hacer click en su enlace para continuar.");
            return;
        }


        // Mapeo de ciudades antes de enviar el formulario
        let ciudadEnviar = this.lead.ciudad;
        if (ciudadEnviar === "Bogotá y Municipios Cercanos") ciudadEnviar = "Bogota";

        const leadEnviar = {
            ...this.lead,
            ciudad: ciudadEnviar,
            aceptacion_tratamiento_datos: "Si", // Enviar campo separado
        };

        this.procesando = true; // ✅ Evita doble envío
        try {
            await axios.post("/add-lead-test-drive", leadEnviar);
            this.mensajeConfirmacion = "Datos para inscripción guardados con éxito!";
            this.iniciarCuentaRegresiva();
        } catch (error) {
            console.error("Error al guardar el lead:", error.response || error);
            alert("Error al guardar el lead. Intente nuevamente.");
        } finally {
            this.procesando = false; // ✅ Habilitar nuevamente el botón después de la respuesta
        }
      },

      iniciarCuentaRegresiva() {
        let interval = setInterval(() => {
          this.contador--;
          if (this.contador === 0) {
            clearInterval(interval);
            window.location.href = "about:blank"; // Cierra la pestaña en navegadores modernos
          }
        }, 1000);
      }
    }
  };
  </script>
  
  <style scoped>
  .mensaje-legal {
    background-color: #f8f9fa;
    font-size: 0.9rem;
  }
  .fw-bold {
    font-weight: bold;
  }
  .spinner-border {
    vertical-align: middle;
    margin-right: 5px;
    }
  </style>
  
  