"""ForestVol MVP — NodeODM REST client with retry strategy.

Handles the full lifecycle of a photogrammetric task on NodeODM:
1. Create a new task by uploading images.
2. Poll task status until completion (or timeout/failure).
3. Download the resulting point cloud (.PLY) to local storage.

Implements a 3-retry fallback strategy per the spec (RF-06).
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from enum import Enum

import httpx

logger = logging.getLogger(__name__)

NODEODM_HOST = os.getenv("NODEODM_HOST", "nodeodm")
NODEODM_PORT = os.getenv("NODEODM_PORT", "3000")
NODEODM_BASE_URL = f"http://{NODEODM_HOST}:{NODEODM_PORT}"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

# Polling configuration
POLL_INTERVAL_SECONDS = int(os.getenv("NODEODM_POLL_INTERVAL", "10"))
POLL_TIMEOUT_SECONDS = int(os.getenv("NODEODM_POLL_TIMEOUT", "1800"))  # 30 min

# Output paths
PROCESSED_PATH = os.getenv("PROCESSED_PATH", "data/processed")


class TaskStatus(str, Enum):
    """NodeODM task statuses."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


# NodeODM status code → our enum mapping
_STATUS_MAP = {
    10: TaskStatus.QUEUED,
    20: TaskStatus.RUNNING,
    30: TaskStatus.FAILED,
    40: TaskStatus.COMPLETED,
    50: TaskStatus.CANCELED,
}


async def create_task(session_dir: Path) -> str | None:
    """Upload images from session_dir to NodeODM and create a processing task.

    Returns the NodeODM task UUID on success, or None on failure.
    """
    image_extensions = {".jpg", ".jpeg", ".png"}
    image_files = [
        f for f in session_dir.iterdir()
        if f.suffix.lower() in image_extensions
    ]

    if not image_files:
        logger.error("No images found in %s", session_dir)
        return None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Build multipart form with all images
                files = [
                    (
                        "images", 
                        (
                            f.name, 
                            open(f, "rb"), 
                            "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
                        )
                    )
                    for f in image_files
                ]

                import json
                options = {
                    "feature-quality": "lowest",
                    "pc-quality": "lowest",
                    "depthmap-resolution": 256,
                    "max-concurrency": 2,
                    "use-fixed-camera-params": True,
                    "texturing-skip-global-seam-leveling": True
                }

                response = await client.post(
                    f"{NODEODM_BASE_URL}/task/new",
                    data={"options": json.dumps(options)},
                    files=files,
                )

                # Close file handles
                for _, (_, fh, _) in files:
                    fh.close()

                if response.status_code == 200:
                    data = response.json()
                    task_uuid = data.get("uuid")
                    print(f"NodeODM task created: {task_uuid}")
                    return task_uuid

                print(f"NodeODM error {response.status_code}: {response.text}")

        except Exception as exc:
            print(f"NodeODM exception: {exc}")

        if attempt < MAX_RETRIES:
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    print("NodeODM task creation failed after all attempts")
    return None


async def poll_task_status(task_uuid: str) -> TaskStatus:
    """Poll NodeODM until the task completes, fails, or times out.

    Returns the final TaskStatus.
    """
    elapsed = 0

    while elapsed < POLL_TIMEOUT_SECONDS:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{NODEODM_BASE_URL}/task/{task_uuid}/info"
                )

                if response.status_code == 200:
                    data = response.json()
                    status_code = data.get("status", {}).get("code", -1)
                    status = _STATUS_MAP.get(status_code, TaskStatus.QUEUED)

                    progress = data.get("progress", 0)
                    logger.info(
                        "NodeODM task %s: %s (progress: %d%%)",
                        task_uuid, status.value, progress,
                    )

                    if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED):
                        return status

        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            logger.warning("Polling error for task %s: %s", task_uuid, exc)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    logger.error("NodeODM task %s timed out after %ds", task_uuid, POLL_TIMEOUT_SECONDS)
    return TaskStatus.FAILED


async def download_result(task_uuid: str, session_id: str) -> Path | None:
    """Download the point cloud output from a completed NodeODM task.

    Saves to data/processed/{session_id}/. Returns the path to the
    downloaded assets directory, or None on failure.
    """
    output_dir = Path(PROCESSED_PATH) / session_id
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Download all assets as a zip
            response = await client.get(
                f"{NODEODM_BASE_URL}/task/{task_uuid}/download/all.zip",
            )

            if response.status_code == 200:
                zip_path = output_dir / "all.zip"
                zip_path.write_bytes(response.content)

                # Extract zip
                shutil.unpack_archive(str(zip_path), str(output_dir))
                zip_path.unlink()  # Clean up zip

                logger.info("NodeODM results downloaded to %s", output_dir)
                return output_dir

            logger.error(
                "Failed to download NodeODM results: %s", response.status_code
            )

    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        logger.error("Download error for task %s: %s", task_uuid, exc)

    return None


async def run_reconstruction(session_id: str, session_dir: Path) -> dict:
    """Full reconstruction pipeline: create → poll → download.

    Returns a dict with keys: success, task_uuid, status, output_dir.
    """
    task_uuid = await create_task(session_dir)
    if task_uuid is None:
        return {
            "success": False,
            "task_uuid": None,
            "status": TaskStatus.FAILED.value,
            "output_dir": None,
            "error": "NODEODM_TASK_CREATION_FAILED",
        }

    final_status = await poll_task_status(task_uuid)

    if final_status != TaskStatus.COMPLETED:
        return {
            "success": False,
            "task_uuid": task_uuid,
            "status": final_status.value,
            "output_dir": None,
            "error": "NODEODM_TASK_FAILED",
        }

    output_dir = await download_result(task_uuid, session_id)

    return {
        "success": output_dir is not None,
        "task_uuid": task_uuid,
        "status": final_status.value,
        "output_dir": str(output_dir) if output_dir else None,
        "error": None if output_dir else "DOWNLOAD_FAILED",
    }
