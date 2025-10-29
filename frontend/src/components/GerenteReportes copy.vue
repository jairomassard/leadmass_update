<template>
  <div id="gerente-reportes" class="container mt-4">
    <h1 class="text-center mb-4">Dashboard de Reportes - Gerencia</h1>

    <!-- Filtros de fechas -->
    <div class="row mb-4">
      <div class="col-md-4">
        <label class="form-label">Fecha desde:</label>
        <input type="date" class="form-control" v-model="fechaDesde" @change="cargarLeads" />
      </div>
      <div class="col-md-4">
        <label class="form-label">Fecha hasta:</label>
        <input type="date" class="form-control" v-model="fechaHasta" @change="cargarLeads" />
      </div>
    </div>

    <!-- KPIs -->
    <div class="row mb-4">
      <div class="col-md-2" v-for="kpi in kpis" :key="kpi.label">
        <div class="card text-center shadow-sm kpi-card">
          <div class="card-body">
            <h5 class="card-title">{{ kpi.label }}</h5>
            <p class="card-text display-6">{{ kpi.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Gráficos -->
    <div class="row">
      <!-- Leads por Marca -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white">Leads por Marca</div>
          <div class="card-body">
            <v-chart v-if="chartMarca.series[0].data.length > 0" :option="chartMarca" style="width:100%; height:350px;" />
            <div v-else class="text-center text-muted">Sin datos (DEBUG Marca)</div>
          </div>
        </div>
      </div>

      <!-- Leads por Modelo -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-success text-white">Leads por Modelo</div>
          <div class="card-body">
            <v-chart v-if="chartModelo.xAxis[0].data.length > 0" :option="chartModelo" style="width:100%; height:350px;" />
            <div v-else class="text-center text-muted">Sin datos (DEBUG Modelo)</div>
          </div>
        </div>
      </div>

      <!-- Leads por Estatus -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-warning text-dark">Leads por Estatus</div>
          <div class="card-body">
            <v-chart v-if="chartEstatus.series[0].data.length > 0" :option="chartEstatus" style="width:100%; height:350px;" />
            <div v-else class="text-center text-muted">Sin datos (DEBUG Estatus)</div>
          </div>
        </div>
      </div>

      <!-- Leads con Test Drive -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-info text-white">Test Drive</div>
          <div class="card-body">
            <v-chart v-if="chartTestDrive.series[0].data.length > 0" :option="chartTestDrive" style="width:100%; height:350px;" />
            <div v-else class="text-center text-muted">Sin datos (DEBUG TestDrive)</div>
          </div>
        </div>
      </div>

      <!-- Pipeline Financiero -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-dark text-white">Pipeline Financiero</div>
          <div class="card-body">
            <v-chart v-if="chartPipeline.xAxis[0].data.length > 0" :option="chartPipeline" style="width:100%; height:350px;" />
            <div v-else class="text-center text-muted">Sin datos (DEBUG Pipeline)</div>
          </div>
        </div>
      </div>

      <!-- Pipeline Funnel -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-secondary text-white">Pipeline Funnel</div>
          <div class="card-body">
            <v-chart v-if="chartFunnel.series[0].data.length > 0" :option="chartFunnel" style="width:100%; height:350px;" />
            <div v-else class="text-center text-muted">Sin datos (DEBUG Funnel)</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "../axios";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { PieChart, BarChart, FunnelChart } from "echarts/charts";
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([TitleComponent, TooltipComponent, LegendComponent, GridComponent, PieChart, BarChart, FunnelChart, CanvasRenderer]);

export default {
  components: { VChart },
  data() {
    return {
      leads: [],
      fechaDesde: "",
      fechaHasta: "",
      kpis: [
        { label: "Total", value: 0 },
        { label: "Nuevos", value: 0 },
        { label: "Seguimiento", value: 0 },
        { label: "Cerrados", value: 0 },
        { label: "Ventas", value: 0 },
        { label: "Test Drive", value: 0 },
      ],
      chartMarca: { series: [{ type: "pie", data: [] }] },
      chartModelo: { xAxis: [{ type: "category", data: [] }], yAxis: [{ type: "value" }], series: [{ type: "bar", data: [] }] },
      chartEstatus: { series: [{ type: "pie", data: [] }] },
      chartTestDrive: { series: [{ type: "pie", data: [] }] },
      chartPipeline: { xAxis: [{ type: "category", data: [] }], yAxis: [{ type: "value" }], series: [{ type: "bar", data: [] }] },
      chartFunnel: { series: [{ type: "funnel", data: [] }] },
    };
  },
  methods: {
    async cargarLeads() {
      try {
        const params = {};
        if (this.fechaDesde) params.fecha_desde = this.fechaDesde;
        if (this.fechaHasta) params.fecha_hasta = this.fechaHasta;

        const response = await axios.get("/get-leads-gerente", { params });
        this.leads = response.data;

        this.calcularKPIs();
        this.generarGraficos();
      } catch (error) {
        console.error("❌ Error al cargar leads:", error);
      }
    },
    calcularKPIs() {
      this.kpis[0].value = this.leads.length;
      this.kpis[1].value = this.leads.filter((l) => l.estatus === "nuevo").length;
      this.kpis[2].value = this.leads.filter((l) => l.estatus === "en seguimiento").length;
      this.kpis[3].value = this.leads.filter((l) => l.estatus === "cerrado").length;
      this.kpis[4].value = this.leads.filter((l) => l.estatus === "culmina en venta").length;
      this.kpis[5].value = this.leads.filter((l) => l.test_drive === "Si").length;
    },
    generarGraficos() {
      // Por Marca
      const porMarca = this.agruparPor("marca_interes");
      this.chartMarca = {
        tooltip: { trigger: "item" },
        series: [{ type: "pie", radius: "60%", data: porMarca, label: { show: true, formatter: "{b}: {c}" } }],
      };

      // Por Modelo
      const porModelo = this.agruparPor("modelo_interesado");
      this.chartModelo = {
        tooltip: { trigger: "axis" },
        xAxis: [{ type: "category", data: porModelo.map((m) => m.name) }],
        yAxis: [{ type: "value" }],
        series: [{ type: "bar", data: porModelo.map((m) => m.value), label: { show: true, position: "top" } }],
      };

      // Por Estatus
      const porEstatus = this.agruparPor("estatus");
      this.chartEstatus = {
        tooltip: { trigger: "item" },
        series: [{ type: "pie", radius: "60%", data: porEstatus, label: { show: true, formatter: "{b}: {c}" } }],
      };

      // Test Drive
      const porTestDrive = this.agruparPor("test_drive");
      this.chartTestDrive = {
        tooltip: { trigger: "item" },
        series: [{ type: "pie", radius: "60%", data: porTestDrive, label: { show: true, formatter: "{b}: {c}" } }],
      };

      // Pipeline Financiero
      const totalProspectado = this.leads.reduce((sum, l) => sum + (l.precio_venta || 0), 0);
      const totalReal = this.leads.filter((l) => l.estatus === "culmina en venta").reduce((sum, l) => sum + (l.precio_venta || 0), 0);

      this.chartPipeline = {
        tooltip: { trigger: "axis", formatter: (params) => `${params[0].name}: $${params[0].value.toLocaleString("es-CO")}` },
        xAxis: [{ type: "category", data: ["Prospectado", "Real (Ventas)"] }],
        yAxis: [{ type: "value", axisLabel: { formatter: (val) => `$${val.toLocaleString("es-CO")}` } }],
        series: [
          {
            type: "bar",
            data: [totalProspectado, totalReal],
            label: { show: true, position: "top", formatter: (val) => `$${val.value.toLocaleString("es-CO")}` },
          },
        ],
      };

      // Funnel
      this.chartFunnel = {
        tooltip: { trigger: "item" },
        series: [{
          type: "funnel",
          left: "10%",
          width: "80%",
          label: { show: true, formatter: "{b}: {c}" },
          data: [
            { value: this.kpis[0].value, name: "Prospectado" },
            { value: this.kpis[2].value, name: "En Seguimiento" },
            { value: this.kpis[3].value, name: "Cerrados" },
            { value: this.kpis[4].value, name: "Ventas" },
          ],
        }],
      };
    },
    agruparPor(campo) {
      const conteo = {};
      this.leads.forEach((lead) => {
        const key = lead[campo] || "No definido";
        conteo[key] = (conteo[key] || 0) + 1;
      });
      return Object.keys(conteo).map((k) => ({ name: k, value: conteo[k] }));
    },
  },
  created() {
    this.cargarLeads();
  },
};
</script>

<style scoped>
.kpi-card {
  background: #f8f9fa;
  border-left: 5px solid #007bff;
}
.kpi-card .card-title {
  font-size: 0.9rem;
  color: #555;
}
.kpi-card .card-text {
  font-weight: bold;
  color: #222;
}
</style>
