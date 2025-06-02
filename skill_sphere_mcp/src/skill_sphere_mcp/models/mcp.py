"""MCP API models."""

from typing import Any

from pydantic import BaseModel, Field


class InitializeRequest(BaseModel):
    """Initialize request model."""

    client_info: dict[str, Any] = Field(
        default_factory=dict,
        description="Client information",
    )


class InitializeResponse(BaseModel):
    """Initialize response model."""

    protocol_version: str = Field(
        default="1.0",
        description="Protocol version",
    )
    capabilities: dict[str, Any] = Field(
        description="Capabilities supported by the server",
    )
    instructions: str = Field(
        description="Instructions for the client",
    )


class QueryRequest(BaseModel):
    """Query request model."""

    query: str = Field(
        description="Cypher query to execute",
    )
    parameters: dict[str, Any] | None = Field(
        default=None,
        description="Query parameters",
    )


class QueryResponse(BaseModel):
    """Query response model."""

    results: list[dict[str, Any]] = Field(
        description="Query results",
    )
    metadata: dict[str, Any] = Field(
        description="Query metadata",
    )


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(
        description="Search query",
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
    )


class SearchResponse(BaseModel):
    """Search response model."""

    results: list[dict[str, Any]] = Field(
        description="Search results",
    )


class ResourceRequest(BaseModel):
    """Resource request model."""

    resource: str = Field(
        description="Resource type to get information for",
    )


class ResourceResponse(BaseModel):
    """Resource response model."""

    type: str = Field(
        description="Resource type",
    )
    resource_schema: dict[str, Any] = Field(
        description="Resource schema",
    )
