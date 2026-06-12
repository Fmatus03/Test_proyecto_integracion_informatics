"""ForestVol MVP — Volume Route."""

import csv
import io
import os
from pathlib import Path

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app.models.schemas import ErrorResponse, PipelineResultResponse, VolumeInfo
from app.services.volume_service import calculate_volume

router = APIRouter()

PROCESSED_PATH = os.getenv("PROCESSED_PATH", "data/processed")


def _get_volume_data(session_id: str) -> dict:
    """Helper to load data and run the volume calculation."""
    processed_dir = Path(PROCESSED_PATH) / session_id
    glb_path = processed_dir / "model.glb"
    
    if not processed_dir.exists() or not glb_path.exists():
        return {
            "success": False,
            "error_code": "NOT_FOUND",
            "message": f"Processed data or GLB not found for session {session_id}",
        }
        
    vol_result = calculate_volume(str(glb_path))
    if not vol_result.success:
        return {
            "success": False,
            "error_code": vol_result.error or "VOLUME_FAILED",
            "message": "Could not calculate volume from mesh",
        }
        
    return {
        "success": True,
        "volume": vol_result
    }


@router.get(
    "/results/{session_id}",
    response_model=PipelineResultResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["pipeline"],
    summary="Get volumetric results",
    description="Calculates and returns the final volume and dimensions of the mesh.",
)
async def get_results(session_id: str):
    """Return the calculated volume and bounding box in JSON format."""
    data = _get_volume_data(session_id)
    if not data["success"]:
        status_code = 404 if data["error_code"] == "NOT_FOUND" else 500
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error_code=data["error_code"],
                message=data["message"],
            ).model_dump(),
        )
        
    vol_result = data["volume"]
    return PipelineResultResponse(
        session_id=session_id,
        status="COMPLETED",
        images=0,  # Could read from uploads if needed, 0 for brevity in MVP results
        volume=VolumeInfo(
            volume_m3=round(vol_result.volume_m3, 3),
            length_m=round(vol_result.length_m, 2),
            width_m=round(vol_result.width_m, 2),
            height_m=round(vol_result.height_m, 2),
        )
    )


@router.get(
    "/export/{session_id}/csv",
    tags=["export"],
    summary="Export results as CSV",
)
async def export_csv(session_id: str):
    """Download the volume report in CSV format."""
    data = _get_volume_data(session_id)
    if not data["success"]:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error_code=data["error_code"],
                message=data["message"],
            ).model_dump(),
        )
        
    vol_result = data["volume"]
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Session ID", "Volume (m3)", "Length (m)", "Width (m)", "Height (m)"])
    writer.writerow([
        session_id, 
        round(vol_result.volume_m3, 3),
        round(vol_result.length_m, 2),
        round(vol_result.width_m, 2),
        round(vol_result.height_m, 2),
    ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{session_id}.csv"}
    )
