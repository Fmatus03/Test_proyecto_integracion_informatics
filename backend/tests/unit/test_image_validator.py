"""Unit tests for the image validator service."""

import pytest
from unittest.mock import MagicMock
from fastapi import UploadFile
from pathlib import Path
from app.services.image_validator import validate_image_security, generate_secure_filename

def test_generate_secure_filename():
    """Test UUID filename generation."""
    filename = generate_secure_filename(".jpg")
    assert filename.endswith(".jpg")
    assert len(filename) == 32 + 4  # 32 chars UUID hex + ".jpg"
    assert ".." not in filename

def create_mock_upload_file(filename: str) -> UploadFile:
    file = MagicMock(spec=UploadFile)
    file.filename = filename
    return file

def test_validate_image_security_valid_jpeg():
    """Test validation with a valid JPEG magic byte sequence."""
    file = create_mock_upload_file("test.jpg")
    # Standard JPEG magic bytes: FF D8 FF E0
    jpeg_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06'
    
    is_valid, msg = validate_image_security(file, jpeg_bytes)
    assert is_valid is True
    assert msg == ""

def test_validate_image_security_invalid_extension():
    """Test validation rejection for invalid extensions."""
    file = create_mock_upload_file("test.pdf")
    jpeg_bytes = b'\xff\xd8\xff\xe0'
    
    is_valid, msg = validate_image_security(file, jpeg_bytes)
    assert is_valid is False
    assert "Invalid extension" in msg

def test_validate_image_security_invalid_magic_bytes():
    """Test validation rejection for mismatched magic bytes (e.g. text file renamed to .jpg)."""
    file = create_mock_upload_file("fake_image.jpg")
    text_bytes = b'<html><body>Hello world</body></html>'
    
    is_valid, msg = validate_image_security(file, text_bytes)
    assert is_valid is False
    assert "Invalid content type" in msg

def test_validate_image_security_path_traversal_filename():
    """Test validation handles path traversal strings gracefully by using suffix logic."""
    file = create_mock_upload_file("../../../etc/passwd.jpg")
    jpeg_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01'
    
    is_valid, msg = validate_image_security(file, jpeg_bytes)
    assert is_valid is True  # The extension is .jpg, and the content is JPEG. The filename will be ignored on save anyway.
