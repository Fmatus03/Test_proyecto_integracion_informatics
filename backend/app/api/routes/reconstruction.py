"""ForestVol MVP — Reconstruction Route."""

import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.schemas import ReconstructionResponse, ErrorResponse
from app.services.nodeodm_client import run_reconstruction

router = APIRouter()

UPLOAD_PATH = os.getenv("UPLOAD_PATH", "data/uploads")


@router.post(
    "/reconstruct/{session_id}",
    response_model=ReconstructionResponse,
    responses={
        404: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    tags=["pipeline"],
    summary="Start 3D reconstruction",
    description="Submit uploaded images to NodeODM for SfM/MVS processing.",
)
async def reconstruct(session_id: str):
    """Start the photogrammetric reconstruction pipeline via NodeODM."""
    session_dir = Path(UPLOAD_PATH) / session_id

    if not session_dir.exists() or not session_dir.is_dir():
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error_code="SESSION_NOT_FOUND",
                message=f"No upload session found with id '{session_id}'",
            ).model_dump(),
        )

    image_extensions = {".jpg", ".jpeg", ".png"}
    image_count = sum(
        1 for f in session_dir.iterdir()
        if f.suffix.lower() in image_extensions
    )

    if image_count == 0:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error_code="NO_IMAGES",
                message="Session directory contains no valid images",
            ).model_dump(),
        )

    result = await run_reconstruction(session_id, session_dir)

    if not result["success"]:
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error_code=result.get("error", "RECONSTRUCTION_FAILED"),
                message=f"Reconstruction failed with status: {result['status']}",
            ).model_dump(),
        )

    return ReconstructionResponse(
        session_id=session_id,
        task_uuid=result["task_uuid"],
        status=result["status"],
        success=True,
        output_dir=result["output_dir"],
    )
