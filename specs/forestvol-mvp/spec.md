# Especificación SDD — ForestVol MVP

## 1. Nombre del sistema
- **Nombre:** ForestVol
- **Versión:** 5.1 MVP
- **Dueño:** TBD (operador del proyecto)
- **Fecha:** 2026-06-09

## 2. Objetivo
- **Qué resuelve:** cálculo automatizado del volumen de castillos de madera mediante fotogrametría.
- **Para quién:** operadores forestales con dron.
- **Resultado esperado:** volumen en m³ con error ≤15% respecto al Ground Truth.

## 3. Usuarios y roles
| Rol | Qué puede hacer | Restricciones |
|---|---|---|
| Operador | Cargar imágenes, iniciar pipeline, visualizar y exportar resultados. | No accede al backend directamente. |

## 4. Flujos transaccionales
| Flujo | Actor | Entrada | Acción | Salida | Error esperado |
|---|---|---|---|---|---|
| Carga de imágenes | Operador | Set JPG/PNG | POST /api/upload | session_id + estado | INVALID_FORMAT, INSUFFICIENT_IMAGES |
| Calibración | Operador | session_id | POST /api/calibrate | scale_px_per_cm | CALIBRATION_FAILED |
| Reconstrucción | Operador | session_id | POST /api/reconstruct | RECONSTRUCTION_PENDING | NODEODM_TIMEOUT |
| Consulta resultado | Operador | session_id | GET /api/results | volume_m3 | RESULTS_NOT_READY |
| Exportación | Operador | session_id | GET /api/export | JSON / CSV | RESULTS_NOT_READY |

## 5. Requisitos funcionales
| ID | Descripción | Módulo de implementación |
|---|---|---|
| RF-01 | Aceptar sets de imágenes JPG/PNG | `image_validator.py` |
| RF-02 | Rechazar archivos inválidos en <2s | `image_validator.py` |
| RF-03 | Detectar guía de calibración 50×50 cm | `calibration_service.py` |
| RF-04 | Calcular relación px/cm | `calibration_service.py` |
| RF-05 | Alerta si guía no detectada (fallback manual) | `calibration_service.py` |
| RF-06 | Reconstruir nube de puntos 3D (SfM/MVS) | `nodeodm_client.py` |
| RF-07 | Generar malla 3D cerrada (watertight) | `mesh_service.py` |
| RF-08 | Calcular volumen en m³ | `volume_service.py` |
| RF-09 | Error volumétrico ≤15% respecto al GT | `volume_service.py` |
| RF-10 | Mostrar modelo 3D en frontend | `Viewer3D.vue` |
| RF-11 | Exportar reporte en JSON | `volume.py` route |
| RF-12 | Exportar reporte en CSV | `volume.py` route |

## 6. Requisitos no funcionales
| ID | Descripción |
|---|---|
| RNF-01 | Procesamiento total <30 mins (CPU reference hardware). |
| RNF-02 | Despliegue reproducible con `docker-compose up`. |
| RNF-03 | Sin dependencia de GPU CUDA (solo CPU). |
| RNF-04 | Operación local sin internet durante procesamiento. |
| RNF-05 | Frontend SPA accesible en navegador sin instalación. |
| RNF-06 | Arquitectura desacoplada (frontend vs backend API REST). |
| RNF-07 | Operación remota por seguridad laboral. |
| RNF-08 | Independencia de conectividad (sin RTK/GCP absolutos). |

## 7. Datos
| Entidad | Campos principales | Sensible | Retención | Validaciones |
|---|---|---|---|---|
| Sesión | session_id, image_count, pipeline_state | No | 30-90 días | UUID válido, estado en enum |
| Imagen | filename, size_bytes, mime_type | No | 30 días | MIME image/jpeg o image/png |
| Resultado | volume_m3, bounding_box, scale_px_per_cm | No | 90 días | volume_m3 > 0, 4 decimales |

## 8. Base de datos
- **Tipo:** Sistema de archivos local (sin base de datos en MVP).
- **Justificación:** MVP académico sin requerimiento de concurrencia ni consultas relacionales.
- **Migraciones:** no aplica.

## 9. API
- `GET /health`
- `POST /api/upload`
- `POST /api/calibrate/{session_id}`
- `POST /api/reconstruct/{session_id}`
- `GET /api/results/{session_id}`
- `GET /api/export/{session_id}/json`
- `GET /api/export/{session_id}/csv`
- `GET /api/model/{session_id}/mesh.glb`

## 10. Frontend
- **Pantallas:** Dashboard único con ImageUploader, PipelineStatus, Viewer3D, VolumeReport.
- **Componentes:** 4 componentes Vue.js con Composition API.
- **Estados:** loading, processing, completed, error por componente.
- **Validaciones:** formato de archivos en cliente antes de upload.

## 11. Criterios de aceptación
| ID | Criterio | Evidencia requerida |
|---|---|---|
| AC-001 | `docker-compose up --build` levanta 3 servicios | Terminal sin errores |
| AC-002 | `GET /health` ok y NodeODM reachable | Log de prueba |
| AC-003 | `POST /api/upload` acepta 10+ JPG/PNG | test_image_validator.py |
| AC-004 | `POST /api/calibrate/{id}` conf >= 0.90 | test_calibration_service.py |
| AC-005 | NodeODM genera `.PLY` < 30 mins | Archivo `.PLY` |
| AC-006 | Open3D genera malla watertight | test_mesh_service.py |
| AC-007 | `GET /api/results/{id}` retorna volumen | test_volume_service.py |
| AC-008 | Error volumétrico ≤15% sobre GT | Reporte JSON |
| AC-009 | Exportación JSON/CSV descargable | test_pipeline.py |
| AC-010 | Frontend renderiza GLB | test_full_flow.py |
| AC-011 | Hitos en estado "completada" | Trazabilidad JSONs |
| AC-012 | Cobertura pruebas >= 80% (general), >= 90% (críticos) | pytest coverage |

## 12. Pruebas esperadas
- **Unitarias:** test_image_validator, test_calibration_service, test_mesh_service, test_volume_service.
- **Integración:** test_pipeline (flujo completo upload→export).
- **E2E:** test_full_flow (perspectiva del operador).
- **Seguridad:** validación MIME estricta, rechazo de archivos inválidos sin lectura a disco.

## 13. Fuera de alcance
- OOS-001: Generación o captura de imágenes.
- OOS-002: GPU CUDA.
- OOS-003: Base de datos relacional o documental.
- OOS-004: Deploy productivo automático.
- OOS-005: Multi-usuario / autenticación.

## 14. Preguntas abiertas
- Q-001: ¿Se proveerá dataset oficial con Ground Truth para validar RF-09?
- Q-002: ¿Existe presupuesto de tokens/tiempo por ciclo?
