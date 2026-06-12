<template>
  <div class="report-container">
    <div class="header">
      <h2>Volumetría Final</h2>
      <span class="badge success">Calculado</span>
    </div>

    <div class="metrics-grid">
      <div class="metric-box highlight">
        <span class="label">Volumen Total</span>
        <span class="value">{{ volume.volume_m3.toFixed(3) }} <small>m³</small></span>
      </div>
      
      <div class="metric-box">
        <span class="label">Largo Máximo</span>
        <span class="value">{{ volume.length_m.toFixed(2) }} <small>m</small></span>
      </div>
      
      <div class="metric-box">
        <span class="label">Ancho Máximo</span>
        <span class="value">{{ volume.width_m.toFixed(2) }} <small>m</small></span>
      </div>
      
      <div class="metric-box">
        <span class="label">Alto Máximo</span>
        <span class="value">{{ volume.height_m.toFixed(2) }} <small>m</small></span>
      </div>
    </div>

    <div class="actions">
      <a :href="exportCsvUrl" target="_blank" class="btn-export csv">
        📥 Descargar Reporte (CSV)
      </a>
      <button class="btn-secondary" @click="$emit('reset')">
        Analizar otro lote
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  volume: {
    type: Object,
    required: true,
  },
  exportCsvUrl: {
    type: String,
    required: true,
  }
});

defineEmits(['reset']);
</script>

<style scoped>
.report-container {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 2rem;
  color: white;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.badge.success {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  border: 1px solid rgba(16, 185, 129, 0.5);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-box {
  background: rgba(30, 41, 59, 0.6);
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
}

.metric-box.highlight {
  grid-column: span 2;
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
}

.metric-box.highlight .value {
  color: var(--primary-light);
  font-size: 3rem;
}

.label {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.value {
  font-size: 1.8rem;
  font-weight: 700;
}

.value small {
  font-size: 0.5em;
  color: var(--text-muted);
}

.actions {
  display: flex;
  gap: 1rem;
}

.btn-export {
  flex: 1;
  text-align: center;
  background: var(--success-color);
  color: white;
  text-decoration: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-export:hover {
  background: var(--success-hover);
}

.btn-secondary {
  flex: 1;
  background: transparent;
  color: white;
  border: 1px solid var(--border-color);
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>
