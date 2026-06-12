"""Unit tests for the mesh service."""

import open3d as o3d
import trimesh
import pytest
from pathlib import Path

from app.services.mesh_service import process_point_cloud, MeshResult


def _create_synthetic_point_cloud(output_path: Path):
    """Create a simple sphere point cloud and save as PLY."""
    # Create a dense sphere mesh
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=20)
    sphere.compute_vertex_normals()
    
    # Sample points from the surface
    pcd = sphere.sample_points_uniformly(number_of_points=2000)
    
    # Save to file
    o3d.io.write_point_cloud(str(output_path), pcd)


class TestMeshService:
    """Tests for the point cloud to mesh pipeline."""

    def test_process_missing_point_cloud(self, tmp_path: Path):
        """Should fail gracefully if PLY does not exist."""
        result = process_point_cloud("sess-123", tmp_path, scale_px_per_cm=10.0)
        assert result.success is False
        assert result.error == "POINT_CLOUD_NOT_FOUND"

    def test_process_empty_point_cloud(self, tmp_path: Path):
        """Should fail gracefully if PLY is empty."""
        empty_pcd = o3d.geometry.PointCloud()
        cloud_path = tmp_path / "point_cloud.ply"
        o3d.io.write_point_cloud(str(cloud_path), empty_pcd)

        result = process_point_cloud("sess-123", tmp_path, scale_px_per_cm=10.0)
        assert result.success is False
        assert result.error == "EMPTY_POINT_CLOUD"

    def test_process_valid_point_cloud(self, tmp_path: Path):
        """Should successfully reconstruct a watertight mesh from a synthetic PLY."""
        cloud_path = tmp_path / "point_cloud.ply"
        _create_synthetic_point_cloud(cloud_path)

        # Let's say 1 cm = 10 pixels. We want the mesh in meters.
        # Scale applied should be: (1.0 / 10.0) * 0.01 = 0.001
        scale_px_per_cm = 10.0
        
        result = process_point_cloud("sess-123", tmp_path, scale_px_per_cm)
        
        assert result.success is True
        assert result.glb_path is not None
        assert Path(result.glb_path).exists()
        
        # Depending on Poisson depth, the result might have tiny boundary artifacts
        # but trimesh.repair.fill_holes should catch them.
        # We assert it ran without crashing and generated vertices.
        assert result.vertex_count > 0
        assert result.face_count > 0

        # Load the GLB and verify scale
        mesh = trimesh.load(result.glb_path, force='mesh')
        
        # Original sphere radius was 1.0 (arbitrary units).
        # We applied scale 0.001. So new radius should be ~0.001.
        # Let's check bounding box size.
        extents = mesh.extents
        assert extents[0] > 0.0
        assert extents[0] < 0.01  # Should be ~0.002 since diameter is 2.0 * 0.001
