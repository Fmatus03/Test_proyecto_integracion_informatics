"""ForestVol MVP — Calibration service using ArUco marker detection.

Detects a 50×50 cm ArUco marker (DICT_4X4_50, ID 0) in drone images
and computes the spatial scale factor (pixels per centimetre).

Strategy:
1. PRIMARY: Detect ArUco marker ID 0 using cv2.aruco with sub-pixel
   corner refinement. Compute side length from the 4 detected corners.
2. FALLBACK: If ArUco is not found, try generic contour detection for
   a high-contrast square (original approach).
3. If neither method finds the guide with confidence >= 0.90, flag
   fallback_needed so the operator can provide a manual value.
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

# ArUco configuration
ARUCO_DICT_TYPE = cv2.aruco.DICT_4X4_50
ARUCO_TARGET_ID = 0

# Contour fallback thresholds
MIN_CONTOUR_AREA = 500
ASPECT_RATIO_TOL = 0.25

# Minimum confidence threshold to accept the detection.
MIN_CONFIDENCE = 0.90


@dataclass
class CalibrationResult:
    """Result of calibration on a single image."""

    detected: bool
    scale_px_per_cm: float
    confidence: float
    side_px: float
    method: str = "none"


def _aruco_side_length(corners: np.ndarray) -> float:
    """Compute the mean side length of a quadrilateral from its 4 corners.

    ``corners`` shape: (4, 2) — the four corner points in pixel coords.
    """
    sides = []
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i + 1) % 4]
        sides.append(float(np.linalg.norm(p2 - p1)))
    return float(np.mean(sides))


def _detect_aruco_in_image(image: np.ndarray) -> CalibrationResult | None:
    """Try to detect ArUco marker ID 0 (DICT_4X4_50) in a single image.

    Returns a CalibrationResult if the target marker is found, else None.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_TYPE)
    parameters = cv2.aruco.DetectorParameters()

    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners_list, ids, _ = detector.detectMarkers(gray)

    if ids is None:
        return None

    # Find our target marker (ID 0)
    for i, marker_id in enumerate(ids.flatten()):
        if marker_id != ARUCO_TARGET_ID:
            continue

        # corners_list[i] shape: (1, 4, 2)
        marker_corners = corners_list[i].reshape(4, 2)
        side_px = _aruco_side_length(marker_corners)
        scale = side_px / GUIDE_SIDE_CM

        # ArUco detections are inherently high-confidence when found.
        # We compute a confidence based on how square the marker appears
        # (perspective distortion reduces squareness).
        sides = [
            float(np.linalg.norm(marker_corners[(j + 1) % 4] - marker_corners[j]))
            for j in range(4)
        ]
        min_side = min(sides)
        max_side = max(sides)
        squareness = min_side / max_side if max_side > 0 else 0
        confidence = round(squareness, 4)

        return CalibrationResult(
            detected=True,
            scale_px_per_cm=round(scale, 4),
            confidence=confidence,
            side_px=round(side_px, 2),
            method="aruco",
        )

    return None


def _detect_contour_in_image(image: np.ndarray) -> CalibrationResult | None:
    """Fallback: detect a high-contrast square via contour analysis."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        if len(approx) != 4:
            continue

        _, _, w, h = cv2.boundingRect(approx)
        if h == 0:
            continue
        aspect = float(w) / float(h)
        if abs(aspect - 1.0) > ASPECT_RATIO_TOL:
            continue

        side_px = (w + h) / 2.0
        scale = side_px / GUIDE_SIDE_CM

        hull_area = cv2.contourArea(cv2.convexHull(approx))
        solidity = area / hull_area if hull_area > 0 else 0
        squareness = 1.0 - abs(aspect - 1.0)
        confidence = round(min(squareness, solidity), 4)

        candidate = CalibrationResult(
            detected=True,
            scale_px_per_cm=round(scale, 4),
            confidence=confidence,
            side_px=round(side_px, 2),
            method="contour",
        )

        if best is None or candidate.confidence > best.confidence:
            best = candidate

    return best


def _detect_guide_in_image(image: np.ndarray) -> CalibrationResult | None:
    """Try ArUco first, then fall back to contour detection."""
    result = _detect_aruco_in_image(image)
    if result is not None:
        return result

    return _detect_contour_in_image(image)


def calibrate_session(session_dir: Path) -> CalibrationResult:
    """Run calibration across all images in a session directory.

    Picks the single best detection (highest confidence) among all images.
    ArUco detections are preferred over contour detections.
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
            method="none",
        )

    for img_path in image_files:
        image = cv2.imread(str(img_path))
        if image is None:
            logger.warning("Could not read image: %s", img_path)
            continue

        result = _detect_guide_in_image(image)
        if result is None:
            continue

        # Prefer ArUco over contour when confidence is similar
        if best_overall is None:
            best_overall = result
        elif result.method == "aruco" and best_overall.method != "aruco":
            best_overall = result
        elif result.confidence > best_overall.confidence and result.method == best_overall.method:
            best_overall = result

    if best_overall is None or best_overall.confidence < MIN_CONFIDENCE:
        logger.info(
            "Calibration guide not detected with sufficient confidence. "
            "Best: %s",
            best_overall,
        )
        return CalibrationResult(
            detected=False,
            scale_px_per_cm=best_overall.scale_px_per_cm if best_overall else 0.0,
            confidence=best_overall.confidence if best_overall else 0.0,
            side_px=best_overall.side_px if best_overall else 0.0,
            method=best_overall.method if best_overall else "none",
        )

    return best_overall
