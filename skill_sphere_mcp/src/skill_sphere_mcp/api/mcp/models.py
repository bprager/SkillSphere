"""MCP API models."""

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


class EntityResponse(BaseModel):
    """Entity response model."""

    id: str
    name: str
    type: str | None = None
    properties: dict[str, Any] | None = None
    relationships: list[dict[str, Any]] | None = None


class SearchRequest(BaseModel):
    """Search request model."""

    query: str
    limit: int = 10


class SearchResponse(BaseModel):
    """Search response model."""

    results: list[dict[str, Any]]


class MatchRoleRequest(BaseModel):
    """Match role request model."""

    required_skills: list[str]
    years_experience: dict[str, int] = {}


class MatchRoleResponse(BaseModel):
    """Match role response model."""

    match_score: float
    skill_gaps: list[str]
    matching_skills: list[dict[str, Any]]


class ResourceRequest(BaseModel):
    """Resource request model."""

    resource_type: str
    resource_id: str


class ToolRequest(BaseModel):
    """Tool request model."""

    tool_name: str
    parameters: dict[str, Any]


class ExplainMatchRequest(BaseModel):
    """Match explanation request."""

    skill_id: str
    role_requirement: str


class ExplainMatchResponse(BaseModel):
    """Match explanation response."""

    explanation: str
    evidence: list[dict[str, Any]]


class GraphSearchRequest(BaseModel):
    """Graph search request."""

    query: str
    top_k: int = 10
