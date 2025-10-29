<template>
  <div id="admin-usuarios" class="container mt-5">
    <h1 class="text-center mb-4">Administración de Usuarios</h1>
    
    <!-- Formulario para crear/editar usuario -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h3 class="card-title text-center">{{ usuarioActual.id ? 'Editar Usuario' : 'Crear Nuevo Usuario' }}</h3>
        <form @submit.prevent="guardarUsuario">
          
          <!-- Fila: Nombres y Apellidos -->
          <div class="row mb-3">
            <div class="col-md-6">
              <label for="nombres" class="form-label">Nombres:</label>
              <input type="text" v-model="usuarioActual.nombres" class="form-control" required>
            </div>
            <div class="col-md-6">
              <label for="apellidos" class="form-label">Apellidos:</label>
              <input type="text" v-model="usuarioActual.apellidos" class="form-control" required>
            </div>
          </div>

          <!-- Fila: Usuario, Contraseña y Tipo de Usuario -->
          <div class="row mb-3">
            <div class="col-md-4">
              <label for="usuario" class="form-label">Usuario:</label>
              <input type="text" v-model="usuarioActual.usuario" class="form-control" required>
            </div>
            <div class="col-md-4">
              <label for="password" class="form-label">Contraseña:</label>
              <input type="password" v-model="usuarioActual.password" class="form-control" required>
            </div>
            <div class="col-md-4">
              <label for="tipo_usuario" class="form-label">Tipo de Usuario:</label>
              <select v-model="usuarioActual.tipo_usuario" @change="validarRol" class="form-select">
                <option value="vendedor">Vendedor</option>
                <option value="supervisor">Supervisor</option>
                <option value="administrador">Administrador</option>
                <option value="expert">Expert</option>
                <option value="gerente">Gerente</option>
              </select>
            </div>
          </div>

          <!-- Nueva Fila: Marca Asignada -->
          <div class="row mb-3" v-if="usuarioActual.tipo_usuario === 'gerente' || usuarioActual.tipo_usuario === 'supervisor'">
            <div class="col-md-12">
              <label for="marca_asignada" class="form-label">Marca Asignada:</label>
              <select v-model="usuarioActual.marca_asignada" class="form-select" required>
                <option value="" disabled>Seleccione una marca</option>
                <option v-for="marca in marcasDisponibles" :key="marca" :value="marca">{{ marca }}</option>
              </select>
            </div>
          </div>

          <!-- Fila: Celular y Correo Electrónico -->
          <div class="row mb-3">
            <div class="col-md-6">
              <label for="celular" class="form-label">Celular:</label>
              <input type="text" v-model="usuarioActual.celular" class="form-control">
            </div>
            <div class="col-md-6">
              <label for="correo" class="form-label">Correo Electrónico:</label>
              <input type="email" v-model="usuarioActual.correo" class="form-control">
            </div>
          </div>

          <!-- Fila: Estado y Concesionario -->
          <div class="row mb-3">
            <div class="col-md-6">
              <label for="activo" class="form-label">Estado:</label>
              <select v-model="usuarioActual.activo" class="form-select">
                <option :value="true">Activo</option>
                <option :value="false">Inactivo</option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="concesionario" class="form-label">Concesionario:</label>
              <select v-model="usuarioActual.concesionario" class="form-select" :required="usuarioActual.tipo_usuario === 'vendedor'">
                <option value="" disabled>Seleccione un concesionario</option>
                <option v-for="concesionario in concesionarios" :key="concesionario.id" :value="concesionario.nombre_concesionario">
                  {{ concesionario.nombre_concesionario }} - {{ concesionario.ciudad }}
                </option>
              </select>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100">{{ usuarioActual.id ? 'Actualizar' : 'Crear' }} Usuario</button>

          <!-- Botón Cancelar en modo edición -->
          <div v-if="usuarioActual.id" class="text-center mt-3">
            <button type="button" class="btn btn-warning" @click="cancelarEdicion">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Botón para cargar la lista de usuarios -->
    <div class="text-center mb-4">
      <button class="btn btn-secondary" @click="consultarUsuarios">Revisión Usuarios Creados</button>
    </div>
    
    <!-- Lista de usuarios existentes -->
    <h2 class="text-center mb-3">Lista de Usuarios</h2>
    <div v-if="usuarios.length" class="table-responsive">
      <table class="table table-striped table-hover">
        <thead class="table-dark">
          <tr>
            <th>ID</th>
            <th>Usuario</th>
            <th>Nombres</th>
            <th>Apellidos</th>
            <th>Celular</th>
            <th>Correo</th>
            <th>Tipo</th>
            <th>Concesionario</th>
            <th>Fecha de Creación</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in usuarios" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.usuario }}</td>
            <td>{{ user.nombres }}</td>
            <td>{{ user.apellidos }}</td>
            <td>{{ user.celular || 'N/A' }}</td>
            <td>{{ user.correo || 'N/A' }}</td>
            <td>{{ user.tipo_usuario }}</td>
            <td>{{ user.concesionario || 'N/A' }}</td>
            <td>{{ user.fecha_creacion }}</td>
            <td>
              <span :class="user.activo ? 'badge bg-success' : 'badge bg-danger'">
                {{ user.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm btn-info me-2" @click="editarUsuario(user)">Editar</button>
              <button class="btn btn-sm btn-danger me-2" @click="eliminarUsuario(user)">Eliminar</button>
              <button class="btn btn-sm" :class="user.activo ? 'btn-danger' : 'btn-success'" @click="toggleEstado(user)">
                {{ user.activo ? 'Desactivar' : 'Activar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
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
      usuarios: [],
      usuarioActual: {
        id: null,
        usuario: '',
        password: '',
        nombres: '',
        apellidos: '',
        concesionario: '',
        tipo_usuario: 'vendedor',
        marca_asignada: '',
        activo: true,
        celular: '',
        correo: ''
      },
      concesionarios: [],
      marcasDisponibles: []
    };
  },
  methods: {
    consultarConcesionarios() {
      axios.get('/get-concesionarios')
        .then(response => {
          console.log("✅ Concesionarios cargados:", response.data); // <- Verifica en la consola
          this.concesionarios = response.data;
            this.marcasDisponibles = [
              ...new Set(response.data.flatMap(c => c.marcas))
            ];


        })
        .catch(error => console.error("Error al obtener concesionarios:", error));
    },
    consultarUsuarios() {
      axios.get('/get-usuarios')
        .then(response => {
          this.usuarios = (response.data || []).map(this.normalizeUsuario);
        })
        .catch(error => console.error("Error al obtener usuarios:", error));
    },

    guardarUsuario() {
      if (this.usuarioActual.tipo_usuario === 'vendedor' && !this.usuarioActual.concesionario) {
        alert("El vendedor debe tener un concesionario asignado.");
        return;
      }
      const url = this.usuarioActual.id ? '/update-usuario' : '/add-usuario';
      axios.post(url, this.usuarioActual)
        .then(() => {
          alert('Usuario guardado o actualizado exitosamente');
          this.consultarUsuarios();
          this.cancelarEdicion(); // ✅ limpiar siempre
        })
        .catch(error => console.error("Error al guardar el usuario:", error));
    },
    editarUsuario(user) {
      const u = this.normalizeUsuario(user);
      // Para el select del concesionario el value debe ser string (no array)
      const concesStr = Array.isArray(user.concesionario)
        ? (user.concesionario[0] || '')
        : (user.concesionario || '');

      this.usuarioActual = {
        ...u,
        concesionario: concesStr === 'N/A' ? '' : concesStr
      };
    },

    cancelarEdicion() {
      this.usuarioActual = { 
        id: null, usuario: '', password: '', nombres: '', apellidos: '', 
        concesionario: '', tipo_usuario: 'vendedor', marca_asignada: '', 
        activo: true, celular: '', correo: '' 
      };
    },
    eliminarUsuario(user) {
      if (confirm(`⚠️ ¿Estás seguro de que deseas eliminar al usuario ${user.usuario}?`) &&
          confirm("Esta acción es irreversible. Confirma nuevamente para eliminar.")) {
        axios.post('/delete-usuario', { id: user.id })
          .then(() => {
            alert("Usuario eliminado exitosamente");
            this.consultarUsuarios();
          })
          .catch(error => console.error("❌ Error al eliminar usuario:", error));
      }
    },
    normalizeUsuario(u) {
      return {
        ...u,
        // Concesionario: si viene como array => "A, B", si viene null => "N/A"
        concesionario: Array.isArray(u.concesionario)
          ? (u.concesionario.filter(Boolean).join(', ') || 'N/A')
          : (u.concesionario || 'N/A'),

        // Fecha: a legible local
        fecha_creacion: u.fecha_creacion
          ? new Date(u.fecha_creacion).toLocaleString('es-CO')
          : 'N/A',

        // Campos vacíos legibles
        celular: u.celular || 'N/A',
        correo: u.correo || 'N/A',

        // Asegurar boolean consistente
        activo: (u.activo === true || u.activo === 'true' || u.activo === 1),

        // Marca asignada siempre definida para evitar warnings en el form
        marca_asignada: u.marca_asignada || ''
      };
    },
    toggleEstado(user) {
      user.activo = !user.activo;
      axios.post('/update-usuario', user)
        .then(() => this.consultarUsuarios())
        .catch(error => console.error("Error al cambiar estado:", error));
    },
    validarRol() {
      if (this.usuarioActual.tipo_usuario !== 'gerente' && this.usuarioActual.tipo_usuario !== 'supervisor') {
        this.usuarioActual.marca_asignada = '';
      }
    }
  },
  created() {
    this.consultarConcesionarios();
    this.consultarUsuarios();
  },
  components: { BotonesGlobales }
};
</script>


<style scoped>
h1, h2 {
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

.table th,
.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.9em;
  padding: 5px 10px;
}
</style>


