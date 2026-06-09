# ForestVol MVP — Tasks

## DEV_PHASE 1 - Infraestructura (Hito 0_etapa_1)
- [x] Crear directorios y `.gitkeep` en `data/`
- [x] Crear `.env.example`
- [x] Crear `docker-compose.yml`
- [x] Crear `backend/Dockerfile` y `backend/requirements.txt`
- [x] Crear `backend/app/main.py` con endpoint `/health`
- [x] Crear esquemas base Pydantic (`schemas.py`)
- [x] Crear `frontend/Dockerfile`, `package.json`, `vite.config.js` y app Vue.js mínima
- [x] Agregar soporte `.gitignore`
- [x] Verificación Docker: pendiente (por el usuario)

## DEV_PHASE 2 - Carga de Imágenes (Hito 0_etapa_2)
- [ ] Implementar `image_validator.py`
- [ ] Implementar `POST /api/upload`

## DEV_PHASE 3 - Integración NodeODM (Hito 0_etapa_3)
- [ ] Implementar `nodeodm_client.py`
- [ ] Implementar `POST /api/reconstruct/{session_id}`

## Resto de fases: pendientes de expansión.
