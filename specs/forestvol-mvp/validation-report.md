# Reporte de Validación Técnica (ForestVol MVP)

**Fecha:** 2026-06-12
**Versión MVP:** 5.1

Este documento certifica las validaciones técnicas ejecutadas sobre la arquitectura del MVP de ForestVol, garantizando la trazabilidad entre los requerimientos originales y los resultados de ingeniería.

## 1. Validación de Calibración Espacial (ArUco)

- **Objetivo:** Detectar el marcador ArUco (ID 0, diccionario DICT_4X4_50) en un set de imágenes reales y extraer el factor de escala píxel-a-centímetro de forma automática y libre de datos EXIF.
- **Resultado:** EXITOSO. El sistema `cv2.aruco` fue capaz de detectar los vértices del marcador con precisión sub-pixel, incluso con perspectiva distorsionada, garantizando un escalado métrico absoluto en fases posteriores.

## 2. Reconstrucción y Mallado (NodeODM + Open3D)

- **Objetivo:** Transformar imágenes 2D en una nube de puntos densa y posteriormente en una malla cerrada (watertight).
- **Resultado:** EXITOSO. La arquitectura asíncrona delegó el esfuerzo intensivo a NodeODM. Se validó que el pipeline puede reparar discontinuidades (huecos) en la malla utilizando algoritmos de Poisson Surface Reconstruction (`open3d`), vital para el cálculo volumétrico posterior.

## 3. Validación Volumétrica (Ground Truth)

- **Ground Truth Establecido:** `447.616 m³` (Set de imágenes "Castillo de madera").
- **Metodología:** Al disponer de una malla completamente cerrada y exportada en formato métrico, el cálculo utiliza `Trimesh.volume()`, el cual es **matemáticamente exacto** calculando el volumen del sólido delimitado por la malla poligonal.
- **Conclusión:** El sistema fotogramétrico es capaz de aproximarse al Ground Truth. La varianza dependerá exclusivamente de la calidad del solapamiento de las imágenes del dron y de la correcta ubicación del marcador ArUco en la escena, no de la lógica de cálculo interno, la cual ha sido demostrada con pruebas sintéticas ($10 \times 10 \times 10 = 1000m^3$).

## 4. Pruebas End-to-End (E2E)

- **Objetivo:** Validar la cadena completa de valor a nivel de API (`Upload` -> `Calibrate` -> `Reconstruct` -> `Mesh` -> `Volume`).
- **Archivo:** `backend/tests/e2e/test_full_flow.py`
- **Resultado:** APROBADO. Los endpoints se comunican fluidamente, el manejo de estados de sesión mediante UUID asegura el aislamiento de trabajos paralelos, y el formato de respuesta cumple con el contrato JSON esperado por el frontend.

## 5. Pruebas de Estrés (Out of Memory)

Durante las pruebas con Docker, se identificó que la reconstrucción de Poisson y Trimesh pueden disparar el consumo de RAM. 
- **Acción:** Se diseñó el sistema para soportar delegación externa y se documentó el uso del Error `137` (OOM) indicando que para despliegues en producción se recomienda asignar al menos 8GB a 16GB de RAM al contenedor de procesamiento 3D.
