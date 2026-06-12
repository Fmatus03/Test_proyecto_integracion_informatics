# Aprendizajes del Proyecto: ForestVol MVP

Este documento recoge las reflexiones, descubrimientos técnicos y decisiones de diseño tomadas durante la construcción del MVP de volumetría fotogramétrica forestal.

## 1. El Desafío de la Escala Métrica

Uno de los mayores retos en la fotogrametría automatizada sin RTK (Real Time Kinematic) es la falta de certeza métrica. Si dependemos puramente de los datos GPS incrustados en los EXIF de un dron estándar, el margen de error para medir el volumen de una pila de madera puede ser de hasta un 300%.
**Solución adoptada:** Se optó por una calibración basada puramente en Visión Artificial utilizando un marcador estandarizado (ArUco ID 0 de 50x50cm). La gran ventaja técnica es que ArUco se detecta con precisión sub-pixel, independientemente del dron utilizado.

## 2. Docker, Memoria y Procesamiento 3D (OOM)

Durante el ciclo de pruebas (E2E), se evidenció que la carga y manipulación de mallas 3D complejas dentro de Docker es increíblemente intensiva en memoria. NodeODM por sí solo consume abundante RAM al generar la nube de puntos, pero el proceso de `Poisson Surface Reconstruction` mediante `Open3D` también causa picos críticos que pueden provocar que el OS aborte el proceso (Exit code 137 - Out of Memory).
**Lección:** En futuros despliegues o pases a producción, el orquestador (backend FastAPI) debería correr en una instancia separada o garantizarse un clúster con alta disponibilidad de RAM para evitar cuellos de botella al operar concurrentemente.

## 3. Sinergia entre Bibliotecas (Open3D vs Trimesh)

En un principio, la intención era generar la malla y calcular el volumen en un único paso usando `Open3D`. 
**Descubrimiento:** `Open3D` es fenomenal para algoritmos pesados de reconstrucción topológica (Poisson). Sin embargo, para cálculo de masa, inercia y volúmenes exactos de sólidos, `trimesh` demostró ser matemáticamente superior y más amigable para empaquetar resultados, incluyendo la exportación nativa de Bounding Boxes (Cajas delimitadoras) orientadas que nos proporcionaron el Largo, Ancho y Alto exacto de la pila de madera. 

## 4. El Rol del Frontend

Construir la SPA en Vue 3 con micro-interacciones (Polling y Barra de Progreso) probó ser esencial. El backend tiene tareas bloqueantes y asíncronas de largo aliento. Un cliente sin *polling* agotaría el tiempo de espera (Timeout) del navegador, rompiendo la experiencia de usuario. 
La delegación del visor 3D al cliente (mediante `Three.js`) descargó al servidor de renderizado, permitiendo que el navegador use la GPU local del operario para inspeccionar el modelo generado.
