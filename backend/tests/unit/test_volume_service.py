"""Unit tests for the volume calculation service."""

from pathlib import Path
import trimesh
import pytest

from app.services.volume_service import calculate_volume


def _create_synthetic_box_mesh(output_path: Path, length: float, width: float, height: float):
    """Create a box mesh with exact dimensions and save as GLB."""
    # trimesh.creation.box creates a box centered at origin
    box = trimesh.creation.box(extents=[length, width, height])
    box.export(str(output_path), file_type="glb")


class TestVolumeService:
    """Tests for volumetric calculations."""

    def test_calculate_volume_missing_file(self):
        """Should fail gracefully if GLB does not exist."""
        result = calculate_volume("nonexistent.glb")
        assert result.success is False
        assert result.error == "MESH_NOT_FOUND"

    def test_calculate_exact_volume_of_synthetic_box(self, tmp_path: Path):
        """A 10x5x2 box should yield exactly 100 cubic meters."""
        glb_path = tmp_path / "box.glb"
        length, width, height = 10.0, 5.0, 2.0
        expected_volume = length * width * height
        
        _create_synthetic_box_mesh(glb_path, length, width, height)

        result = calculate_volume(str(glb_path))
        
        assert result.success is True
        assert abs(result.volume_m3 - expected_volume) < 0.001
        
        # Dimensions are sorted descending: [10.0, 5.0, 2.0]
        assert abs(result.length_m - 10.0) < 0.001
        assert abs(result.width_m - 5.0) < 0.001
        assert abs(result.height_m - 2.0) < 0.001

    def test_ground_truth_accuracy(self, tmp_path: Path):
        """Test accuracy reporting against the known Ground Truth of the wood stack.
        
        The user provided a Ground Truth of 447.616 cubic meters for the timber stockpile
        (32 logs of 13.988 m3 each).
        In this test, we create a synthetic block of that exact volume to ensure 
        the service computes it correctly. In reality, the photogrammetry will yield
        a slightly different volume and we'd calculate the error %.
        """
        glb_path = tmp_path / "ground_truth_mock.glb"
        
        # We need a box that gives 447.616 m3. Let's do 10 x 10 x 4.47616
        length, width, height = 10.0, 10.0, 4.47616
        expected_volume = 447.616
        
        _create_synthetic_box_mesh(glb_path, length, width, height)
        
        result = calculate_volume(str(glb_path))
        
        assert result.success is True
        assert abs(result.volume_m3 - expected_volume) < 0.001
        
        # Simulating how accuracy would be calculated if needed:
        error_percentage = abs(result.volume_m3 - expected_volume) / expected_volume * 100.0
        assert error_percentage < 0.01  # Error should be near zero for the exact box
