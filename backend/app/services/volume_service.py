"""ForestVol MVP — Volume calculation service.

Loads the exported 3D mesh (model.glb), calculates its physical dimensions
(bounding box), and integrates its watertight volume in cubic meters.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import trimesh

logger = logging.getLogger(__name__)


@dataclass
class VolumeResult:
    """Result of the volumetric calculation."""
    success: bool
    volume_m3: float
    length_m: float
    width_m: float
    height_m: float
    error: str | None = None


def calculate_volume(glb_path: str) -> VolumeResult:
    """Calculate the volume and dimensions of a GLB mesh.
    
    The mesh is expected to already be in meters (scaled by mesh_service).
    Returns the volume in cubic meters and bounding box dimensions.
    """
    path = Path(glb_path)
    if not path.exists():
        logger.error("Mesh file not found: %s", glb_path)
        return VolumeResult(False, 0.0, 0.0, 0.0, 0.0, "MESH_NOT_FOUND")

    try:
        # Load mesh
        mesh = trimesh.load(str(path), force='mesh')
        
        # In a real forestry scenario, we might want to subtract the ground plane.
        # But for this MVP, the mesh generated from the drone should primarily 
        # enclose the timber stockpile.
        # Trimesh volume integration is exact for watertight meshes.
        volume = mesh.volume
        
        # We can extract the oriented bounding box or axis-aligned bounding box.
        # Oriented Bounding Box (OBB) gives us the true length/width/height 
        # regardless of how it's rotated in the XY plane.
        obb_extents = mesh.bounding_box_oriented.extents
        
        # Sort dimensions to intelligently assign length/width/height
        # Usually: length > width > height (for a typical stack, though height can vary)
        # Let's just sort them. The smallest is likely height or width, largest is length.
        dims = sorted(obb_extents, reverse=True)
        length = dims[0]
        width = dims[1]
        height = dims[2]

        # Alternatively, if we trust the Z axis to be up:
        # aabb_extents = mesh.extents
        # length, width, height = aabb_extents[0], aabb_extents[1], aabb_extents[2]

        return VolumeResult(
            success=True,
            volume_m3=float(volume),
            length_m=float(length),
            width_m=float(width),
            height_m=float(height),
            error=None
        )

    except Exception as exc:
        logger.exception("Failed to calculate volume for %s", glb_path)
        return VolumeResult(False, 0.0, 0.0, 0.0, 0.0, "CALCULATION_ERROR")
