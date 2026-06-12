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

class UploadResponse(BaseModel):
    """Response schema for POST /api/upload endpoint."""

    session_id: str = Field(
        ...,
        description="Unique session identifier (UUID)",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    image_count: int = Field(
        ...,
        description="Number of successfully validated images",
        examples=[20],
    )
    valid: bool = Field(
        ...,
        description="Whether the entire batch was valid",
        examples=[True],
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of file-specific validation errors",
    )
    pipeline_state: str = Field(
        ...,
        description="Current state of the pipeline",
        examples=["VALIDATED"],
    )
