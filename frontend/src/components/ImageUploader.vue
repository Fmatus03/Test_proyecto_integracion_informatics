<template>
  <div 
    class="uploader-container" 
    :class="{ 'is-dragover': isDragging }"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <div class="uploader-content" v-if="!isUploading">
      <div class="icon">📁</div>
      <h3>Arrastrá las fotos acá</h3>
      <p>o hacé clic para seleccionar los archivos JPG/PNG del vuelo</p>
      
      <input 
        type="file" 
        multiple 
        accept="image/jpeg, image/jpg, image/png" 
        class="file-input" 
        @change="onFileSelect"
        ref="fileInput"
      />
      
      <button class="btn-primary" @click="$refs.fileInput.click()">
        Seleccionar Imágenes
      </button>

      <div class="file-count" v-if="files.length > 0">
        {{ files.length }} archivos seleccionados listos para subir.
      </div>
      <button class="btn-success" v-if="files.length >= 10" @click="startUpload">
        Iniciar Procesamiento
      </button>
      <div class="error-msg" v-if="files.length > 0 && files.length < 10">
        Necesitás al menos 10 imágenes para una reconstrucción 3D válida.
      </div>
    </div>

    <div class="uploading-state" v-else>
      <div class="spinner"></div>
      <h3>Subiendo imágenes...</h3>
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <p>{{ uploadProgress }}% completado</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { uploadImages } from '../services/api';

const emit = defineEmits(['upload-complete']);

const isDragging = ref(false);
const files = ref([]);
const isUploading = ref(false);
const uploadProgress = ref(0);

const onDragOver = () => {
  isDragging.value = true;
};

const onDragLeave = () => {
  isDragging.value = false;
};

const onDrop = (e) => {
  isDragging.value = false;
  handleFiles(e.dataTransfer.files);
};

const onFileSelect = (e) => {
  handleFiles(e.target.files);
};

const handleFiles = (fileList) => {
  // Filter JPEGs and PNGs
  const validFiles = Array.from(fileList).filter(
    f => f.type === 'image/jpeg' || f.name.toLowerCase().endsWith('.jpg') || f.type === 'image/png' || f.name.toLowerCase().endsWith('.png')
  );
  files.value = validFiles;
};

const startUpload = async () => {
  if (files.value.length < 10) return;
  
  isUploading.value = true;
  uploadProgress.value = 0;
  
  try {
    const result = await uploadImages(files.value, (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      uploadProgress.value = percentCompleted;
    });
    
    // Result has { session_id, message, files_accepted }
    emit('upload-complete', result.session_id);
  } catch (error) {
    console.error("Error uploading images", error);
    alert("Hubo un error subiendo las imágenes. Revisa la consola.");
    isUploading.value = false;
  }
};
</script>

<style scoped>
.uploader-container {
  background: var(--glass-bg);
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  color: var(--text-color);
}

.uploader-container.is-dragover {
  border-color: var(--primary-color);
  background: rgba(30, 41, 59, 0.8);
  transform: scale(1.02);
}

.file-input {
  display: none;
}

.icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
}

p {
  color: var(--text-muted);
  margin-bottom: 2rem;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 1rem;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-success {
  background: var(--success-color);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 1rem;
  display: block;
  margin-left: auto;
  margin-right: auto;
  font-size: 1.1rem;
}

.btn-success:hover {
  background: var(--success-hover);
}

.file-count {
  margin-top: 1rem;
  font-weight: 500;
  color: var(--primary-light);
}

.error-msg {
  color: #ef4444;
  margin-top: 1rem;
  font-weight: 500;
}

/* Uploading State */
.uploading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

.progress-bar-container {
  width: 100%;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-bar {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
