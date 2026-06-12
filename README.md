# 🌲 ForestVol MVP

Sistema integral automatizado para el cálculo volumétrico de pilas de madera a partir de vuelos fotogramétricos con drones. Diseñado con una arquitectura moderna que combina **FastAPI** (Python) en el backend, **Vue 3** en el frontend, y delegación asíncrona hacia **NodeODM** para el procesamiento pesado de SfM (Structure from Motion).

## Arquitectura

El sistema se compone de 3 servicios orquestados vía Docker:
1. **Frontend (Vue.js + Three.js):** SPA moderna que gestiona la carga de imágenes (*Drag & Drop*), el *polling* de estado, renderizado del modelo 3D en el navegador y descarga de reportes. Corre en el puerto `3000`.
2. **Backend (FastAPI):** Orquestador central. Gestiona la subida de archivos, procesa la calibración por Visión Artificial (ArUco), delega tareas a NodeODM, aplica algoritmos de Poisson Surface Reconstruction (`Open3D`) para tapar huecos en la malla, y calcula el volumen final exacto (`trimesh`). Corre en el puerto `8000`.
3. **NodeODM:** Motor fotogramétrico estandarizado que toma las imágenes aéreas y las transforma en una nube de puntos densa. Corre en el puerto `3001` (interno).

## Flujo Operativo

1. **Upload:** Se cargan mínimo 10 imágenes JPG del vuelo.
2. **Calibración:** El backend busca un marcador **ArUco (ID 0, dict 4X4_50)** en las fotos para obtener el factor de escala absoluto (píxel a centímetro). Esto hace al sistema robusto frente a pérdida de datos EXIF.
3. **Reconstrucción:** NodeODM genera la nube de puntos y malla inicial.
4. **Mallado Final:** El backend escala y cierra la malla (*watertight*) convirtiéndola en formato estandarizado `.glb`.
5. **Reporte:** El visor 3D renderiza la malla final. El volumen es extraído matemáticamente en `m³` y presentado al usuario.

## Requisitos Previos

- **Docker** y **Docker Compose** instalados.
- Se recomienda fuertemente asignar al menos **8GB de memoria RAM** al motor Docker para evitar interrupciones (*Out of Memory* - Exit code 137) al procesar mallas de alta resolución.

## Levantando el Proyecto 🚀

Para desplegar todo el sistema desde cero de manera local, ejecuta en la raíz del proyecto:

```bash
docker compose up --build -d
```

Una vez que los contenedores estén inicializados:
- **Aplicación Web:** Entra a `http://localhost:3000` en tu navegador.
- **API Docs (Swagger):** Entra a `http://localhost:8000/docs`.

### Ground Truth y Validación

El MVP se construyó alrededor de un caso de prueba controlado ("Castillo de Madera") con un volumen conocido de **447.616 m³**. Las lógicas de calibración han sido validadas contra estas imágenes, aislando el cálculo métrico de metadatos GPS potencialmente inestables.

## Licencia & Créditos
Proyecto desarrollado para facilitar la trazabilidad en la cadena de suministro forestal.
