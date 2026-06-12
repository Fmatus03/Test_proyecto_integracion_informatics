<template>
  <div class="pipeline-status">
    <div class="status-card">
      <div class="step" :class="{ 'active': currentStep === 'CALIBRATING', 'completed': stepIndex > 0 }">
        <div class="circle">{{ stepIndex > 0 ? '✓' : '1' }}</div>
        <div class="label">Calibración Espacial</div>
      </div>
      
      <div class="connector" :class="{ 'active': stepIndex > 0 }"></div>

      <div class="step" :class="{ 'active': currentStep === 'RECONSTRUCTING', 'completed': stepIndex > 1 }">
        <div class="circle">{{ stepIndex > 1 ? '✓' : '2' }}</div>
        <div class="label">Reconstrucción 3D (NodeODM)</div>
        <small v-if="currentStep === 'RECONSTRUCTING'" class="hint">Puede demorar varios minutos...</small>
      </div>

      <div class="connector" :class="{ 'active': stepIndex > 1 }"></div>

      <div class="step" :class="{ 'active': currentStep === 'MESHING', 'completed': stepIndex > 2 }">
        <div class="circle">{{ stepIndex > 2 ? '✓' : '3' }}</div>
        <div class="label">Generación de Malla</div>
      </div>
      
      <div class="connector" :class="{ 'active': stepIndex > 2 }"></div>

      <div class="step" :class="{ 'active': currentStep === 'DONE', 'completed': stepIndex > 3 }">
        <div class="circle">{{ stepIndex > 3 ? '✓' : '4' }}</div>
        <div class="label">Volumen Listo</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentStep: {
    type: String,
    required: true,
    // 'CALIBRATING', 'RECONSTRUCTING', 'MESHING', 'DONE', 'ERROR'
  }
});

const steps = ['CALIBRATING', 'RECONSTRUCTING', 'MESHING', 'DONE'];

const stepIndex = computed(() => {
  if (props.currentStep === 'ERROR') return -1;
  return steps.indexOf(props.currentStep);
});
</script>

<style scoped>
.pipeline-status {
  padding: 2rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.status-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 2;
  width: 120px;
  text-align: center;
}

.circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-dark);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  transition: all 0.3s;
}

.label {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
}

.hint {
  font-size: 0.75rem;
  color: var(--primary-color);
  margin-top: 0.25rem;
  animation: pulse 1.5s infinite;
}

/* Active State */
.step.active .circle {
  border-color: var(--primary-color);
  background: var(--primary-dark);
  color: var(--primary-light);
  box-shadow: 0 0 15px var(--primary-color);
  animation: pulse 2s infinite;
}
.step.active .label {
  color: var(--primary-color);
}

/* Completed State */
.step.completed .circle {
  background: var(--success-color);
  border-color: var(--success-color);
  color: white;
}
.step.completed .label {
  color: white;
}

/* Connectors */
.connector {
  flex-grow: 1;
  height: 4px;
  background: var(--border-color);
  margin-top: 20px;
  z-index: 1;
  transition: background 0.3s;
}

.connector.active {
  background: var(--success-color);
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>
