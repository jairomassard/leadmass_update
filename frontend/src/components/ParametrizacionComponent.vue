<template>
  <div id="parametrizacion" class="container mt-5">
    <h1 class="text-center mb-4">Parametrización de Concesionarios</h1>

    <!-- Formulario para agregar un concesionario -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h3 class="card-title text-center">Agregar Nuevo Concesionario</h3>
        <form @submit.prevent="agregarConcesionario">
          <div class="mb-3">
            <label for="nombre_concesionario" class="form-label">Nombre Concesionario:</label>
            <input type="text" v-model="nuevoConcesionario.nombre_concesionario" class="form-control" required>
          </div>
          <div class="mb-3">
            <label for="ciudad" class="form-label">Ciudad:</label>
            <input type="text" v-model="nuevoConcesionario.ciudad" class="form-control" required>
          </div>
          <div class="mb-3">
            <label>Marcas:</label>
            <div class="row">
              <div class="col-md-2" v-for="marca in marcasDisponibles" :key="marca">
                <div class="form-check">
                  <input type="checkbox" :value="marca" v-model="nuevoConcesionario.marcas" class="form-check-input">
                  <label class="form-check-label">{{ marca }}</label>
                </div>
              </div>
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100">Agregar Concesionario</button>
        </form>
      </div>
    </div>

    <!-- Visor y editor de concesionarios existentes -->
    <h2 class="text-center mb-4">Concesionarios Existentes</h2>
    <div v-if="concesionarios.length">
      <div class="card mb-4 shadow-sm">
        <div class="card-body">
          <h3 class="card-title">{{ concesionarioActual.nombre_concesionario }}</h3>
          <p><strong>Ciudad:</strong> {{ concesionarioActual.ciudad }}</p>
          <p><strong>Marcas Manejadas:</strong></p>
          <ul class="list-unstyled">
            <li v-for="marca in concesionarioActual.marcas" :key="marca">{{ marca }}</li>
          </ul>

          <!-- Botones de navegación -->
          <div class="d-flex justify-content-between mt-4">
            <button class="btn btn-outline-secondary" @click="concesionarioAnterior" :disabled="currentIndex === 0">← Anterior</button>
            <button class="btn btn-outline-secondary" @click="concesionarioSiguiente" :disabled="currentIndex === concesionarios.length - 1">Siguiente →</button>
          </div>

          <!-- Botón para editar el concesionario -->
          <button class="btn btn-info w-100 mt-3" @click="habilitarEdicion">Editar Concesionario</button>

          <!-- Si está en modo edición, habilitar los inputs -->
          <div v-if="editMode" class="mt-3">
            <h4>Editar Concesionario</h4>
            <form @submit.prevent="guardarCambios">
              <div class="mb-3">
                <label for="nombre_concesionario" class="form-label">Nombre Concesionario:</label>
                <input type="text" v-model="concesionarioActual.nombre_concesionario" class="form-control">
              </div>
              <div class="mb-3">
                <label for="ciudad" class="form-label">Ciudad:</label>
                <input type="text" v-model="concesionarioActual.ciudad" class="form-control">
              </div>
              <div class="mb-3">
                <label>Marcas:</label>
                <div class="form-check" v-for="marca in marcasDisponibles" :key="marca">
                  <input type="checkbox" :value="marca" v-model="concesionarioActual.marcas" class="form-check-input">
                  <label class="form-check-label">{{ marca }}</label>
                </div>
              </div>
              <button type="submit" class="btn btn-success w-100">Guardar Cambios</button>
            </form>
          </div>

          <!-- Botón para eliminar el concesionario -->
          <button class="btn btn-danger w-100 mt-3" @click="eliminarConcesionario">Eliminar Concesionario</button>
        </div>
      </div>
    </div>
    
    <!-- Botones globales -->
    <BotonesGlobales />
  </div>
</template>

<script>
import axios from '../axios';
import BotonesGlobales from './BotonesGlobales.vue';

export default {
  data() {
    return {
      concesionarios: [],
      nuevoConcesionario: {
        nombre_concesionario: '',
        ciudad: '',
        marcas: []
      },
      marcasDisponibles: [
        'Mercedez-benz', 'Range Rover', 'Defender', 'Discovery', 'Jaguar',
        'DFSK', 'Seres', 'Subaru', 'Citroen', 'DS Automóviles', 'Suzuki',
        'Develon', 'Dieci', 'Hino', 'Mack', 'Hangcha', 'Komatsu', 'Linde',
        'Still', 'XCMG', 'JAC','Great Wall', "KGM"
      ],
      currentIndex: 0,
      editMode: false
    };
  },
  computed: {
    concesionarioActual() {
      return this.concesionarios[this.currentIndex];
    }
  },
  methods: {
    obtenerConcesionarios() {
      axios.get('/get-concesionarios')
        .then(response => {
          this.concesionarios = response.data;
        })
        .catch(error => {
          console.error("Error al obtener concesionarios:", error);
        });
    },
    agregarConcesionario() {
      axios.post('/add-concesionario', this.nuevoConcesionario)
        .then(() => {
          alert('Concesionario agregado exitosamente');
          this.obtenerConcesionarios();
        })
        .catch(error => {
          console.error("Error al agregar concesionario:", error);
        });
    },
    concesionarioAnterior() {
      if (this.currentIndex > 0) {
        this.currentIndex--;
      }
    },
    concesionarioSiguiente() {
      if (this.currentIndex < this.concesionarios.length - 1) {
        this.currentIndex++;
      }
    },
    habilitarEdicion() {
      this.editMode = true;
    },
    guardarCambios() {
      axios.post('/update-concesionario', this.concesionarioActual)
        .then(() => {
          alert('Concesionario actualizado exitosamente');
          this.editMode = false;
          this.obtenerConcesionarios();  // Actualizar la lista de concesionarios
        })
        .catch(error => {
          console.error("Error al actualizar concesionario:", error);
        });
    },
    eliminarConcesionario() {
      if (confirm('¿Estás seguro de eliminar este concesionario?')) {
        axios.post('/delete-concesionario', { id: this.concesionarioActual.id })
          .then(() => {
            alert('Concesionario eliminado exitosamente');
            this.obtenerConcesionarios();  // Actualizar la lista
          })
          .catch(error => {
            console.error("Error al eliminar concesionario:", error);
          });
      }
    }
  },
  mounted() {
    this.obtenerConcesionarios();
  },
  components: {
    BotonesGlobales
  }
};
</script>

<style scoped>
h1, h2, h3 {
  color: #333;
}

.card {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.table-responsive {
  margin-top: 20px;
}

.badge {
  font-size: 0.9em;
  padding: 5px 10px;
}
</style>







