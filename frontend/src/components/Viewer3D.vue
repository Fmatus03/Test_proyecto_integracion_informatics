<template>
  <div class="viewer-container" ref="container">
    <div v-if="loading" class="viewer-loading">
      <div class="spinner"></div>
      <p>Cargando modelo 3D (puede pesar varios MB)...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const props = defineProps({
  glbUrl: {
    type: String,
    required: true,
  }
});

const container = ref(null);
const loading = ref(true);

let scene, camera, renderer, controls, animationId;

const initThree = () => {
  const width = container.value.clientWidth;
  const height = container.value.clientHeight || 400;

  // Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color('#0f172a'); // matches slate-900

  // Camera
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(0, 5, 10);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.value.appendChild(renderer.domElement);

  // Controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
  directionalLight.position.set(10, 20, 10);
  scene.add(directionalLight);

  loadModel(props.glbUrl);

  // Resize handler
  window.addEventListener('resize', onWindowResize);
  animate();
};

const loadModel = (url) => {
  loading.value = true;
  const loader = new GLTFLoader();
  
  loader.load(
    url,
    (gltf) => {
      const model = gltf.scene;
      
      // Center the model
      const box = new THREE.Box3().setFromObject(model);
      const center = box.getCenter(new THREE.Vector3());
      model.position.x += (model.position.x - center.x);
      model.position.y += (model.position.y - center.y);
      model.position.z += (model.position.z - center.z);
      
      scene.add(model);
      
      // Adjust camera to fit bounding box
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = camera.fov * (Math.PI / 180);
      let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
      camera.position.set(0, maxDim, cameraZ * 1.5);
      
      controls.update();
      loading.value = false;
    },
    undefined,
    (error) => {
      console.error('Error loading GLB:', error);
      loading.value = false;
    }
  );
};

const onWindowResize = () => {
  if (!container.value || !camera || !renderer) return;
  const width = container.value.clientWidth;
  const height = container.value.clientHeight || 400;
  
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
};

const animate = () => {
  animationId = requestAnimationFrame(animate);
  if (controls) controls.update();
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
};

onMounted(() => {
  initThree();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', onWindowResize);
  cancelAnimationFrame(animationId);
  if (renderer) {
    renderer.dispose();
    if (container.value && container.value.contains(renderer.domElement)) {
      container.value.removeChild(renderer.domElement);
    }
  }
});
</script>

<style scoped>
.viewer-container {
  width: 100%;
  height: 400px;
  background: var(--bg-dark);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  border: 1px solid var(--border-color);
}

.viewer-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.8);
  z-index: 10;
  color: white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
