# ForestVol MVP — Technical Plan

## Phases
1. **DEV_PHASE 1 - Infraestructura:** Docker compose, FastAPI skeleton, frontend scaffolding.
2. **DEV_PHASE 2 - Carga de Imágenes (RF-01, RF-02):** `image_validator.py`, route `POST /api/upload`, data storage.
3. **DEV_PHASE 3 - Calibración (RF-03, RF-04, RF-05):** `calibration_service.py` with OpenCV.
4. **DEV_PHASE 4 - Reconstrucción SfM (RF-06):** `nodeodm_client.py` with 3-retry fallback.
5. **DEV_PHASE 5 - Malla 3D (RF-07):** `mesh_service.py` with Open3D (watertight repair).
6. **DEV_PHASE 6 - Volumetría y Exportación (RF-08, RF-09, RF-11, RF-12):** `volume_service.py` and API routes.
7. **DEV_PHASE 7 - Frontend (RF-10):** Vue.js components and Three.js viewer.
8. **DEV_PHASE 8 - Verificación Final:** tests, coverage, full flow validation.

## Stack Aprobado
- Python 3.11 + FastAPI 0.111+
- NodeODM
- OpenCV 4.9+
- Open3D 0.18+
- Vue.js 3.4+ + Three.js r165+
- Docker + Docker Compose
