"""ForestVol MVP — Calibration service using OpenCV contour detection.

Detects a 50×50 cm calibration guide (solid-color square) in drone images
and computes the spatial scale factor (pixels per centimetre).

Strategy:
1. Convert image to grayscale.
2. Apply adaptive threshold to isolate high-contrast regions.
3. Find contours and filter for quadrilaterals (4-vertex polygons).
4. Among candidate quads, pick the largest one that passes an aspect-ratio
   check (close to 1:1 for a square).
5. Compute the mean side length in pixels → divide by 50 cm → scale.

If no guide is detected with sufficient confidence (≥ 0.90), the service
raises a fallback flag so the operator can provide a manual scale value.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Physical size of the calibration guide in centimetres.
GUIDE_SIDE_CM = 50.0

# Minimum contour area in pixels² to avoid noise.
MIN_CONTOUR_AREA = 500

# Aspect-ratio tolerance — a perfect square has ratio 1.0.
ASPECT_RATIO_TOL = 0.25  # accept ratios in [0.75, 1.25]

# Minimum confidence threshold to accept the detection.
MIN_CONFIDENCE = 0.90


@dataclass
class CalibrationResult:
    """Result of calibration on a single image."""

    detected: bool
    scale_px_per_cm: float
    confidence: float
    side_px: float


def _detect_guide_in_image(image: np.ndarray) -> CalibrationResult | None:
    """Try to detect the calibration square in a single image.

    Returns a CalibrationResult if a suitable quadrilateral is found,
    otherwise None.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold handles varying lighting conditions typical in
    # outdoor drone imagery.
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    best: CalibrationResult | None = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_CONTOUR_AREA:
            continue

        # Approximate the contour to a polygon.
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        if len(approx) != 4:
            continue

        # Compute bounding rectangle and check aspect ratio.
        _, _, w, h = cv2.boundingRect(approx)
        if h == 0:
            continue
        aspect = float(w) / float(h)
        if abs(aspect - 1.0) > ASPECT_RATIO_TOL:
            continue

        # Use the mean of width and height as the estimated side length.
        side_px = (w + h) / 2.0
        scale = side_px / GUIDE_SIDE_CM

        # Confidence heuristic:
        # - How square the shape is (aspect close to 1.0).
        # - How convex the shape is.
        hull_area = cv2.contourArea(cv2.convexHull(approx))
        solidity = area / hull_area if hull_area > 0 else 0
        squareness = 1.0 - abs(aspect - 1.0)
        confidence = round(min(squareness, solidity), 4)

        candidate = CalibrationResult(
            detected=True,
            scale_px_per_cm=round(scale, 4),
            confidence=confidence,
            side_px=round(side_px, 2),
        )

        # Keep the candidate with the highest confidence.
        if best is None or candidate.confidence > best.confidence:
            best = candidate

    return best


def calibrate_session(session_dir: Path) -> CalibrationResult:
    """Run calibration across all images in a session directory.

    Picks the single best detection (highest confidence) among all images.
    If no image yields a detection above ``MIN_CONFIDENCE``, returns a
    fallback result with ``detected=False``.
    """
    best_overall: CalibrationResult | None = None

    image_extensions = {".jpg", ".jpeg", ".png"}
    image_files = [
        f for f in session_dir.iterdir()
        if f.suffix.lower() in image_extensions
    ]

    if not image_files:
        logger.warning("No images found in session directory: %s", session_dir)
        return CalibrationResult(
            detected=False,
            scale_px_per_cm=0.0,
            confidence=0.0,
            side_px=0.0,
        )

    for img_path in image_files:
        image = cv2.imread(str(img_path))
        if image is None:
            logger.warning("Could not read image: %s", img_path)
            continue

        result = _detect_guide_in_image(image)
        if result is None:
            continue

        if best_overall is None or result.confidence > best_overall.confidence:
            best_overall = result

    if best_overall is None or best_overall.confidence < MIN_CONFIDENCE:
        logger.info(
            "Calibration guide not detected with sufficient confidence. "
            "Best confidence: %s",
            best_overall.confidence if best_overall else 0.0,
        )
        return CalibrationResult(
            detected=False,
            scale_px_per_cm=best_overall.scale_px_per_cm if best_overall else 0.0,
            confidence=best_overall.confidence if best_overall else 0.0,
            side_px=best_overall.side_px if best_overall else 0.0,
        )

    return best_overall
