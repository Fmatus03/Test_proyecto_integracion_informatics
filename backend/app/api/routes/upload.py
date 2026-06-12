"""ForestVol MVP — Upload Route."""

import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import UploadResponse, ErrorResponse
from app.services.image_validator import validate_image_security, generate_secure_filename

router = APIRouter()

MIN_IMAGES = int(os.getenv("MIN_IMAGES", "10"))
MAX_IMAGES = int(os.getenv("MAX_IMAGES", "50"))
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "data/uploads")

# Security limits
MAX_IMAGE_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_MB", "20")) * 1024 * 1024
MAX_SESSION_SIZE_BYTES = int(os.getenv("MAX_SESSION_SIZE_GB", "1")) * 1024 * 1024 * 1024

@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
    tags=["pipeline"],
    summary="Upload images",
    description="Validates and securely stores a batch of images for a new session.",
)
async def upload_images(files: list[UploadFile] = File(...)):
    """Handle image uploads securely."""
    if len(files) < MIN_IMAGES:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_code="INSUFFICIENT_IMAGES",
                message=f"Minimum {MIN_IMAGES} images required. Received: {len(files)}"
            ).model_dump(),
        )

    if len(files) > MAX_IMAGES:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_code="TOO_MANY_IMAGES",
                message=f"Maximum {MAX_IMAGES} images allowed. Received: {len(files)}"
            ).model_dump(),
        )

    session_id = str(uuid.uuid4())
    session_dir = Path(UPLOAD_PATH) / session_id
    
    # Do not create directory until we are sure we are processing
    
    total_size = 0
    errors = []
    valid_files = []

    for file in files:
        # First chunk is needed for magic bytes validation
        first_chunk = await file.read(2048)
        
        # Check if empty
        if not first_chunk:
            errors.append(f"File {file.filename} is empty")
            continue

        is_valid, error_msg = validate_image_security(file, first_chunk)
        if not is_valid:
            errors.append(f"{file.filename}: {error_msg}")
            continue

        # Go to end of file to get size, then seek back
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_IMAGE_SIZE_BYTES:
            errors.append(f"File {file.filename} exceeds {MAX_IMAGE_SIZE_BYTES} bytes")
            continue
            
        total_size += file_size
        
        if total_size > MAX_SESSION_SIZE_BYTES:
            return JSONResponse(
                status_code=413,
                content=ErrorResponse(
                    error_code="SESSION_SIZE_EXCEEDED",
                    message="Total upload size exceeds session limit"
                ).model_dump(),
            )
            
        valid_files.append(file)

    if errors:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_code="INVALID_IMAGE_FORMAT",
                message=f"Validation failed. Errors: {errors}"
            ).model_dump(),
        )
        
    # All files valid, securely store them
    session_dir.mkdir(parents=True, exist_ok=True)
    
    for file in valid_files:
        ext = Path(file.filename or "").suffix
        safe_filename = generate_secure_filename(ext)
        file_path = session_dir / safe_filename
        
        await file.seek(0)
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # 1MB chunks
                await out_file.write(content)
                
    return UploadResponse(
        session_id=session_id,
        image_count=len(valid_files),
        valid=True,
        errors=[],
        pipeline_state="VALIDATED",
    )
