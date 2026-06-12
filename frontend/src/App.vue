<template>
  <div class="app-container">
    <header class="app-header">
      <h1>🌲 ForestVol <span class="badge">MVP 5.1</span></h1>
      <p>Fotogrametría y Volumetría Automatizada para Pilas de Madera</p>
    </header>

    <main class="app-main">
      <!-- IDLE / UPLOAD STATE -->
      <ImageUploader 
        v-if="appState === 'IDLE'" 
        @upload-complete="onUploadComplete" 
      />

      <!-- PROCESSING STATE -->
      <PipelineStatus 
        v-if="['CALIBRATING', 'RECONSTRUCTING', 'MESHING', 'ERROR'].includes(appState)" 
        :current-step="appState" 
      />

      <!-- ERROR STATE overlay -->
      <div v-if="appState === 'ERROR'" class="error-panel">
        <h3>Oops! Algo salió mal.</h3>
        <p>{{ errorMessage }}</p>
        <button class="btn-primary" @click="resetApp">Volver a intentar</button>
      </div>

      <!-- RESULTS STATE -->
      <div v-if="appState === 'DONE'" class="results-layout">
        <div class="viewer-section">
          <Viewer3D :glbUrl="glbModelUrl" v-if="glbModelUrl" />
        </div>
        <div class="report-section">
          <VolumeReport 
            v-if="volumeData"
            :volume="volumeData" 
            :exportCsvUrl="csvUrl"
            @reset="resetApp" 
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import ImageUploader from './components/ImageUploader.vue';
import PipelineStatus from './components/PipelineStatus.vue';
import Viewer3D from './components/Viewer3D.vue';
import VolumeReport from './components/VolumeReport.vue';
import { 
  calibrateSession, 
  startReconstruction, 
  generateMesh, 
  getPipelineStatus, 
  exportCsvUrl 
} from './services/api';

// States: IDLE, CALIBRATING, RECONSTRUCTING, MESHING, DONE, ERROR
const appState = ref('IDLE');
const sessionId = ref(null);
const errorMessage = ref('');
const scaleFactor = ref(null);
const volumeData = ref(null);

const glbModelUrl = computed(() => {
  if (!sessionId.value) return null;
  return `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/results/${sessionId.value}/model.glb`; // Note: we need to serve this file from the backend!
});

const csvUrl = computed(() => {
  return sessionId.value ? exportCsvUrl(sessionId.value) : '#';
});

const onUploadComplete = async (sid) => {
  sessionId.value = sid;
  
  try {
    // 1. Calibration
    appState.value = 'CALIBRATING';
    const calibRes = await calibrateSession(sid);
    scaleFactor.value = calibRes.scale_px_per_cm;

    if (calibRes.fallback_needed) {
      console.warn("Se activó el Fallback en la calibración");
    }

    // 2. NodeODM Reconstruction (SfM)
    appState.value = 'RECONSTRUCTING';
    await startReconstruction(sid);

    // 3. Meshing & Poisson
    appState.value = 'MESHING';
    await generateMesh(sid, scaleFactor.value);

    // 4. Get Final Volume Results
    const results = await getPipelineStatus(sid);
    volumeData.value = results.volume;
    
    appState.value = 'DONE';

  } catch (error) {
    console.error("Pipeline Error:", error);
    appState.value = 'ERROR';
    errorMessage.value = error.response?.data?.message || "Ocurrió un error en el procesamiento fotogramétrico.";
  }
};

const resetApp = () => {
  appState.value = 'IDLE';
  sessionId.value = null;
  errorMessage.value = '';
  scaleFactor.value = null;
  volumeData.value = null;
};
</script>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.app-header {
  text-align: center;
  margin-bottom: 3rem;
}

.app-header h1 {
  font-size: 2.5rem;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.badge {
  background: var(--primary-color);
  font-size: 1rem;
  padding: 4px 12px;
  border-radius: 20px;
  vertical-align: middle;
}

.app-header p {
  color: var(--text-muted);
  font-size: 1.1rem;
}

.error-panel {
  margin-top: 2rem;
  padding: 2rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  text-align: center;
}

.error-panel h3 {
  color: #ef4444;
  margin-top: 0;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
}

/* Results Layout */
.results-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  animation: fadeIn 0.5s ease;
}

@media (max-width: 900px) {
  .results-layout {
    grid-template-columns: 1fr;
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
