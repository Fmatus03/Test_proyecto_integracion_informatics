"""ForestVol MVP — Main FastAPI application entry point."""

import os

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import ErrorResponse, HealthResponse
from app.api.routes import upload
from app.api.routes import calibration

app = FastAPI(
    title="ForestVol MVP",
    description="Photogrammetric volume calculation system for timber stockpiles.",
    version="5.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{os.getenv('FRONTEND_PORT', '3000')}",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(calibration.router, prefix="/api")

NODEODM_HOST = os.getenv("NODEODM_HOST", "localhost")
NODEODM_PORT = os.getenv("NODEODM_PORT", "3001")


async def _check_nodeodm() -> bool:
    """Check if NodeODM service is reachable via HTTP."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"http://{NODEODM_HOST}:{NODEODM_PORT}/info"
            )
            return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return False


@app.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": ErrorResponse}},
    tags=["system"],
    summary="Health check",
    description="Verify backend and NodeODM connectivity.",
)
async def health_check() -> HealthResponse | JSONResponse:
    """Return service health status including NodeODM reachability."""
    nodeodm_ok = await _check_nodeodm()

    if not nodeodm_ok:
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error_code="DEPENDENCY_UNAVAILABLE",
                message="NodeODM service is not reachable at configured host",
            ).model_dump(),
        )

    return HealthResponse(
        status="ok",
        version="5.1",
        nodeodm_reachable=True,
    )
