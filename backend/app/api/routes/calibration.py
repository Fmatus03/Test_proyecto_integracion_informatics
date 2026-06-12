"""ForestVol MVP — Calibration Route."""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import CalibrationResponse, ErrorResponse
from app.services.calibration_service import calibrate_session

router = APIRouter()

UPLOAD_PATH = os.getenv("UPLOAD_PATH", "data/uploads")


@router.post(
    "/calibrate/{session_id}",
    response_model=CalibrationResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    tags=["pipeline"],
    summary="Calibrate spatial scale",
    description="Detect the 50×50 cm calibration guide and compute px/cm scale.",
)
async def calibrate(session_id: str):
    """Run spatial calibration on uploaded images for the given session."""
    session_dir = Path(UPLOAD_PATH) / session_id

    if not session_dir.exists() or not session_dir.is_dir():
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error_code="SESSION_NOT_FOUND",
                message=f"No upload session found with id '{session_id}'",
            ).model_dump(),
        )

    result = calibrate_session(session_dir)

    return CalibrationResponse(
        session_id=session_id,
        scale_px_per_cm=result.scale_px_per_cm,
        confidence=result.confidence,
        fallback_needed=not result.detected,
        side_px=result.side_px,
    )
