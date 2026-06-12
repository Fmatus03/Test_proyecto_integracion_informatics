"""Unit tests for the calibration service.

We generate synthetic images with NumPy so the tests are self-contained
and do not require real drone photos.
"""

import numpy as np
import pytest
from pathlib import Path

from app.services.calibration_service import (
    _detect_guide_in_image,
    calibrate_session,
    CalibrationResult,
    GUIDE_SIDE_CM,
)


def _make_square_image(
    img_size: int = 600,
    square_size: int = 200,
    bg_color: int = 30,
    fg_color: int = 240,
) -> np.ndarray:
    """Create a synthetic BGR image with a white square on dark background."""
    img = np.full((img_size, img_size, 3), bg_color, dtype=np.uint8)
    offset = (img_size - square_size) // 2
    img[offset : offset + square_size, offset : offset + square_size] = fg_color
    return img


class TestDetectGuideInImage:
    """Tests for the single-image detection function."""

    def test_detects_square(self):
        """A clear white square on a dark background should be detected."""
        image = _make_square_image(square_size=200)
        result = _detect_guide_in_image(image)

        assert result is not None
        assert result.detected is True
        assert result.confidence >= 0.90
        # The detected side should be close to 200 px.
        assert abs(result.side_px - 200.0) < 20.0

    def test_scale_calculation(self):
        """Scale should equal side_px / 50 cm."""
        image = _make_square_image(square_size=100)
        result = _detect_guide_in_image(image)

        assert result is not None
        expected_scale = result.side_px / GUIDE_SIDE_CM
        assert abs(result.scale_px_per_cm - expected_scale) < 0.01

    def test_no_detection_on_blank(self):
        """A uniform image should yield no detection."""
        blank = np.full((400, 400, 3), 128, dtype=np.uint8)
        result = _detect_guide_in_image(blank)

        assert result is None

    def test_rejects_rectangle(self):
        """A long rectangle (aspect ratio far from 1.0) should not match."""
        img = np.full((600, 600, 3), 30, dtype=np.uint8)
        # Draw a 300×50 rectangle — aspect ratio = 6.0
        img[275:325, 150:450] = 240
        result = _detect_guide_in_image(img)

        # Either None or very low confidence
        assert result is None or result.confidence < 0.50


class TestCalibrateSession:
    """Tests for the session-level calibration."""

    def test_empty_directory(self, tmp_path: Path):
        """An empty session directory should return detected=False."""
        result = calibrate_session(tmp_path)
        assert result.detected is False

    def test_session_with_good_image(self, tmp_path: Path):
        """A session with one good synthetic image should calibrate."""
        import cv2

        image = _make_square_image(square_size=200)
        cv2.imwrite(str(tmp_path / "img_001.jpg"), image)

        result = calibrate_session(tmp_path)

        assert result.detected is True
        assert result.confidence >= 0.90
        assert result.scale_px_per_cm > 0.0

    def test_session_picks_best(self, tmp_path: Path):
        """When multiple images exist, the best confidence wins."""
        import cv2

        # Good image — clear square
        good = _make_square_image(square_size=200, bg_color=10, fg_color=250)
        cv2.imwrite(str(tmp_path / "good.png"), good)

        # Noisy image — uniform gray
        noisy = np.full((400, 400, 3), 120, dtype=np.uint8)
        cv2.imwrite(str(tmp_path / "noisy.png"), noisy)

        result = calibrate_session(tmp_path)
        assert result.detected is True
        assert result.confidence >= 0.90
