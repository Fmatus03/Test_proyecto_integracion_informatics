"""ForestVol MVP — End to End Pipeline Test.

This test simulates the entire lifecycle of a request from the frontend:
1. Upload images
2. Calibrate (Mocked for speed in E2E, but tests the route)
3. Reconstruct (Mocked NodeODM)
4. Meshing (Mocked Poisson)
5. Volume Calculation (Tests the route)
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app

client = TestClient(app)

def test_full_pipeline_flow(tmp_path, monkeypatch):
    """Test the complete happy path of the MVP."""
    # 1. Mock the environment paths
    upload_dir = tmp_path / "uploads"
    processed_dir = tmp_path / "processed"
    export_dir = tmp_path / "exports"
    
    upload_dir.mkdir()
    processed_dir.mkdir()
    export_dir.mkdir()
    
    monkeypatch.setenv("UPLOAD_PATH", str(upload_dir))
    monkeypatch.setenv("PROCESSED_PATH", str(processed_dir))
    monkeypatch.setenv("EXPORT_PATH", str(export_dir))

    # 1. Upload Images
    # Create fake JPGs
    files = []
    for i in range(10):
        img_path = tmp_path / f"test_{i}.jpg"
        img_path.write_bytes(b"fake_image_data")
        files.append(("files", (f"test_{i}.jpg", open(img_path, "rb"), "image/jpeg")))

    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # 2. Calibration (Mock the actual ArUco logic to avoid needing a real image here)
    # We will mock `process_calibration` to just return a scale
    async def mock_process_calibration(sess_id, sess_dir):
        return {"scale_px_per_cm": 2.5, "confidence": 0.95, "fallback_used": False}
    
    monkeypatch.setattr("app.api.routes.calibration.process_calibration", mock_process_calibration)
    
    response = client.post(f"/api/calibrate/{session_id}")
    assert response.status_code == 200
    scale = response.json()["scale_px_per_cm"]
    assert scale == 2.5

    # 3. Reconstruction (Mock NodeODM)
    async def mock_run_reconstruction(sess_id, sess_dir):
        # Create fake odm_textured_model_geo.obj
        obj_dir = processed_dir / sess_id / "odm_texturing"
        obj_dir.mkdir(parents=True)
        (obj_dir / "odm_textured_model_geo.obj").write_text("fake obj content")
        return {"success": True, "task_uuid": "fake-uuid", "status": "COMPLETED", "output_dir": str(processed_dir / sess_id)}
        
    monkeypatch.setattr("app.api.routes.reconstruction.run_reconstruction", mock_run_reconstruction)
    
    response = client.post(f"/api/reconstruct/{session_id}?scale_px_per_cm={scale}")
    assert response.status_code == 200

    # 4. Mesh Generation (Mock open3d/trimesh logic)
    async def mock_process_mesh(sess_id, sess_dir, s):
        # Create fake model.glb
        (processed_dir / sess_id / "model.glb").write_bytes(b"fake glb")
        return {"vertices": 100, "faces": 50, "is_watertight": True, "path": str(processed_dir / sess_id / "model.glb")}

    monkeypatch.setattr("app.api.routes.mesh.process_mesh", mock_process_mesh)
    
    response = client.post(f"/api/mesh/{session_id}?scale_px_per_cm={scale}")
    assert response.status_code == 200

    # 5. Volume Calculation (Mock volume logic since we have a fake GLB)
    async def mock_calculate_volume(sess_id, sess_dir, gt):
        return {
            "volume_m3": 445.0,
            "length_m": 10.0,
            "width_m": 5.0,
            "height_m": 8.9,
            "ground_truth_m3": gt,
            "error_percentage": abs(445.0 - gt) / gt * 100 if gt else None
        }

    monkeypatch.setattr("app.api.routes.volume.calculate_volume", mock_calculate_volume)
    
    # Request final results
    response = client.get(f"/api/results/{session_id}?ground_truth_m3=447.616")
    assert response.status_code == 200
    data = response.json()
    assert "volume" in data
    assert data["volume"]["volume_m3"] == 445.0
    assert data["volume"]["ground_truth_m3"] == 447.616
    assert data["volume"]["error_percentage"] is not None

    # Export CSV
    response = client.get(f"/api/export/{session_id}/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
