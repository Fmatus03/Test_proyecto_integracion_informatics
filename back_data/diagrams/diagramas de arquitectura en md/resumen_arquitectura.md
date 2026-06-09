# Resumen de la Arquitectura

## Resumen ejecutivo
La documentación analizada describe un sistema para calcular el volumen aparente de castillos de madera a partir de imágenes aéreas capturadas por drones. La arquitectura propuesta es una solución web desacoplada, con backend en Python, motor fotogramétrico en NodeODM/OpenDroneMap, calibración con OpenCV y cálculo volumétrico con Open3D.

## Análisis general del dominio
El problema pertenece principalmente a Ingeniería de Datos, con apoyo en visualización y una dimensión exploratoria de IA. El foco real no está en clasificar especies ni en integración empresarial, sino en automatizar la medición volumétrica, reducir riesgo operacional y mejorar la precisión frente a métodos manuales.

## Estilo arquitectónico propuesto
- Arquitectura en capas para la lógica de negocio.
- Arquitectura orientada a servicios internos para la orquestación del pipeline.
- Despliegue contenedorizado para el motor fotogramétrico.
- Interfaz SPA desacoplada del procesamiento analítico.

## Decisiones arquitectónicas
- Python como orquestador principal por interoperabilidad con OpenCV, Open3D y servicios de fotogrametría.
- NodeODM/OpenDroneMap como motor 3D por su compatibilidad con Docker y ejecución en CPU.
- Open3D como base del cálculo volumétrico por su API moderna y soporte geométrico.
- OpenCV para detectar la guía física de calibración de 50x50 cm.
- Frontend SPA con Three.js para visualización 3D y exposición de métricas.

## Riesgos técnicos
- La calidad de la calibración depende de la visibilidad real de la guía física en terreno.
- El rendimiento fotogramétrico puede variar según cantidad de imágenes, solapamiento y condiciones ambientales.
- La malla reconstruida puede requerir reparación topológica antes del cálculo.
- La documentación no fija el motor exacto de persistencia, por lo que la implementación final debe concretarlo.

## Inconsistencias detectadas
- En los casos de uso, UC-05 referencia RF-13 y RF-14, pero esos requisitos no aparecen definidos.
- En los criterios de aceptación aparece RF-009 en lugar de RF-09.
- El archivo de estado del arte usa el título “fotometría”, aunque el contenido corresponde a fotogrametría.
- El diagrama insertado en Casos de uso está embebido como imagen, no como Mermaid, por lo que no es reutilizable como trazado textual.

## Supuestos realizados
- El sistema se implementa como un monorrepo con separación clara de frontend, backend e infraestructura.
- La persistencia cubrirá metadatos y artefactos intermedios para auditoría y exportación.
- La reconstrucción 3D se tratará como un proceso asíncrono controlado por el backend.
- YOLOv8 queda como referencia de estado del arte y no como requisito funcional obligatorio.

## Recomendaciones
- Definir formalmente el motor de base de datos y el esquema de metadatos antes de implementar.
- Corregir la numeración de requisitos para cerrar trazabilidad total.
- Elaborar una batería de pruebas con imágenes reales y distintas condiciones de iluminación.
- Registrar métricas de precisión, tiempo de proceso y tasa de fallos topológicos.

## Próximos pasos antes de implementación
1. Normalizar y corregir la especificación de requisitos.
2. Prototipar el flujo mínimo de carga, calibración y exportación.
3. Validar integración con NodeODM en contenedor.
4. Medir precisión volumétrica frente a medición física de control.
5. Definir el esquema de persistencia y auditoría de procesos.