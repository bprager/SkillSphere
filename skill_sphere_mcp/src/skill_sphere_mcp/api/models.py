"""Models for the MCP server."""

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str


class InitializeRequest(BaseModel):
    """Initialize request model."""

    protocol_version: str
    client_info: dict[str, Any]


class InitializeResponse(BaseModel):
    """Initialize response model."""

    protocol_version: str
    capabilities: dict[str, Any]
    instructions: str
