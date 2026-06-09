# Trazabilidad de Fuentes

## Vista lógica

### Diagrama de componentes
Fuentes utilizadas:
- [Requisitos.md](../back_data/Requisitos.md)
- [Casos de uso.md](../back_data/Casos%20de%20uso.md)
- [Objetivos y Alcance.md](../back_data/Objetivos%20y%20Alcance.md)
- [Estado del arte fotogrametría.md](../back_data/Estado%20del%20arte%20fotogrametr%C3%ADa.md)

Información extraída:
- carga de imágenes JPG/PNG
- calibración con guía física de 50x50 cm
- reconstrucción 3D con NodeODM/OpenDroneMap
- cálculo volumétrico con Open3D
- exportación JSON/CSV
- visualización 3D en SPA web

Supuestos:
- arquitectura en capas para separar presentación, negocio e infraestructura
- persistencia de metadatos y artefactos para trazabilidad de procesos

### Diagrama de clases de alto nivel
Fuentes utilizadas:
- [Requisitos.md](../back_data/Requisitos.md)
- [Casos de uso.md](../back_data/Casos%20de%20uso.md)

Información extraída:
- entidades de proceso, set de imágenes, calibración, malla y reporte
- relaciones entre carga, calibración, reconstrucción y exportación

Supuestos:
- modelado conceptual de alto nivel, no UML de implementación

## Vista de procesos

### Flujo principal end-to-end
Fuentes utilizadas:
- [Casos de uso.md](../back_data/Casos%20de%20uso.md)
- [Requisitos.md](../back_data/Requisitos.md)

Información extraída:
- UC-01 a UC-06
- secuencia de validación, calibración, reconstrucción, cálculo y exportación
- estados de error: formato inválido, guía no detectada, NodeODM no responde, malla defectuosa

Supuestos:
- la reconstrucción fotogramétrica se trata como trabajo asíncrono por job
- el backend mantiene estado intermedio para auditoría y reintentos

### Secuencia de excepción: guía no detectada
Fuentes utilizadas:
- [Requisitos.md](../back_data/Requisitos.md)
- [Casos de uso.md](../back_data/Casos%20de%20uso.md)

Información extraída:
- RF-05
- flujo alternativo de UC-02

Supuestos:
- el sistema bloquea el avance hasta intervención del operador

## Vista de desarrollo

### Estructura lógica del proyecto
Fuentes utilizadas:
- [Requisitos.md](../back_data/Requisitos.md)
- [Objetivos y Alcance.md](../back_data/Objetivos%20y%20Alcance.md)
- [Estado del arte fotogrametría.md](../back_data/Estado%20del%20arte%20fotogram%C3%ADa.md)

Información extraída:
- backend en Python 3.x
- frontend SPA desacoplado
- contenedorización de NodeODM
- uso de tecnologías open-source

Supuestos:
- monorrepo con separación interna por carpetas para facilitar el análisis académico

## Vista física

### Diagrama de despliegue
Fuentes utilizadas:
- [Requisitos.md](../back_data/Requisitos.md)
- [Estado del arte fotogrametría.md](../back_data/Estado%20del%20arte%20fotogram%C3%ADa.md)

Información extraída:
- despliegue en Docker de NodeODM
- ejecución eficiente en CPU estándar
- desacoplamiento frontend/backend

Supuestos:
- base de datos de metadatos y almacenamiento de artefactos en infraestructura local o servidor único
- no se asume uso obligatorio de nube pública

## Vista de escenarios

### Casos de uso críticos
Fuentes utilizadas:
- [Casos de uso.md](../back_data/Casos%20de%20uso.md)
- [Requisitos.md](../back_data/Requisitos.md)

Información extraída:
- UC-01 a UC-06
- trazabilidad entre requisitos funcionales y casos de uso

Supuestos:
- los casos de uso UC-05 y UC-06 se consideran críticos para validación operativa y entrega del valor

## Supuestos globales
- No se inventaron funcionalidades fuera de la documentación base.
- YOLOv8 se consideró como antecedente del estado del arte, pero no como componente obligatorio del núcleo funcional.
- La exportación y visualización se apoyan en los metadatos ya persistidos por el backend.

## Decisiones respaldadas
- OpenDroneMap/NodeODM como motor fotogramétrico por su soporte en Docker y ejecución en CPU.
- Open3D como librería principal de cálculo volumétrico.
- OpenCV para la calibración determinista de la guía física.
- SPA desacoplada para visualización y operación remota.
