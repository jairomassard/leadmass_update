<template>
    <div id="supervisor-leads" class="container mt-4">
      <h1 class="text-center mb-4">Gerencia y Reporte de Leads</h1>
  
      <!-- Botón para cargar contenido de la tabla -->
      <div class="text-center mb-4">
        <button class="btn btn-primary" @click="generarContenidoTabla">Generar Contenido Tabla</button>
      </div>
  
      <!-- Sección de Gráfico de Embudo y Totalizadores -->
      <div class="row mb-4">
        <!-- Gráfico de Embudo (Columna 8) -->
        <div class="col-md-8">
          <div class="chart-container d-flex justify-content-center">
            <v-chart :option="chartOptions" style="width: 100%; height: 350px;" />
          </div>
        </div>
  
        <!-- Totalizadores y Últimas Conexiones (Columna 4) -->
        <div class="col-md-4">
          <div class="totalizadores border p-3 rounded">
            <p>Total leads en sistema: <strong>{{ totalLeadsAsignados }}</strong></p>
            <p>Total leads Nuevos: <strong>{{ totalLeadsNuevos }}</strong></p>
            <p>Total leads asignados: <strong>{{ totalLeadsAsignadosEstado }}</strong></p>
            <p>Total leads en seguimiento: <strong>{{ totalLeadsEnSeguimiento }}</strong></p>
            <p>Total leads cerrados: <strong>{{ totalLeadsCerrados }}</strong></p>
            <p>Total leads culminados en venta: <strong>{{ totalLeadsCulminadosEnVenta }}</strong></p>
            <p>Total leads con Test Drive: <strong>{{ totalLeadsConTestDrive }}</strong></p>
            <p>Última conexión del vendedor: <strong>{{ tiempoUltimaConexion }}</strong></p>
            <p>Última puesta en línea: <strong>{{ ultimaPuestaOnline }}</strong></p>
          </div>
        </div>
      </div>
  
      <!-- Sección de Botones de Exportación y Acciones -->
      <div class="d-flex justify-content-center mb-4">
        <button class="btn btn-success me-2" @click="exportarReporte('pdf')">Exportar PDF</button>
        <button class="btn btn-info me-2" @click="exportarReporte('csv')">Exportar CSV</button>
        <!--<router-link to="/estado-vendedores-supervisor" class="btn btn-secondary me-2">
          Verificar Conexión Vendedores
        </router-link>
        <router-link to="/leads-expert" class="btn btn-secondary">
          Ver Leads Capturados por Expertos
        </router-link> -->
      </div> 
  
      <!-- Botón de Salir 
      <div class="navigation-buttons text-center mb-4">
        <BotonesGlobalesSalir />
      </div> -->
  
      <!-- Filtros de búsqueda -->
    <div class="filtros mb-4 row g-3" v-if="contenidoGenerado">
      <div class="col-md-6">
          <label class="form-label">Filtrar por Marca:</label>
          <select class="form-select" v-model="filtroMarca" @change="filtrarLeads">
            <option value="">Todos</option>
            <option v-for="marca in marcasDisponibles" :key="marca" :value="marca">
              {{ marca }}
            </option>
          </select>
      </div>
      <div class="col-md-6">
        <label class="form-label">Filtrar por vendedor:</label>
        <select class="form-select" v-model.number="filtroVendedor" @change="filtrarLeads">
          <option value="">Todos</option>
          <!--<option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">-->
          <option v-for="vendedor in vendedores" :key="vendedor.id" :value="String(vendedor.id)"> 
            {{ vendedor.nombre }}
          </option>
        </select>
      </div>
    </div>
    <div class="filtros mb-4 row g-3" v-if="contenidoGenerado">
      <div class="col-md-3">
        <label class="form-label">Filtrar por estado:</label>
        <select class="form-select" v-model="filtroEstado" @change="filtrarLeads">
          <option value="">Todos</option>
          <option value="nuevo">Nuevo</option>
          <option value="asignado">Asignado</option>
          <option value="en seguimiento">En Seguimiento</option>
          <option value="cerrado">Cerrado</option>
          <option value="culmina en venta">Culmina en Venta</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Filtrar por Test Drive:</label>
        <select class="form-select" v-model="filtroTestDrive" @change="filtrarLeads">
          <option value="">Todos</option>
          <option value="Si">Si</option>
          <option value="No">No</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Fecha desde:</label>
        <input type="date" class="form-control" v-model="filtroFechaDesde" @change="filtrarLeads">
      </div>
      <div class="col-md-3">
        <label class="form-label">Fecha hasta:</label>
        <input type="date" class="form-control" v-model="filtroFechaHasta" @change="filtrarLeads">
      </div>
    </div>
  
<!-- Tabla de leads -->
    <div class="table-responsive" v-if="contenidoGenerado">
      <table class="table table-bordered table-striped">
        <thead class="table-dark">
          <tr>
            <th>Vendedor</th>
            <th>Nombres</th>
            <th>Apellidos</th>
            <th>Identificación</th>
            <th>Teléfono</th>
            <th>Dirección</th>
            <th>Ciudad</th>
            <th>Correo</th>
            <th>Fecha Lead</th>
            <th>Origen Lead</th>
            <th>Marca de Interés</th>
            <th>Modelo Interesado</th>
            <th>Precio de Venta</th>
            <th>Estatus</th>
            <th>Test Drive</th>
            <th>Seguimientos</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lead in leadsFiltrados" :key="lead.id">
            <td>{{ lead.vendedor_nombre }}</td>
            <td>{{ lead.nombres }}</td>
            <td>{{ lead.apellidos }}</td>
            <td>{{ lead.identificacion }}</td>
            <td>{{ lead.telefono }}</td>
            <td>{{ lead.direccion }}</td>
            <td>{{ lead.ciudad }}</td>
            <td>{{ lead.correo }}</td>
            <td>{{ lead.fecha_lead }}</td>
            <td>{{ lead.origen_lead }}</td>
            <td>{{ lead.marca_interes }}</td>
            <td>{{ lead.modelo_interesado }}</td>
            <td>
              {{ lead.precio_venta !== undefined ? Number(lead.precio_venta).toLocaleString("es-CO", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) : "0" }}
            </td>
            <td>{{ lead.estatus }}</td>
            <td>{{ lead.test_drive }}</td>
            <td>{{ lead.seguimientos }}</td>
            <td>
              <button v-if="leadEditando !== lead.id" class="btn btn-primary" @click="editarLead(lead)">Editar</button>
              <button v-if="leadEditando === lead.id" class="btn btn-success" @click="guardarEdicion">Guardar</button>
              <button v-if="leadEditando === lead.id" class="btn btn-danger" @click="cancelarEdicion">Cancelar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Formulario de edición -->
    <div v-if="leadEditando" class="card p-4 mt-3">
      <h3 class="text-center">Editar Lead</h3>
      <div class="row g-3">
        <div class="col-md-4">
          <label class="form-label">Nombres</label>
          <input type="text" v-model="leadSeleccionado.nombres" class="form-control" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Apellidos</label>
          <input type="text" v-model="leadSeleccionado.apellidos" class="form-control" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Cédula</label>
          <input type="text" v-model="leadSeleccionado.identificacion" class="form-control" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Correo</label>
          <input type="email" v-model="leadSeleccionado.correo" class="form-control" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Teléfono</label>
          <input type="text" v-model="leadSeleccionado.telefono" class="form-control" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Marca</label>
          <select v-model="leadSeleccionado.marca_interes" class="form-select">
            <option v-for="marca in marcasDisponibles" :key="marca" :value="marca">{{ marca }}</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">Modelo</label>
          <input type="text" v-model="leadSeleccionado.modelo_interesado" class="form-control" />
        </div>
        <div class="col-4">
          <label class="form-label">Precio de Venta</label>
          <input
            type="text"
            class="form-control"
            :value="leadSeleccionado.precio_venta ? Number(leadSeleccionado.precio_venta).toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) : ''"
            @input="leadSeleccionado.precio_venta = $event.target.value.replace(/\./g, '')"
          />


        </div>
        <div class="col-md-4">
          <label class="form-label">Estatus</label>
          <select v-model="leadSeleccionado.estatus" class="form-select">
            <option value="nuevo">Nuevo</option>
            <option value="asignado">Asignado</option>
            <option value="en seguimiento">En Seguimiento</option>
            <option value="cerrado">Cerrado</option>
            <option value="culmina en venta">Culmina en Venta</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">Vendedor</label>
          <select v-model="leadSeleccionado.vendedor_id" class="form-select">
            <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">{{ vendedor.nombre }}</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">Test Drive</label>
          <select v-model="leadSeleccionado.test_drive" class="form-select">
            <option value="Si">Sí</option>
            <option value="No">No</option>
          </select>
        </div>
        <div class="col-md-12">
          <label class="form-label">Seguimiento</label>
          <textarea v-model="leadSeleccionado.seguimientos" class="form-control"></textarea>
        </div>
      </div>
      <div class="text-center mt-3">
        <button class="btn btn-success me-2" @click="guardarEdicion">Guardar</button>
        <button class="btn btn-danger" @click="cancelarEdicion">Cancelar</button>
      </div>
    </div>


    </div>
  </template>
  
  
  <script>
  import axios from '../axios';
  import VChart from 'vue-echarts';
  import { use } from 'echarts/core';
  import { FunnelChart } from 'echarts/charts';
  import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
  import { CanvasRenderer } from 'echarts/renderers';
  //import BotonesGlobalesSalir from './BotonesGlobalesSalir.vue';
  
  use([TitleComponent, TooltipComponent, LegendComponent, FunnelChart, CanvasRenderer]);
  
  export default {
    components: {
      VChart,
      //BotonesGlobalesSalir
    },
    data() {
      return {
        headers: [
          "Nombres", "Apellidos", "Identificación", "Teléfono", "Dirección", "Ciudad", "Correo", "Fecha Lead",
          "Origen Lead", "Marca de Interés", "Modelo Interesado", "Precio de Venta", "Estatus", "Test Drive", "Seguimientos", "Vendedor"
        ],

        
        usuarioId: null,  // 🔹 Almacena el ID del usuario autenticado
        leads: [],
        leadsFiltrados: [],
        concesionarios: [],
        vendedores: [],
        marcasDisponibles: ["Subaru", "Suzuki", "Citroen", "Great Wall"],
        //filtroConcesionario: '',
        leadEditando: null,
        leadSeleccionado: {},
        filtroMarca: "",
        filtroVendedor: '',
        filtroEstado: '',
        filtroTestDrive: '',
        filtroFechaDesde: '', // Fecha de inicio del rango
        filtroFechaHasta: '', // Fecha de fin del rango
        totalLeadsAsignados: 0,
        totalLeadsNuevos: 0,
        totalLeadsAsignadosEstado: 0,
        totalLeadsEnSeguimiento: 0,
        totalLeadsCerrados: 0,
        totalLeadsCulminadosEnVenta: 0,
        totalLeadsConTestDrive: 0,
        tiempoUltimaConexion: '',
        ultimaPuestaOnline: '',
        contenidoGenerado: false, // Controla la visibilidad del contenido
        columnWidths: {},   // Anchos de columna inicializados
        resizingColumn: null,
        initialX: 0,
        initialWidth: 0,
        chartOptions: {
          tooltip: { trigger: 'item' },
          legend: { top: 'bottom' },
          series: [
            {
              type: 'funnel',
              left: '10%',
              width: '80%',
              sort: 'descending',
              label: {
                show: true,
                position: 'inside'
              },
              data: [
                { value: this.totalLeadsAsignados, name: 'En sistema' },
                { value: this.totalLeadsNuevos, name: 'Nuevo' },
                { value: this.totalLeadsEnSeguimiento, name: 'En seguimiento' },
                { value: this.totalLeadsCerrados, name: 'Cerrados' },
                { value: this.totalLeadsCulminadosEnVenta, name: 'Culminados en venta' },
                //{ value: this.totalLeadsAsignadosEstado, name: 'Asignados' },
              ],
            },
          ],
        },
      };
    },
    methods: {
        // Método para cargar concesionarios
        //cargarConcesionarios() {
        //    axios.get("/get-concesionarios-con-leads").then((response) => {
        //        this.concesionarios = response.data.map((c) => ({
        //        id: c.id,
        //        nombre: c.nombre_concesionario,
        //        }));
        //    });
        //},
        generarContenidoTabla() {
            this.cargarLeads();
            this.contenidoGenerado = true;
        },
      
        async cargarVendedores() {
          try {
            const response = await axios.get("/get-vendedores");
            this.vendedores = response.data;

            console.log("✅ Vendedores cargados:", this.vendedores); // 🚀 Verifica si se están cargando los datos
          } catch (error) {
            console.error("❌ Error al cargar vendedores:", error);
          }
        },
        // Nueva función para obtener el nombre del vendedor según su ID
        obtenerNombreVendedor(vendedorId) {
            const vendedor = this.vendedores.find(v => v.id === parseInt(vendedorId));
            return vendedor ? vendedor.nombre : null;
        },
        filtrarLeads() {
            console.log("🔎 Filtro de Vendedor:", this.filtroVendedor);
            console.log("🔎 Leads antes de filtrar:", this.leads);

            this.leadsFiltrados = this.leads.filter((lead) => {
              console.log(`Lead ID: ${lead.id}, Vendedor: ${lead.vendedor_nombre}, Comparando con: ${this.filtroVendedor}`);

              const fechaLead = new Date(lead.fecha_lead);
              const fechaDesde = this.filtroFechaDesde ? new Date(this.filtroFechaDesde) : null;
              const fechaHasta = this.filtroFechaHasta ? new Date(this.filtroFechaHasta) : null;
              return (
                  //(!this.filtroConcesionario || lead.concesionario_id === parseInt(this.filtroConcesionario)) &&
                  (!this.filtroMarca || lead.marca_interes === this.filtroMarca) &&
                  (!this.filtroVendedor || lead.vendedor_nombre === this.obtenerNombreVendedor(this.filtroVendedor)) &&
                  (!this.filtroEstado || lead.estatus === this.filtroEstado) &&
                  (!this.filtroTestDrive || lead.test_drive === this.filtroTestDrive) &&
                  (!fechaDesde || fechaLead >= fechaDesde) &&
                  (!fechaHasta || fechaLead <= fechaHasta)
                );
            });
            console.log("✅ Leads después de filtrar:", this.leadsFiltrados);
            this.calcularTotalizadores(); // Recalcula totalizadores después de filtrar
            this.actualizarGrafico();    // Actualiza el gráfico después de filtrar
        },

        async cargarLeads() {
          try {
            const response = await axios.get("/get-leads-gerente");
            this.leads = response.data; // Guarda todos los leads en la lista principal

            console.log("✅ Leads cargados para gerente:", this.leads);

            // 🔹 Asegurar que "seguimientos" y "vendedor_id" no sean NULL
            this.leads = this.leads.map(lead => ({
              ...lead,
              seguimientos: lead.seguimientos ? lead.seguimientos : "",  // Evita que llegue null
              vendedor_id: lead.vendedor_id ? lead.vendedor_id : null    // Evita undefined
            }));

            this.filtrarLeads(); // Aplicar filtros después de la carga
            this.calcularTotalizadores(); // Actualizar totales
            this.actualizarGrafico(); // Refrescar gráfico
          } catch (error) {
            console.error("❌ Error al cargar leads:", error);
          }
        },

        editarLead(lead) {
          this.leadEditando = lead.id;
          this.leadSeleccionado = { ...lead }; // Clonar objeto para evitar modificarlo directamente

          // 🔹 Si el lead tiene un vendedor asignado, asegurarnos de que `vendedor_id` esté bien definido
          if (lead.vendedor_id) {
            this.leadSeleccionado.vendedor_id = lead.vendedor_id;
          } else {
            this.leadSeleccionado.vendedor_id = null; // Evita valores undefined
          }

          // 🔹 Verificar que el campo "seguimientos" tenga datos y no se pierdan
          if (lead.seguimientos) {
            this.leadSeleccionado.seguimientos = lead.seguimientos;
          } else {
            this.leadSeleccionado.seguimientos = ""; // Evita valores undefined o nulos
          }

          if (lead.precio_venta !== undefined && lead.precio_venta !== null) {
            this.leadSeleccionado.precio_venta = lead.precio_venta;
          } else {
            this.leadSeleccionado.precio_venta = 0;
          }


          console.log("🔎 Lead seleccionado para edición:", this.leadSeleccionado);
        },

        async guardarEdicion() {
          try {
            // 🔹 Verificar si `usuarioId` está definido antes de continuar
            if (!this.usuarioId) {
              console.error("❌ Error: usuarioId no está definido.");
              alert("Error: No se encontró el ID del usuario gerente.");
              return;
            }

            if (!this.leadSeleccionado || !this.leadSeleccionado.id) {
              console.error("❌ Error: No hay un lead seleccionado o falta el ID.");
              alert("Error: No hay un lead seleccionado para actualizar.");
              return;
            }

            // 🔹 Agregar `usuario_id` a los datos que se enviarán
            const datosActualizados = {
              ...this.leadSeleccionado,
              usuario_id: this.usuarioId // ✅ Se envía el usuario gerente que está haciendo la edición
            };

            console.log("📤 Enviando datos actualizados al backend:", datosActualizados);

            // 🔹 Enviar los datos al backend
            const response = await axios.post('/update-lead-gerente', datosActualizados);

            // 🔹 Confirmación de éxito
            alert(response.data.message || 'Lead actualizado correctamente');

            // 🔹 Restablecer la edición y recargar los leads
            this.leadEditando = null;
            this.leadSeleccionado = {}; // Limpia los datos seleccionados
            this.cargarLeads(); // Recargar los leads para reflejar los cambios

          } catch (error) {
            console.error("❌ Error al guardar el lead:", error);
            alert("Error al actualizar el lead. Verifica la consola para más detalles.");
          }
        },


        cancelarEdicion() {
          this.leadEditando = null;
          this.leadSeleccionado = {};
        },

       calcularTotalizadores() {
          this.totalLeadsAsignados = this.leadsFiltrados.length;
          this.totalLeadsNuevos = this.leadsFiltrados.filter(lead => lead.estatus === 'nuevo').length;
          this.totalLeadsEnSeguimiento = this.leadsFiltrados.filter(lead => lead.estatus === 'en seguimiento').length;
          this.totalLeadsCerrados = this.leadsFiltrados.filter(lead => lead.estatus === 'cerrado').length;
          this.totalLeadsCulminadosEnVenta = this.leadsFiltrados.filter(lead => lead.estatus === 'culmina en venta').length;
          this.totalLeadsAsignadosEstado = this.leadsFiltrados.filter(lead => lead.estatus === 'asignado').length;
          this.totalLeadsConTestDrive = this.leadsFiltrados.filter(lead => lead.test_drive === 'Si').length;

          if (this.filtroVendedor) {
              axios.get(`/tiempo-ultima-conexion?vendedor=${this.filtroVendedor}`)
                  .then(response => {
                      this.tiempoUltimaConexion = response.data.fecha_ultima_conexion;
                      this.ultimaPuestaOnline = response.data.ultima_puesta_online;
                  })
                  .catch(error => {
                      console.error("Error al obtener fecha desde la última conexión:", error);
                      this.tiempoUltimaConexion = 'Error';
                      this.ultimaPuestaOnline = 'Error';
                  });
          } else {
              this.tiempoUltimaConexion = 'N/A';
              this.ultimaPuestaOnline = 'N/A';
          }
      },

      actualizarGrafico() {
          this.chartOptions.series[0].data = [
              { value: this.totalLeadsAsignados, name: 'En sistema' },
              { value: this.totalLeadsNuevos, name: 'Nuevo' },
              { value: this.totalLeadsEnSeguimiento, name: 'En seguimiento' },
              { value: this.totalLeadsCerrados, name: 'Cerrados' },
              { value: this.totalLeadsCulminadosEnVenta, name: 'Culminados en venta' },
          ];
      },
      //updateChartData() {
        //this.chartOptions.series[0].data = [
          //{ value: this.totalLeadsNuevos, name: 'Nuevos' },
          //{ value: this.totalLeadsAsignados, name: 'En sistema' },
          //{ value: this.totalLeadsEnSeguimiento, name: 'En seguimiento' },
          //{ value: this.totalLeadsCerrados, name: 'Cerrados' },
          //{ value: this.totalLeadsCulminadosEnVenta, name: 'Culminados en venta' },
          //{ value: this.totalLeadsAsignadosEstado, name: 'Asignados' },
        //];
      //},
      guardarLead(lead) {
        axios.post('/update-lead', lead)
          .then(() => {
            alert('Lead actualizado');
          })
          .catch(error => {
            console.error("Error al guardar el lead:", error);
          });
      },
      exportarReporte(formato) {
        const leadsConAsignado = this.leadsFiltrados.map(lead => ({
            ...lead,
            asignado_a: this.filtroVendedor ? parseInt(this.filtroVendedor) : null // Asegurar que `asignado_a` llegue al backend
        }));

        axios.post('/exportar-reporte-gerente', {
            leads: leadsConAsignado,
            vendedor: this.filtroVendedor ? parseInt(this.filtroVendedor) : null, // Enviar ID del vendedor
            filtro_marca: this.filtroMarca || null,  
            filtro_estado: this.filtroEstado || null,
            filtroTestDrive: this.filtroTestDrive || null,
            fechaDesde: this.filtroFechaDesde || null,
            fechaHasta: this.filtroFechaHasta || null,
            formato: formato
        }, { responseType: 'blob' })
        .then(response => {
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `reporte_leads.${formato}`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        })
        .catch(error => {
            console.error("Error al exportar reporte:", error);
        });
      }
    },
    created() {
        this.usuarioId = parseInt(localStorage.getItem("id_usuario")) || null;
        if (!this.usuarioId) {
          console.error("❌ No se pudo obtener el usuario_id.");
        }

        this.cargarVendedores(); // ✅ Cargar vendedores al iniciar
        this.cargarLeads();
      }
  };
  </script>
  
  
  <style scoped>
  .table-responsive {
    margin-top: 20px;
    overflow-x: auto; /* Scroll horizontal si hay muchas columnas */
    overflow-y: auto; /* Scroll vertical dentro del contenedor */
    max-height: 500px; /* 🔹 Altura máxima fija (ajústala a lo que necesites) */
    border: 1px solid #ddd;
  }

  /* Mantener fijo el encabezado al hacer scroll */
  .table thead th {
    position: sticky;
    top: 0;
    background-color: #343a40; /* mismo color del thead */
    color: white;
    z-index: 2; /* asegurar que quede encima */
  }
  
  /* Mantén los estilos actuales de la tabla */
  .table-responsive .table {
    table-layout: auto; /* Cambia de fixed a auto para que las columnas no sean forzadas a un tamaño fijo */
    width: 100%;
  }
  
  .table th, .table td {
    white-space: normal; /* Permite ajuste de texto en varias líneas */
    overflow: visible; /* Evita el recorte del texto */
    text-overflow: unset; /* No se corta el texto */
    padding: 8px; /* Espaciado interno */
    text-align: left; /* Alineación del texto */
    vertical-align: middle; /* Centrado vertical */
    word-wrap: break-word; /* Ajusta palabras largas */
  }
  
  /* Estilo para el encabezado con redimensionamiento */
  .table-responsive .table th div.resizable-header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: col-resize;
  }
  
  .table-responsive .table th {
    position: relative;
  }
  
  .table-responsive .table th div.resizable-header::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 5px;
    cursor: col-resize;
    background-color: transparent;
  }

  .table-warning {
    background-color: #fff3cd !important;
  }
  
  .chart-container {
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .controls .totalizadores p {
    font-size: 1em;
    color: #333;
    margin: 5px 0;
    font-weight: bold;
  }
  
  /* Ajusta el tamaño de los campos de entrada y texto */
  .resizable-input,
  .resizable-textarea {
    font-size: 0.95em; /* Tamaño de fuente ajustado para los campos */
    padding: 5px; /* Espacio interno de los campos */
    resize: horizontal; /* Permite redimensionar solo horizontalmente */
    overflow: auto; /* Asegura el comportamiento correcto al redimensionar */
    min-width: 50px; /* Ancho mínimo para mejor visualización */
  }
  
  /* Estilo específico para el área de texto de seguimiento */
  .seguimiento-textarea {
    resize: vertical; /* Permite redimensionar solo verticalmente */
    max-width: 150px; /* Ancho máximo para mantener la tabla compacta */
    min-height: 80px;
  }
  
  .export-button {
    margin-right: 10px;
  }
  </style>