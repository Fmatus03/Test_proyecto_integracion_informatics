# 04. Orquestador, Ciclo de 12 Pasos y Operabilidad — ForestVol MVP

**Proyecto:** ForestVol  
**Versión:** 5.1  
**Fecha:** 2026-06-08  
**Estado:** `complete`  
**Propósito:** definir la misión del orquestador, máquina de estados del ciclo, los 12 pasos obligatorios con sus gates, estado canónico, routing de fases, logs, tokens, circuit breakers, validaciones, retries, aprendizaje, observabilidad y checklist de operabilidad para el proyecto ForestVol MVP.

---

## 1. Misión del orquestador

El orquestador es el controlador operativo del ciclo ForestVol. No es un chat libre. No improvisa. No implementa código directamente.

Debe:

1. Recibir el objetivo del MVP y normalizarlo como Work Order.
2. Crear `state.json` con `cycle_id`, objetivo y stack.
3. Ejecutar siempre el ciclo de 12 pasos en orden.
4. Informar al usuario antes de ejecutar (plan) y al cerrar (resultado).
5. Controlar roles, skills, herramientas, permisos y presupuesto.
6. Aplicar el flujo SDD completo: spec → plan → tasks → analyze → implement → validate → close.
7. Ejecutar pruebas y validaciones en cada cierre de hito.
8. Registrar logs, tokens, costo y tiempos en `.factory/runs/<cycle_id>/`.
9. Actualizar trazabilidad JSON en `trazabilidad/` al completar cada etapa.
10. Actualizar aprendizaje en `.factory/memory/Aprendizaje.ForestVol.md` cuando corresponda.
11. Cerrar con estado controlado: `complete`, `needs_user_input`, `not_answerable` o `error`.

---

## 2. Estados cerrados del ciclo

| Estado | Uso |
|---|---|
| `complete` | Todos los gates críticos pasan. DoD cumplida. Evidencias registradas. |
| `needs_user_input` | Falta decisión o dato crítico del usuario para avanzar (Ground Truth, escala manual, aprobación Meshroom, dependency request). |
| `not_answerable` | La decisión exige evidencia que no existe (métricas sin Ground Truth). |
| `error` | Falló herramienta, validación o ejecución no recuperable. |

---

## 3. Máquina de estados del ciclo

```
INIT
  -> NORMALIZE_WORK_ORDER      (crear state.json, cycle_id, objetivo)
  -> PLAN_CYCLE                (paso 1: definir scope, stack, gates)
  -> LOAD_INDEX_CACHE          (paso 2: indexar back_data/, specs/, código)
  -> READ_LEARNING             (paso 3: leer Aprendizaje.ForestVol.md)
  -> START_LOGS                (paso 4: abrir cycle_log.jsonl)
  -> START_USAGE_LEDGER        (paso 5: abrir usage_ledger.jsonl)
  -> INFORM_USER_PLAN          (paso 6: emitir mensaje de plan al usuario)
  -> EXECUTE_SDD_FLOW          (paso 7: spec → plan → tasks → analyze → implement → validate)
      -> SPECIFY               (crear spec.md)
      -> CLARIFY               (resolver preguntas abiertas)
      -> CHECKLIST             (validar requisitos)
      -> CONTEXT_GROUNDING     (indexar evidencia)
      -> PLAN                  (crear plan.md)
      -> PLAN_VALIDATION       (verificar stack y dependencias)
      -> TASKS                 (crear tasks.md con RF-XX)
      -> ANALYZE               (crear analyze-report.md → Proceed: yes/no)
      -> IMPLEMENT             (fases 1-8 en orden estricto)
          -> DEV_PHASE_1_INFRA
          -> DEV_PHASE_2_UPLOAD
          -> DEV_PHASE_3_NODEODM                   [cierre Hito 0]
          -> DEV_PHASE_4_CALIBRACION               [cierre Hito 1]
          -> DEV_PHASE_5_MALLA_Y_VOL_PRELIMINAR    [cierre Hito 0.5 — ver nota(*) abajo]
          -> DEV_PHASE_6_VOLUMETRIA                [cierre Hito 2]
          -> DEV_PHASE_7_FRONTEND
          -> DEV_PHASE_8_ESTABILIZACION            [cierre Hito 3]
      -> VALIDATE              (pytest + cobertura + trazabilidad)

> (*) **Nota de orden de hitos:** El Hito 0.5 tiene un nombre de archivo `hito_0_5_volumetria_preliminar.json` que aparece antes de `hito_1` alfabéticamente, pero **cronológicamente se ejecuta en Sprint 3, después de Hito 1 (Sprint 2)**. El nombre refleja su posición conceptual de "validación preliminar" entre Hito 0 y el Hito 2 de volumetría funcional, no su orden de ejecución. El orden de sprints es: S1=Hito0, S2=Hito1, S3=Hito0.5, S4=Hito2, S5=Hito3.
  -> RUN_TESTS                 (paso 8: ejecutar suite completa)
  -> LEARNING_AND_RETRY        (paso 9: registrar aprendizaje o reintentar)
  -> UPDATE_INDEX_CACHE        (paso 10: actualizar índice y cache)
  -> INFORM_RESULT             (paso 11: emitir mensaje de resultado)
  -> CLOSE                     (paso 12: registrar tokens/costo/tiempo, generar final-report.md)
```

### 3.1 Transiciones críticas

| Transición | Condición requerida |
|---|---|
| `PLAN_CYCLE → LOAD_INDEX_CACHE` | `cycle_id` creado, objetivo definido, `state.json` escrito. |
| `INFORM_USER_PLAN → EXECUTE_SDD_FLOW` | Mensaje de plan emitido y registrado en `cycle_log.jsonl`. |
| `CLARIFY → CHECKLIST` | Todas las preguntas críticas respondidas o en estado `needs_user_input`. |
| `CHECKLIST → CONTEXT_GROUNDING` | Requisitos claros, testables y con criterios de aceptación. |
| `PLAN_VALIDATION → TASKS` | Plan usa solo stack aprobado. Sin dependencias no autorizadas. |
| `ANALYZE → IMPLEMENT` | `analyze-report.md` con campo `Proceed: yes`. Sin contradicciones spec→plan→tasks. |
| `DEV_PHASE_N → DEV_PHASE_N+1` | DoD de la fase anterior cumplida. `trazabilidad/{hito}.json` actualizado. |
| `VALIDATE → CLOSE` | Suite de pruebas ejecutada. Cobertura ≥ 80% backend, ≥ 90% servicios críticos. |
| `CLOSE` | `final-report.md` generado. `usage_ledger.jsonl` con tokens finales. |

---

## 4. Ciclo obligatorio de 12 pasos — ForestVol MVP

### Paso 1 — Planificar el ciclo

**Meta:** definir objetivo, producto esperado y regla de no inventar.

```yaml
step_id: 1_plan_cycle
required: true
outputs:
  - .factory/runs/CYCLE-FORESTVOL-MVP-001/state.json
gate:
  cycle_id_created: true
  objective_defined: true
  no_invention_rule_set: true
```

El orquestador debe declarar en `state.json`:

```json
{
  "cycle_id": "CYCLE-FORESTVOL-MVP-001",
  "trace_id": "TRACE-001",
  "project_id": "forestvol-mvp",
  "status": "running",
  "objective": "Implementar el MVP completo de ForestVol v5.1: pipeline carga→calibración→SfM/MVS→malla→volumen.",
  "product_expected": "Sistema ForestVol ejecutable con docker-compose up, pipeline end-to-end funcional y trazabilidad completa.",
  "scope": "Backend FastAPI + Frontend Vue.js + NodeODM + Open3D + OpenCV.",
  "out_of_scope": "Captura de imágenes, GPU CUDA, base de datos, microservicios.",
  "stack": {
    "backend": "Python3.11/FastAPI",
    "calibration": "OpenCV4.9+",
    "sfm": "NodeODM",
    "geometry": "Open3D0.18+",
    "frontend": "Vue.js3/Three.js",
    "infra": "Docker/DockerCompose"
  },
  "current_phase": "plan_cycle",
  "gates": {
    "spec_exists": "pending",
    "plan_valid": "pending",
    "tasks_atomic": "pending",
    "analyze_approved": "pending",
    "validation": "pending",
    "budget": "pending"
  },
  "hitos": {
    "hito_0": "pending",
    "hito_1": "pending",
    "hito_0_5": "pending",
    "hito_2": "pending",
    "hito_3": "pending"
  },
  "regla": "No inventar requisitos, métricas, dependencias ni reglas de negocio no especificadas."
}
```

---

### Paso 2 — Cargar índice y cache de contexto

**Meta:** evitar contexto gigante y reutilizar evidencia.

```yaml
step_id: 2_load_index_cache
outputs:
  - .factory/runs/CYCLE-FORESTVOL-MVP-001/context-cache.json
```

Indexar:
- `back_data/` → documentación del proyecto.
- `trazabilidad/` → estado de hitos anteriores.
- `.factory/memory/Aprendizaje.ForestVol.md` → aprendizajes validados.
- `specs/forestvol-mvp/` → artefactos SDD existentes.
- `backend/` y `frontend/` → código existente (si hay).

---

### Paso 3 — Analizar aprendizajes previos

**Meta:** usar aprendizajes validados sin contaminar el ciclo.

```yaml
step_id: 3_read_learning
inputs:
  - .factory/memory/Aprendizaje.ForestVol.md
```

Reglas:
- Ignorar aprendizajes con estado `proposed` o `rejected`.
- No cargar secretos ni PII.
- Registrar en `context-cache.json` qué aprendizajes influyeron en este ciclo.

---

### Paso 4 — Iniciar logs

**Meta:** abrir trazas antes de ejecutar cualquier implementación.

```yaml
step_id: 4_start_logs
outputs:
  - .factory/runs/CYCLE-FORESTVOL-MVP-001/cycle_log.jsonl
```

Estructura de cada evento:
```json
{
  "timestamp": "datetime ISO-8601",
  "cycle_id": "CYCLE-FORESTVOL-MVP-001",
  "trace_id": "TRACE-001",
  "phase": "string",
  "event": "string",
  "status": "running|success|blocked|error",
  "evidence_path": "string|null"
}
```

Eventos mínimos a registrar:
- `cycle_started`
- `phase_started:<nombre>`
- `phase_completed:<nombre>`
- `gate_passed:<nombre>`
- `gate_failed:<nombre>`
- `hito_closed:<nombre>`
- `bloqueante_registrado:<descripción>`
- `cycle_closed`

---

### Paso 5 — Registrar consumo de tokens y hora de inicio

**Meta:** medir costo y presupuesto desde el inicio.

```yaml
step_id: 5_start_usage
outputs:
  - .factory/runs/CYCLE-FORESTVOL-MVP-001/usage_ledger.jsonl
```

Entrada inicial:
```json
{
  "cycle_id": "CYCLE-FORESTVOL-MVP-001",
  "started_at": "datetime",
  "model": "claude-opus-4-6",
  "input_tokens": 0,
  "cached_input_tokens": 0,
  "output_tokens": 0,
  "tool_calls": 0,
  "estimated_cost": 0,
  "budget": {
    "max_tool_calls": "TBD",
    "max_duration_minutes": "TBD",
    "max_retries": 1
  }
}
```

Actualizar al cierre de cada fase con los valores reales. Si el proveedor no entrega tokens exactos, registrar `"not_available"` y marcar como `"estimated": true`.

---

### Paso 6 — Informar plan al usuario

**Meta:** transparencia obligatoria antes de ejecutar cualquier código.

**No avanzar a implementación si este mensaje no fue emitido y registrado en `cycle_log.jsonl`.**

Mensaje obligatorio:

```markdown
## Plan de ciclo — CYCLE-FORESTVOL-MVP-001

- **Objetivo:** Implementar MVP ForestVol v5.1 — pipeline fotogramétrico completo.
- **Stack aprobado:** Python 3.11, FastAPI, Vue.js 3, Three.js, NodeODM, Open3D, OpenCV, Docker Compose.
- **Fases:** 8 fases de implementación en orden estricto.
- **Hitos:** Hito 0 → Hito 1 → Hito 0.5 → Hito 2 → Hito 3.
- **Gates activos:** spec_exists, plan_valid, tasks_atomic, analyze_approved, validation, budget.
- **Trazabilidad:** trazabilidad/{hito}.json + .factory/runs/CYCLE-001/.
- **Regla:** no se escribe código sin task aprobada mapeada a RF-XX y prueba.
- **Bloqueos posibles:** NodeODM no disponible, malla no watertight, error volumétrico >25% en Hito 0.5.
- **Condición de cierre exitoso:** todos los hitos en estado "completada", error volumétrico ≤15% (si GT disponible), docker-compose up funcional.
```

---

### Paso 7 — Ejecutar flujo SDD (implementación)

**Meta:** implementar el MVP en 8 fases siguiendo el orden estricto.

Sub-reglas obligatorias:
- No pasar a `IMPLEMENT` sin `analyze-report.md` con `Proceed: yes`.
- No pasar a siguiente fase sin DoD cumplida y trazabilidad actualizada.
- No pasar a `CLOSE` sin `validation-report.md` aprobado.

#### Orden de implementación obligatorio

```
DEV_PHASE 1 — INFRAESTRUCTURA BASE Y ARTEFACTOS SDD
  1.1  Crear estructura de directorios completa
  1.2  Crear .env.example
  1.3  Crear .factory/runs/CYCLE-FORESTVOL-MVP-001/state.json
  1.4  Crear trazabilidad/*.json (todas las etapas en "pendiente")
  1.5  Crear specs/forestvol-mvp/spec.md
  1.6  Crear specs/forestvol-mvp/plan.md
  1.7  Crear specs/forestvol-mvp/tasks.md
  1.8  Crear specs/forestvol-mvp/analyze-report.md (Proceed: yes)
  1.9  Crear docker-compose.yml con 3 servicios
  1.10 Crear backend/Dockerfile (Python 3.11)
  1.11 Crear frontend/Dockerfile (Node 20)
  1.12 Crear backend/app/main.py con /health y schemas base
  1.13 Verificar docker-compose up sin errores
  → Actualizar trazabilidad/hito_0_validacion_tecnica.json (etapa 1)

DEV_PHASE 2 — PIPELINE DE CARGA
  2.1  Implementar image_validator.py (extensión + MIME + tamaño + cantidad)
  2.2  Implementar schemas.py con modelos Pydantic v2
  2.3  Implementar endpoint POST /api/upload
  2.4  Gestión de session_id y almacenamiento en data/uploads/
  2.5  Tests unitarios test_image_validator.py
  → Actualizar trazabilidad/hito_0_validacion_tecnica.json (etapa 2)

DEV_PHASE 3 — INTEGRACIÓN NODEODM                         [CIERRE HITO 0]
  3.1  Implementar nodeodm_client.py (REST + polling + 3 intentos fallback)
  3.2  Implementar endpoint POST /api/reconstruct/{session_id}
  3.3  Probar con dataset mínimo (10+ imágenes)
  3.4  Verificar .PLY generado en data/processed/
  → Actualizar trazabilidad/hito_0_validacion_tecnica.json (etapa 3 — CIERRE HITO 0)

DEV_PHASE 4 — CALIBRACIÓN ESPACIAL                        [CIERRE HITO 1]
  4.1  Implementar calibration_service.py con OpenCV
  4.2  Detección contornos de guía 50×50 cm + ArUco opcional
  4.3  Cálculo px/cm y transformación homográfica
  4.4  Fallback de escala manual
  4.5  Endpoint POST /api/calibrate/{session_id}
  4.6  Tests test_calibration_service.py con métricas
  → Actualizar trazabilidad/hito_1_calibracion_espacial.json (CIERRE HITO 1)

DEV_PHASE 5 — MALLA 3D Y VOLUMETRÍA PRELIMINAR                [CIERRE HITO 0.5]
  5.1  Implementar mesh_service.py (Poisson Surface Reconstruction)
  5.2  2 ciclos de reparación automática de malla
  5.3  Verificación watertightness obligatoria
  5.4  Aplicar escala métrica a la malla
  5.5  Exportación GLB (visualización) y PLY (procesamiento)
  5.6  Tests test_mesh_service.py
  5.7  Cálculo volumétrico preliminar sobre dataset de prueba
  5.8  Verificar error ≤25% o registrar bloqueante
  → Actualizar trazabilidad/hito_0_5_volumetria_preliminar.json (CIERRE HITO 0.5)

DEV_PHASE 6 — VOLUMETRÍA FUNCIONAL Y EXPORTACIÓN         [CIERRE HITO 2]
  6.1  Implementar volume_service.py con get_volume() de Open3D
  6.2  Bounding box (largo, ancho, alto en metros)
  6.3  Metadata completa + estructura JSON de reporte
  6.4  Endpoint GET /api/results/{session_id}
  6.5  Endpoint GET /api/export/{session_id}/json
  6.6  Endpoint GET /api/export/{session_id}/csv
  6.7  Tests test_volume_service.py
  6.8  Tests integración test_pipeline.py
  6.9  Verificar pipeline end-to-end sin intervención manual
  6.10 Verificar error ≤15% o clasificar MVP ACEPTABLE/FALLIDO
  6.11 Completar specs/forestvol-mvp/traceability-matrix.md
  → Actualizar trazabilidad/hito_2_volumetria_funcional.json (CIERRE HITO 2)

DEV_PHASE 7 — FRONTEND VUE.JS + THREE.JS
  7.1  Scaffolding Vue.js 3 + Composition API + Vite
  7.2  services/api.js con axios (base URL desde env)
  7.3  ImageUploader.vue (drag & drop + validación visual)
  7.4  PipelineStatus.vue (polling de estado + barra de progreso)
  7.5  Viewer3D.vue (Three.js + GLB + OrbitControls)
  7.6  VolumeReport.vue (métricas + botones exportación)
  7.7  Dashboard.vue (integración de todos los componentes)
  → Actualizar trazabilidad/hito_3_mvp_completo.json (etapas frontend)

DEV_PHASE 8 — ESTABILIZACIÓN Y CIERRE                    [CIERRE HITO 3]
  8.1  Tests e2e test_full_flow.py (flujo operador completo)
  8.2  Verificar cobertura ≥80% backend, ≥90% servicios críticos
  8.3  Verificar docker-compose up --build sin errores
  8.4  README.md con instrucciones de despliegue y uso
  8.5  Crear specs/forestvol-mvp/validation-report.md
  8.6  Revisar todos los archivos de trazabilidad (estado "completada")
  8.7  Verificar DoD de cada hito
  8.8  Actualizar Aprendizaje.ForestVol.md con aprendizajes del ciclo
  8.9  Actualizar usage_ledger.jsonl con tokens y costo total
  8.10 Crear .factory/runs/CYCLE-FORESTVOL-MVP-001/final-report.md
  8.11 Emitir mensaje de cierre al usuario (Paso 11)
  8.12 Registrar hora de término y métricas finales (Paso 12)
  → Actualizar trazabilidad/hito_3_mvp_completo.json (CIERRE HITO 3 — MVP COMPLETO)
```

---

### Paso 8 — Ejecutar pruebas de validación

**Meta:** probar siempre antes de cerrar cualquier hito.

| Tipo de prueba | Obligatorio si | Evidencia |
|---|---|---|
| Unitarias backend | Siempre | `backend/tests/unit/` |
| Integración pipeline | Siempre | `backend/tests/integration/test_pipeline.py` |
| E2E flujo operador | Cierre Hito 3 | `backend/tests/e2e/test_full_flow.py` |
| Cobertura pytest | Cierre de cada hito | Reporte de cobertura |
| Docker build | Cierre de cada fase | Salida de `docker-compose build` |

Gate:
```yaml
gate: validation_required
pass_condition:
  traceability_complete: true
  required_tests_executed: true
  critical_tests_passed: true
  coverage_backend_pct: >= 80
  coverage_critical_services_pct: >= 90
  docker_build_success: true
on_fail:
  action: "bloquear cierre del hito + registrar aprendizaje"
```

---

### Paso 9 — Si no cumple, registrar aprendizaje y decidir retry o bloqueo

**Meta:** no repetir errores sin aprendizaje.

Si falla un gate o prueba:
```
1. Registrar finding en cycle_log.jsonl.
2. Clasificar causa: calibración | nodeodm | malla | volumen | test | scope | dependencia.
3. Actualizar .factory/memory/Aprendizaje.ForestVol.md si aplica.
4. Decidir: retry (máx. 1 por fase) → rollback → bloqueo (needs_user_input).
5. Registrar decisión en state.json campo "last_block_reason".
6. Volver a la fase SDD correcta.
```

Política de reintentos:
```yaml
max_retries_per_phase: 1
max_total_cycle_retries: 2
on_exceeded: "needs_user_input"
```

Casos específicos de manejo:
- **NodeODM falla:** ejecutar 3 intentos fallback → si falla: `needs_user_input` + proponer Meshroom.
- **Malla no watertight:** ejecutar 2 ciclos de reparación → si falla: bloquear volumen.
- **Error >25% en Hito 0.5:** detener avance a Hito 2, revisar calibración.
- **Error >15% en Hito 2:** clasificar MVP ACEPTABLE o FALLIDO, documentar.

---

### Paso 10 — Actualizar índice y cache

**Meta:** mantener contexto reproducible para ciclos futuros.

Actualizar si cambiaron: spec, plan, tasks, analyze, código, tests, contratos, trazabilidad.

Salidas:
```
.factory/runs/CYCLE-FORESTVOL-MVP-001/index-update-report.md
.factory/runs/CYCLE-FORESTVOL-MVP-001/cache-update-report.md
```

---

### Paso 11 — Informar resultado al usuario

**Meta:** cierre operacional claro.

Emitir mensaje con:
- Qué hitos se cerraron y cuáles quedaron pendientes.
- Qué artefactos se crearon o modificaron.
- Qué gates pasaron y cuáles fallaron.
- Qué pruebas se ejecutaron y sus resultados (cobertura obtenida).
- Error volumétrico obtenido (o `null` si no hay Ground Truth).
- Clasificación del MVP: EXITOSO / ACEPTABLE / FALLIDO / PENDIENTE.
- Estado final del ciclo.
- Próximos pasos si hay bloqueo.

---

### Paso 12 — Registrar cierre, tokens y costo

**Meta:** cerrar con medición completa.

Actualizar `usage_ledger.jsonl` con entrada de cierre:
```json
{
  "cycle_id": "CYCLE-FORESTVOL-MVP-001",
  "ended_at": "datetime",
  "duration_seconds": 0,
  "tokens": {
    "input": 0,
    "cached": 0,
    "output": 0
  },
  "tool_calls": 0,
  "estimated_cost": 0,
  "status": "complete|needs_user_input|error"
}
```

Crear `final-report.md` con:
```markdown
# Final Report — CYCLE-FORESTVOL-MVP-001

- cycle_id: CYCLE-FORESTVOL-MVP-001
- status: complete|needs_user_input|error
- started_at:
- ended_at:
- duration:
- objetivo: Implementar MVP ForestVol v5.1
- hitos_completados: [hito_0, hito_1, hito_0_5, hito_2, hito_3]
- artefactos_creados: []
- gates: {spec_exists: pass, plan_valid: pass, ...}
- pruebas: {coverage_backend: %, coverage_critical: %, tests_passed: N}
- error_volumetrico: null|%
- clasificacion_mvp: EXITOSO|ACEPTABLE|FALLIDO|PENDIENTE
- tokens_input:
- tokens_cached:
- tokens_output:
- costo_estimado:
- aprendizaje_registrado: true|false
- proximo_paso:
```

---

## 5. Estado canónico — `state.json`

Archivo: `.factory/runs/CYCLE-FORESTVOL-MVP-001/state.json`

```json
{
  "cycle_id": "CYCLE-FORESTVOL-MVP-001",
  "trace_id": "TRACE-001",
  "project_id": "forestvol-mvp",
  "status": "running",
  "objective": "Implementar MVP ForestVol v5.1",
  "product_expected": "Sistema ejecutable con docker-compose up, pipeline completo, trazabilidad.",
  "current_phase": "implement",
  "current_fase": "DEV_PHASE_3_NODEODM",
  "stack": {
    "backend": "Python3.11/FastAPI",
    "calibration": "OpenCV4.9+",
    "sfm": "NodeODM",
    "geometry": "Open3D0.18+",
    "frontend": "Vue.js3/Three.js",
    "infra": "Docker/DockerCompose"
  },
  "hitos": {
    "hito_0": "en_progreso",
    "hito_1": "pendiente",
    "hito_0_5": "pendiente",
    "hito_2": "pendiente",
    "hito_3": "pendiente"
  },
  "gates": {
    "spec_exists": "pass",
    "plan_valid": "pass",
    "tasks_atomic": "pass",
    "analyze_approved": "pass",
    "validation": "pending",
    "budget": "pass"
  },
  "artifacts": {
    "spec": "specs/forestvol-mvp/spec.md",
    "plan": "specs/forestvol-mvp/plan.md",
    "tasks": "specs/forestvol-mvp/tasks.md",
    "analyze": "specs/forestvol-mvp/analyze-report.md",
    "traceability": "specs/forestvol-mvp/traceability-matrix.md",
    "validation": "specs/forestvol-mvp/validation-report.md"
  },
  "usage": {
    "input_tokens": 0,
    "cached_input_tokens": 0,
    "output_tokens": 0,
    "tool_calls": 0,
    "estimated_cost": 0
  },
  "decisions": [],
  "risks": [],
  "last_block_reason": null,
  "missing_info": []
}
```

---

## 6. Sistema de trazabilidad — `trazabilidad/*.json`

### 6.1 Estructura obligatoria

```json
{
  "hito": {
    "id": "hito_0",
    "nombre": "Validación Técnica Inicial",
    "sprint": "Sprint 1",
    "fecha_objetivo": "TBD",
    "criterio_exito": "Docker + NodeODM operativos. Primera nube de puntos generada.",
    "estado": "en_progreso"
  },
  "etapas": [
    {
      "etapa_id": "hito_0_etapa_1",
      "nombre": "Configuración Docker Compose base",
      "estado": "completada",
      "fecha_completado": "ISO-8601",
      "partes_proyecto_utilizadas": [
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        ".env.example"
      ],
      "justificacion": "Se configuró la infraestructura Docker Compose con los 3 servicios. Python 3.11-slim por compatibilidad con Open3D 0.18. Node 20-alpine para frontend por tamaño reducido.",
      "que_se_hizo": "Creación de docker-compose.yml con los 3 servicios, redes internas, mapeo de volúmenes a /data. Verificación de que los 3 servicios levantan con docker-compose up.",
      "estado_resultante": "Infraestructura Docker operativa. Servicios responden en puertos 8000, 3000 y 3001. Volúmenes montados correctamente.",
      "ground_truth_disponible": false,
      "metricas": {
        "tiempo_implementacion_min": 45,
        "tests_pasados": 0,
        "errores_encontrados": 0,
        "cobertura_pct": null
      },
      "checklist": [
        { "item": "docker-compose.yml creado con 3 servicios", "completado": true },
        { "item": "Red interna forestvol-network configurada", "completado": true },
        { "item": "Volúmenes de datos mapeados en /data", "completado": true },
        { "item": "docker-compose up sin errores de build", "completado": true },
        { "item": "NodeODM responde en puerto 3001", "completado": true }
      ]
    }
  ],
  "resumen_hito": {
    "etapas_totales": 3,
    "etapas_completadas": 1,
    "porcentaje_avance": 33,
    "bloqueantes": [],
    "proxima_etapa": "hito_0_etapa_2 — Pipeline de carga de imágenes"
  }
}
```

### 6.2 Estados válidos

| Estado | Descripción |
|---|---|
| `"pendiente"` | No iniciada. |
| `"en_progreso"` | Actualmente siendo implementada. |
| `"completada"` | Finalizada con DoD cumplida. |
| `"bloqueada"` | Bloqueante externo impide avanzar. |
| `"con_contingencia"` | Completada con plan de contingencia activo. |

### 6.3 Regla de actualización

**Actualizar el JSON del hito ANTES de avanzar a la siguiente etapa.**  
No es válido actualizar al final de múltiples etapas. La actualización es atómica por etapa.

---

## 7. Routing de ciclo

| Tipo de trabajo | Ruta |
|---|---|
| Implementación de nueva fase | Ciclo SDD completo (8 fases en orden). |
| Corrección de bug en módulo | Identificar fase afectada → re-implementar task → re-validar → actualizar trazabilidad. |
| Cambio de parámetro NodeODM | Volver a Fase 3, documentar decisión en trazabilidad. |
| Ajuste de umbral de calibración | Volver a Fase 4, re-ejecutar tests de calibración. |
| Problema de malla | Volver a Fase 5, revisar parámetros de Poisson. |
| Error volumétrico fuera de rango | Revisar Fase 4 (calibración) y Fase 5 (malla) antes de Fase 6. |
| Cambio de componente frontend | Solo Fase 7, sin afectar backend. |
| Pregunta sin cambio de código | Responder desde evidencia. No implementar. |

---

## 8. Logs, tokens y costos

### 8.1 Archivos del ciclo

```
.factory/runs/CYCLE-FORESTVOL-MVP-001/
├── state.json              → estado canónico del ciclo
├── cycle_log.jsonl         → log de todos los eventos
├── usage_ledger.jsonl      → tokens, costo y tiempo por fase
├── context-cache.json      → índice de evidencia cargada
├── index-update-report.md  → archivos indexados en paso 10
├── cache-update-report.md  → cache actualizado en paso 10
└── final-report.md         → reporte final del ciclo
```

### 8.2 Métrica por fase

```json
{
  "cycle_id": "CYCLE-FORESTVOL-MVP-001",
  "phase": "implement",
  "fase_implementacion": "DEV_PHASE_2_UPLOAD",
  "task_id": "T-003",
  "started_at": "datetime",
  "ended_at": "datetime",
  "input_tokens": 0,
  "cached_input_tokens": 0,
  "output_tokens": 0,
  "tool_calls": 0,
  "cache_hit": false,
  "latency_ms": 0,
  "estimated_cost": 0,
  "status": "success|blocked|error"
}
```

### 8.3 Presupuesto

```yaml
budget:
  max_tool_calls: TBD
  max_duration_minutes: TBD
  max_retries: 1
  action_on_exceed: "needs_user_input"
```

---

## 9. Circuit breakers

| Breaker | Dispara si | Acción |
|---|---|---|
| `missing_analyze` | No existe `analyze-report.md` con `Proceed: yes` | Bloquear implementación. |
| `code_without_task` | Intento de escribir código sin task aprobada | Bloquear. Crear finding. |
| `dependency_violation` | Librería no en stack aprobado | Crear dependency request. Bloquear. |
| `test_failure_critical` | Prueba crítica falla | Bloquear cierre del hito. |
| `mesh_not_watertight_final` | `is_watertight() == False` tras 2 ciclos de reparación | Bloquear `get_volume()`. Registrar bloqueante. |
| `nodeodm_all_retries_failed` | Los 3 intentos de NodeODM fallan | `FAILED` + proponer Meshroom + `needs_user_input`. |
| `volume_error_gt25` | Error volumétrico > 25% en Hito 0.5 | Detener avance a Hito 2. Revisar calibración. |
| `budget_exceeded` | Tool calls superan presupuesto | Pausar. `needs_user_input`. |
| `scope_creep` | Cambio no trazado a task aprobada | Crear finding. Volver a analyze. |
| `traceability_not_updated` | Etapa completada sin actualizar JSON de trazabilidad | No avanzar a siguiente etapa. |
| `tool_error_repeated` | Herramienta falla 2 veces seguidas | `error` o fallback aprobado. |

---

## 10. Validaciones del ciclo

### 10.1 Validación SDD (antes de implementar)

- Existe `specs/forestvol-mvp/spec.md`.
- Existe `specs/forestvol-mvp/plan.md`.
- Existe `specs/forestvol-mvp/tasks.md`.
- Existe `specs/forestvol-mvp/analyze-report.md` con `Proceed: yes`.
- Todo RF-XX tiene al menos una task.
- Toda task tiene RF-XX de referencia.
- Todo RF funcional tiene prueba definida.

### 10.2 Validación técnica (por fase)

- Stack aprobado en `requirements.txt` y `package.json`.
- Configuración leída de `.env` (sin valores hardcodeados).
- API con contrato Pydantic v2 en `schemas.py`.
- Datos de prueba son sintéticos (no imágenes reales del cliente).
- Pruebas definidas antes de implementar cada módulo.

### 10.3 Validación de implementación (cierre de hito)

- Cada archivo creado mapea a una task aprobada.
- Cada task mapea a un RF-XX.
- Cada RF funcional tiene prueba ejecutada y aprobada.
- No hay cambios fuera del scope de las tasks aprobadas.
- Tests críticos pasan.
- `docker-compose build` exitoso.
- JSON de trazabilidad del hito tiene estado `"completada"` en todas las etapas.

---

## 11. Retries

```yaml
retry_policy:
  schema_error:
    max_retries: 1
    action: "retry_with_schema_feedback"
  tool_timeout:
    max_retries: 1
    action: "retry_or_degrade"
  test_failure:
    max_retries: 1
    action: "fix_if_task_scoped_else_block"
  nodeodm_failure:
    max_retries: 3
    action: "degrade_parameters_each_retry"
  mesh_not_watertight:
    max_retries: 2
    action: "reduce_density_and_regenerate"
  ambiguity:
    max_retries: 0
    action: "needs_user_input"
  policy_violation:
    max_retries: 0
    action: "block"
```

---

## 12. Observabilidad

### 12.1 Métricas del ciclo

| Categoría | Métricas |
|---|---|
| Productividad | Fases completadas, hitos cerrados, tasks implementadas. |
| Calidad | Cobertura de tests, pruebas aprobadas, errores encontrados. |
| Pipeline fotogramétrico | Confianza de calibración, porcentaje de agujeros en malla, watertightness. |
| Volumetría | Error volumétrico m³, clasificación MVP (EXITOSO/ACEPTABLE/FALLIDO). |
| IA / tokens | Tokens input/output/cache, costo estimado, tool calls. |
| Trazabilidad | Hitos completados, etapas con bloqueante, drift findings. |

### 12.2 Plantilla de mensaje al usuario — inicio (Paso 6)

```markdown
Inicio ciclo CYCLE-FORESTVOL-MVP-001.

Objetivo: Implementar MVP ForestVol v5.1 — pipeline fotogramétrico completo.
Stack: Python 3.11 / FastAPI / Vue.js 3 / Three.js / NodeODM / Open3D / OpenCV / Docker Compose.
Fases: 8 fases de implementación → 5 hitos.
Gates: spec_exists, plan_valid, tasks_atomic, analyze_approved, validation, budget.
Regla: no se escribe código sin task aprobada mapeada a RF-XX y prueba.
Trazabilidad: trazabilidad/{hito}.json + .factory/runs/CYCLE-001/.
```

### 12.3 Plantilla de mensaje al usuario — progreso

```markdown
Ciclo CYCLE-FORESTVOL-MVP-001: fase {{phase}} / {{fase_implementacion}}.
Hito activo: {{hito_activo}} — {{porcentaje}}% completado.
Último evento: {{summary}}
Bloqueos activos: {{blocks}}
Siguiente etapa: {{next}}
```

### 12.4 Plantilla de mensaje al usuario — cierre (Paso 11)

```markdown
Cierre ciclo CYCLE-FORESTVOL-MVP-001.

Estado: {{status}}
Hitos completados: {{hitos_completados}}
Artefactos: {{artifacts}}
Pruebas: cobertura backend {{cov_backend}}%, servicios críticos {{cov_critical}}%.
Error volumétrico: {{error_pct}}% (GT {{gt_disponible}})
Clasificación MVP: {{clasificacion}}
Tokens input/cache/output: {{tokens}}
Costo estimado: {{cost}}
Duración: {{duration}}
Aprendizaje registrado: {{learning}}
Próximo paso: {{next}}
```

---

## 13. Checklist de producción

### 13.1 Orquestador
- [x] Máquina de estados del ciclo definida.
- [x] Ciclo obligatorio de 12 pasos definido con gates.
- [x] Estado canónico `state.json` definido.
- [x] Routing de ciclo por tipo de trabajo definido.
- [x] Mensajes al usuario definidos (inicio, progreso, cierre).
- [x] Estados cerrados definidos.

### 13.2 Contexto
- [x] Indexación de evidencia definida (paso 2).
- [x] Lectura de aprendizajes definida (paso 3).
- [x] Actualización de índice/cache definida (paso 10).
- [x] Prohibición de cachear secretos definida.

### 13.3 Operabilidad
- [x] Logs JSONL por ciclo definidos.
- [x] Tokens/costos/tiempos definidos.
- [x] Circuit breakers definidos (11 breakers).
- [x] Validaciones SDD, técnicas y de implementación definidas.
- [x] Retries definidos por tipo de error.
- [x] Aprendizaje gobernado definido.
- [x] Observabilidad y métricas definidas.

### 13.4 Trazabilidad ForestVol
- [x] Estructura JSON de trazabilidad por hito definida.
- [x] Campos obligatorios de cada etapa definidos.
- [x] Estados válidos de etapas e hitos definidos.
- [x] Regla de actualización atómica definida.
- [x] Orden de implementación de 8 fases con puntos de actualización definidos.

### 13.5 Seguridad y entrega
- [x] Permisos mínimos por rol definidos (documento 03).
- [x] Dry-run definido para acciones con side effects.
- [x] Validación obligatoria por hito definida.
- [x] Definition of Done definida.
- [x] Cierre con evidencia y reporte final definidos.
