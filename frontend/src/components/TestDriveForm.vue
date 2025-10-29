<template>
    <div id="test-drive-form" class="container mt-4">
      <div class="header-image">
        <img src="/images/cabezote.jpg" alt="Cabezote" />
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
    
            <div class="col-md-4">
                <label for="ciudad" class="form-label fw-bold">Ciudad</label>
                <select v-model="lead.ciudad" class="form-select" required>
                <option disabled value="">Selecciona una Ciudad</option>
                <option v-for="ciudad in ciudades" :key="ciudad" :value="ciudad">{{ ciudad }}</option>
                </select>
            </div>
    
            <div class="col-md-4">
                <label for="marca" class="form-label fw-bold">Marca de Interés</label>
                <select v-model="lead.marca_interes" class="form-select">
                    <option disabled value="">Selecciona una marca</option>
                    <option v-for="marca in marcasDisponibles" :key="marca" :value="marca">
                    {{ marca }}
                    </option>
                </select>
            </div>
            <div class="col-md-4">
                <label for="modelo_interesado" class="form-label fw-bold">Modelo Interesado</label>
                <select v-model="lead.modelo_interesado" class="form-select" required>
                    <option disabled value="">Selecciona un modelo</option>
                    <option v-for="modelo in modelosFiltrados" :key="modelo" :value="modelo">
                    {{ modelo }}
                    </option>
                </select>
            </div>
    
            <div class="col-md-8">
                <label class="form-label fw-bold">Autorización de Tratamiento de Datos y Habeas Data:   </label>
                <div class="form-check form-check-inline">
                  <input 
                    type="checkbox" 
                    v-model="lead.habeas_data_si" 
                    id="habeas_data_si" 
                    class="form-check-input" 
                    :value="true"
                    @change="actualizarHabeasData"
                  />
                  <label for="habeas_data_si" class="form-check-label">Sí</label>
                </div>
                <div class="form-check form-check-inline">
                  <input 
                    type="checkbox" 
                    v-model="lead.habeas_data_no" 
                    id="habeas_data_no" 
                    class="form-check-input" 
                    :value="true"
                    @change="actualizarHabeasData"
                  />
                  <label for="habeas_data_no" class="form-check-label">No</label>
                </div>
                <small class="text-muted d-block mt-1">
                  <a :href="obtenerEnlaceAutorizacion()" target="_blank" @click="marcarVisitaEnlace">
                    Ver términos de autorización
                  </a>
                </small>
              </div>
            </div>
    
            <div class="mensaje-legal mt-3 p-2 border rounded">
            <p class="fw-bold">Consideraciones legales:</p>
            <p>1. Este agendamiento de test drive incluye préstamo de un vehículo  seleccionado por el cliente en la ciudad de Bogotá, en los concesionarios de Inchcape: Morato, Usaquén, Avda. Chile, Calle 13, Avda Boyacá y Centro Mayor; de acuerdo con el listado de Vehículos disponibles para test drive al momento de hacer el agendamiento  en la fecha que el cliente desee hacerlo, previa reservación y cuya duración es de 1 día contado a partir de la firma de un contrato de comodato. Para tal fin debe ser mayor de 18 años, presentar cédula de ciudadanía original,  residir en Colombia, pase | licencia de conducción  colombiano y vigente; diligenciar, firmar y aceptar el formato de exoneración y formato de check list entrega del vehículo.</p>
            <p>2. El cliente deberá aceptar la política y tratamiento de datos y habeas data al momento de diligenciar el formato y no tener restricción de contactabilidad en el RNE (Registo Nacional de Excluidos) de la CRC (Comisión de Regulación de Comunicaciones).</p>
            
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
          habeas_data_si: false, // Nuevo campo para el checkbox "Sí"
          habeas_data_no: false, // Nuevo campo para el checkbox "No"
          aceptacion_tratamiento_datos: "Si", // Se envía junto con habeas_data
            origen_lead: "Canal digital" // Valor fijo
        },
        marcasDisponibles: ["KGM"],
        // Lista de modelos organizados por marca
        modelosPorMarca: {
            "KGM": ["TIVOLI", "KORANDO", "REXTON", "REXTON SPORTS", "TORRES", "TORRES EVX", "ACTYON"],
            
        },
        ciudades: ["Bogotá y Municipios Cercanos"],  // para mas ciudades poner: , "Medellín"
        mensajeConfirmacion: "",
        contador: 15,
        enlaceVisitado: false, // Variable para rastrear si hizo clic en el enlace
        procesando: false, // ✅ Estado para evitar doble envío
        errores: {
            identificacion: false,
            telefono: false
        }
      };
    },
    computed: {
      modelosFiltrados() {
        return this.lead.marca_interes ? this.modelosPorMarca[this.lead.marca_interes] || [] : [];
        },
      formularioCompleto() {
        return (
          this.lead.nombres &&
          this.lead.apellidos &&
          this.lead.identificacion &&
          this.lead.telefono &&
          this.lead.correo &&
          this.lead.ciudad &&
          this.lead.marca_interes &&
          this.lead.modelo_interesado && // Aseguro que el modelo sea obligatorio
          this.lead.habeas_data_si // Solo "Sí" habilita el botón
        );
      }
    },
    watch: {
        "lead.marca_interes": function () {
            this.lead.modelo_interesado = ""; // Resetear modelo si cambia la marca
        }
    },

    methods: {
      obtenerEnlaceAutorizacion() {
        if (this.lead.marca_interes === "Subaru" || this.lead.marca_interes === "Citroen") {
          return "https://pracodidacol.com/wp-content/uploads/2020/05/JU-PO-02__POLITICA-INSTITUCIONAL-DE-TRATAMIENTO-Y-USO-DE-DATOS-E-INFORMACION-PERSONAL_1724169415.docx-f-f-f-f.pdf";
        } else if (this.lead.marca_interes === "Suzuki" || this.lead.marca_interes === "Great Wall") {
          return "https://derco.com.co/wp-content/uploads/2024/09/JU-PO-02-POLITICA-INSTITUCIONAL-DE-TRATAMIENTO-Y-USO-DE-DATOS-E-INFORMACION-PERSONAL_1724169415.docx-f-f-f-f.pdf";
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
      actualizarHabeasData() {
        // Aseguro que solo uno esté seleccionado a la vez y actualizo habeas_data
        if (this.lead.habeas_data_si && this.lead.habeas_data_no) {
          this.lead.habeas_data_no = false; // Si "Sí" está seleccionado, desactivo "No"
        }
        this.lead.habeas_data = this.lead.habeas_data_si ? "Si" : (this.lead.habeas_data_no ? "No" : "");
      },
      async guardarLead() {
        if (!this.formularioCompleto || this.procesando) {
            alert("Debe completar todos los campos, aceptar la Autorización de Tratamiento de Datos y Habeas Data y hacer click para visitar su enlace para continuar.");
            return;
        }


        // Mapeo de ciudades antes de enviar el formulario
        let ciudadEnviar = this.lead.ciudad;
        if (ciudadEnviar === "Bogotá y Municipios Cercanos") ciudadEnviar = "Bogota";

        const leadEnviar = {
            ...this.lead,
            ciudad: ciudadEnviar,
            aceptacion_tratamiento_datos: "Si", // Enviar campo separado
            habeas_data: this.lead.habeas_data // Envío el valor procesado
        };

        this.procesando = true; // ✅ Evita doble envío
        try {
            await axios.post("/add-lead-test-drive", leadEnviar);
            this.mensajeConfirmacion = "Gracias por registrarte para vivir esta experiencia de Test Drive. Próximamente serás contactado por uno de nuestros consultores.";
            
            // Disparar el evento de conversión del Meta Pixel
            if (window.fbq) {
              fbq('track', 'CompleteRegistration', {
                content_name: 'Test Drive Registration',
                status: 'successful'
              });
            }
                      
            
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

  .header-image {
    width: 100%; /* Contenedor ocupa el ancho disponible */
  }

  .header-image img {
    width: 100%; /* Imagen ocupa el 100% del ancho del contenedor */
    height: auto; /* Mantiene la proporción original */
    display: block; /* Elimina espacios no deseados */
  } 

  @media (max-width: 576px) {
    .header-image {
      width: 100%;
      padding-bottom: 50%; /* Relación de aspecto aproximada para hacerla más alta */
      position: relative;
    }
    .header-image img {
      width: 100%;
      height: 100%; /* Llena el contenedor */
      position: absolute;
      top: 0;
      left: 0;
      object-fit: contain; /* Muestra toda la imagen sin recortarla */
    }
  }

 /* Tablets (entre 577px y 991px) */
  @media (min-width: 577px) and (max-width: 991px) {
    .header-image img {
      width: 100%;
      height: auto; /* Proporción original */
    }
  }

  /* PCs (992px en adelante) */
  @media (min-width: 992px) {
    .header-image img {
      width: 100%;
      height: auto; /* Proporción original, como estaba antes */
    }
  }

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
  
  