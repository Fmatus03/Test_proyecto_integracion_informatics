"""Unit tests for the calibration service.

Tests cover both ArUco detection and contour fallback using synthetic images.
"""

import numpy as np
import cv2
import pytest
from pathlib import Path

from app.services.calibration_service import (
    _detect_aruco_in_image,
    _detect_contour_in_image,
    _detect_guide_in_image,
    calibrate_session,
    CalibrationResult,
    GUIDE_SIDE_CM,
    ARUCO_DICT_TYPE,
    ARUCO_TARGET_ID,
)


def _make_aruco_image(
    img_size: int = 800,
    marker_size_px: int = 200,
) -> np.ndarray:
    """Create a synthetic image containing ArUco marker ID 0."""
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_TYPE)
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, ARUCO_TARGET_ID, marker_size_px)

    # Place marker on a white canvas
    canvas = np.full((img_size, img_size, 3), 240, dtype=np.uint8)
    offset = (img_size - marker_size_px) // 2
    # Marker is grayscale, expand to BGR
    canvas[offset:offset + marker_size_px, offset:offset + marker_size_px] = marker_img[:, :, np.newaxis]

    return canvas


def _make_square_image(
    img_size: int = 600,
    square_size: int = 200,
    bg_color: int = 30,
    fg_color: int = 240,
) -> np.ndarray:
    """Create a synthetic BGR image with a white square on dark background."""
    img = np.full((img_size, img_size, 3), bg_color, dtype=np.uint8)
    offset = (img_size - square_size) // 2
    img[offset:offset + square_size, offset:offset + square_size] = fg_color
    return img


class TestArucoDetection:
    """Tests for the ArUco marker detection path."""

    def test_detects_aruco_marker(self):
        """A clean ArUco marker ID 0 should be detected."""
        image = _make_aruco_image(marker_size_px=200)
        result = _detect_aruco_in_image(image)

        assert result is not None
        assert result.detected is True
        assert result.method == "aruco"
        assert result.confidence >= 0.90
        assert abs(result.side_px - 200.0) < 20.0

    def test_aruco_scale_calculation(self):
        """Scale should equal side_px / 50 cm."""
        image = _make_aruco_image(marker_size_px=150)
        result = _detect_aruco_in_image(image)

        assert result is not None
        expected_scale = result.side_px / GUIDE_SIDE_CM
        assert abs(result.scale_px_per_cm - expected_scale) < 0.01

    def test_no_aruco_on_blank(self):
        """A uniform image should yield no ArUco detection."""
        blank = np.full((400, 400, 3), 128, dtype=np.uint8)
        result = _detect_aruco_in_image(blank)
        assert result is None


class TestContourFallback:
    """Tests for the contour-based fallback detection."""

    def test_detects_square(self):
        """A clear white square on a dark background should be detected."""
        image = _make_square_image(square_size=200)
        result = _detect_contour_in_image(image)

        assert result is not None
        assert result.detected is True
        assert result.method == "contour"
        assert result.confidence >= 0.90

    def test_no_detection_on_blank(self):
        """A uniform image should yield no detection."""
        blank = np.full((400, 400, 3), 128, dtype=np.uint8)
        result = _detect_contour_in_image(blank)
        assert result is None

    def test_rejects_rectangle(self):
        """A long rectangle (aspect ratio far from 1.0) should not match."""
        img = np.full((600, 600, 3), 30, dtype=np.uint8)
        img[275:325, 150:450] = 240
        result = _detect_contour_in_image(img)
        assert result is None or result.confidence < 0.50


class TestGuideDetectionPriority:
    """Tests for the combined detection (ArUco preferred over contour)."""

    def test_aruco_preferred_over_contour(self):
        """When an ArUco marker is present, it should be the chosen method."""
        image = _make_aruco_image(marker_size_px=200)
        result = _detect_guide_in_image(image)

        assert result is not None
        assert result.method == "aruco"

    def test_falls_back_to_contour(self):
        """Without an ArUco marker, contour detection should kick in."""
        image = _make_square_image(square_size=200)
        result = _detect_guide_in_image(image)

        assert result is not None
        assert result.method == "contour"


class TestCalibrateSession:
    """Tests for the session-level calibration."""

    def test_empty_directory(self, tmp_path: Path):
        """An empty session directory should return detected=False."""
        result = calibrate_session(tmp_path)
        assert result.detected is False

    def test_session_with_aruco_image(self, tmp_path: Path):
        """A session with one ArUco image should calibrate via ArUco."""
        image = _make_aruco_image(marker_size_px=200)
        cv2.imwrite(str(tmp_path / "img_001.jpg"), image)

        result = calibrate_session(tmp_path)

        assert result.detected is True
        assert result.method == "aruco"
        assert result.confidence >= 0.90
        assert result.scale_px_per_cm > 0.0

    def test_session_prefers_aruco_over_contour(self, tmp_path: Path):
        """ArUco detection should win over contour when both are present."""
        aruco_img = _make_aruco_image(marker_size_px=200)
        square_img = _make_square_image(square_size=200)

        cv2.imwrite(str(tmp_path / "aruco.png"), aruco_img)
        cv2.imwrite(str(tmp_path / "square.png"), square_img)

        result = calibrate_session(tmp_path)
        assert result.method == "aruco"
