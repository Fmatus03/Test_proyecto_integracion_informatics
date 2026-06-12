"""ForestVol MVP — Image validation service with strict security constraints."""

import os
import uuid
import magic
from pathlib import Path
from fastapi import UploadFile

# Use configured boundaries or reasonable defaults
MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "20"))
MAX_SESSION_SIZE_GB = int(os.getenv("MAX_SESSION_SIZE_GB", "1"))

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def validate_image_security(file: UploadFile, first_chunk: bytes) -> tuple[bool, str]:
    """
    Validate the image using strict security rules:
    - Check file extension
    - Check Magic Bytes (MIME) using python-magic
    """
    # 1. Validate Extension
    # Using Path.name ensures we strip any directory traversal sequences
    # However, UploadFile.filename should be just the basename in FastAPI.
    filename = Path(file.filename or "").name.lower()
    ext = Path(filename).suffix
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid extension {ext}. Only JPG and PNG are supported."

    # 2. Validate MIME via Magic Bytes
    # We use python-magic to inspect the actual content, ignoring the client-provided content-type
    try:
        mime_type = magic.from_buffer(first_chunk, mime=True)
    except Exception:
        return False, "Could not determine file type from content."

    if mime_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid content type {mime_type}. Only image/jpeg and image/png are supported."

    return True, ""

def generate_secure_filename(ext: str) -> str:
    """Generate a random UUID filename to prevent directory traversal and metadata exploits."""
    return f"{uuid.uuid4().hex}{ext.lower()}"
