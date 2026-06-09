# Vista de Procesos

## Descripción general
La vista de procesos modela el comportamiento dinámico del sistema. El flujo principal es predominantemente secuencial, pero el procesamiento fotogramétrico se trata como una operación larga y asíncrona sobre un motor externo, con actualizaciones de estado al backend y a la interfaz.

## Procesos críticos
- Carga y validación de imágenes.
- Detección de la guía física y cálculo de escala.
- Envío del set a NodeODM para reconstrucción 3D.
- Verificación de integridad de la malla y cálculo volumétrico.
- Generación de métricas y exportación de reportes.

## Flujo principal end-to-end
```mermaid
sequenceDiagram
    actor Operador as Operador Forestal
    participant UI as SPA Web
    participant API as Backend Python
    participant CV as OpenCV
    participant ODM as NodeODM
    participant G3D as Open3D
    participant DB as Persistencia

    Operador->>UI: Carga set de imágenes JPG/PNG
    UI->>API: Enviar archivos
    API->>DB: Registrar proceso e imágenes
    API-->>UI: Confirmación de carga

    API->>CV: Detectar guía 50x50 cm
    CV-->>API: Escala aplicada / advertencia
    API->>ODM: Crear job de reconstrucción 3D
    ODM-->>API: Job aceptado
    loop Seguimiento del job
        API->>ODM: Consultar estado
        ODM-->>API: Estado y artefactos
    end

    API->>G3D: Cargar malla y calcular volumen
    G3D-->>API: Volumen m3 y validación de malla
    API->>DB: Guardar resultado y metadatos
    API-->>UI: Actualizar panel de métricas
    Operador->>UI: Exportar reporte
    UI->>API: Solicitar JSON o CSV
    API-->>UI: Archivo descargable
```

## Sincronía y asincronía
- Síncrono: carga de archivos, validación de formato, consulta de resultados, exportación.
- Asíncrono: reconstrucción fotogramétrica en NodeODM y actualización progresiva del estado del proceso.

## Eventos importantes
- Archivo rechazado por formato inválido.
- Guía no detectada en el set de imágenes.
- NodeODM no responde o falla el job.
- Malla no estanca y requiere reparación o aborta el cálculo.
- Resultado volumétrico calculado y disponible.

## Manejo transaccional
La unidad transaccional principal es el proceso fotogramétrico completo. El backend debe persistir estados intermedios para permitir reintentos y auditoría del resultado. Los artefactos 3D se tratan como salidas derivadas del job, no como datos editables manualmente.

## Secuencia de excepción: guía no detectada
```mermaid
sequenceDiagram
    actor Operador as Operador Forestal
    participant UI as SPA Web
    participant API as Backend Python
    participant CV as OpenCV

    Operador->>UI: Inicia procesamiento
    UI->>API: Solicitud de calibración
    API->>CV: Buscar guía física
    CV-->>API: No encontrada
    API-->>UI: Advertencia y bloqueo del avance
    UI-->>Operador: Solicitar recarga o confirmación
```

## Secuencia de excepción: malla defectuosa
```mermaid
sequenceDiagram
    participant API as Backend Python
    participant ODM as NodeODM
    participant G3D as Open3D

    API->>ODM: Solicitar reconstrucción
    ODM-->>API: Nube de puntos y malla
    API->>G3D: Verificar watertightness
    G3D-->>API: Malla no cerrada
    API-->>ODM: Registrar incidente y detener cálculo
```

## Observaciones de diseño
El sistema debe tolerar fallas parciales y conservar trazabilidad de estados. Esto es importante porque los requisitos aceptan la detección tardía de errores en calibración, topología de malla y conectividad del motor de fotogrametría.
