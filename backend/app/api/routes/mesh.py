"""ForestVol MVP — Mesh Route."""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import MeshResponse, ErrorResponse
from app.services.mesh_service import process_point_cloud

router = APIRouter()

PROCESSED_PATH = os.getenv("PROCESSED_PATH", "data/processed")


@router.post(
    "/mesh/{session_id}",
    response_model=MeshResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["pipeline"],
    summary="Generate 3D Mesh from Point Cloud",
    description="Loads a point cloud, runs Poisson reconstruction, repairs holes, and scales the result to meters.",
)
async def generate_mesh(
    session_id: str,
    scale_px_per_cm: float = Query(
        ...,
        description="The spatial scale factor obtained from the calibration phase.",
        gt=0.0
    ),
):
    """Process a point cloud into a scaled, watertight GLB mesh."""
    processed_dir = Path(PROCESSED_PATH) / session_id

    if not processed_dir.exists() or not processed_dir.is_dir():
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error_code="SESSION_NOT_FOUND",
                message=f"No processed session found with id '{session_id}'",
            ).model_dump(),
        )

    result = process_point_cloud(session_id, processed_dir, scale_px_per_cm)

    if not result.success:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error_code=result.error or "MESH_PROCESSING_FAILED",
                message="Failed to generate 3D mesh from point cloud",
            ).model_dump(),
        )

    return MeshResponse(
        session_id=session_id,
        glb_path=result.glb_path,
        is_watertight=result.is_watertight,
        vertex_count=result.vertex_count,
        face_count=result.face_count,
    )
