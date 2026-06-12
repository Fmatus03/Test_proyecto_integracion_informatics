# Matriz de Trazabilidad (ForestVol MVP)

Esta matriz vincula los Requerimientos Funcionales (RF) definidos en la especificación inicial con los tests unitarios y de integración que validan su cumplimiento.

| Requerimiento Funcional | Descripción Corta | Módulo Afectado | Tests Automatizados que lo Validan |
| :--- | :--- | :--- | :--- |
| **RF-01** | Subida en bloques (Chunks) | `upload.py`, `image_validator.py` | `test_image_validator.py::test_validate_image_security_valid_jpeg` |
| **RF-02** | Rechazo Rápido (File Security) | `image_validator.py` | `test_image_validator.py::test_validate_image_security_invalid_extension`, `test_validate_image_security_invalid_magic_bytes` |
| **RF-03** | Calibración Automática | `calibration_service.py` | `test_calibration_service.py::TestArucoDetection` y `TestGuideDetectionPriority` |
| **RF-04** | Error de Escala ≤ 5% | `calibration_service.py` | `test_calibration_service.py::TestArucoDetection::test_aruco_scale_calculation` |
| **RF-05** | Alerta de Calibración Fallida | `calibration_service.py` | `test_calibration_service.py::TestContourFallback::test_no_detection_on_blank` |
| **RF-06** | Integración SfM (NodeODM) | `nodeodm_client.py` | *Verificado manualmente mediante flujo E2E (requiere levantar NodeODM real)* |
| **RF-07** | Generación de Malla Watertight | `mesh_service.py` | `test_mesh_service.py::test_process_valid_point_cloud` |
| **RF-08** | Cálculo Volumétrico en m³ | `volume_service.py` | `test_volume_service.py::test_calculate_exact_volume_of_synthetic_box` |
| **RF-09** | Exportación de Resultados | `volume.py` | Endpoint validado estáticamente, reportes en CSV/JSON |
| **GT-01** | Validación Ground Truth (447.616 m³) | `test_volume_service.py` | `test_volume_service.py::test_ground_truth_accuracy` |
