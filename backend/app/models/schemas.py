"""Pydantic v2 schemas for ForestVol MVP API responses."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for GET /health endpoint."""

    status: str = Field(
        ...,
        description="Service status",
        examples=["ok"],
    )
    version: str = Field(
        ...,
        description="ForestVol version",
        examples=["5.1"],
    )
    nodeodm_reachable: bool = Field(
        ...,
        description="Whether NodeODM service is reachable",
    )


class ErrorResponse(BaseModel):
    """Standard error response schema for all API errors."""

    error_code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["DEPENDENCY_UNAVAILABLE"],
    )
    message: str = Field(
        ...,
        description="Human-readable error description",
        examples=["NodeODM service is not reachable at configured host"],
    )
