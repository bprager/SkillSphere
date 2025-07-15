"""MCP (Model Context Protocol) models for request and response handling."""

from typing import Any
from typing import Dict
from typing import Optional

from pydantic import Field
from pydantic import field_validator

from skill_sphere_mcp.models.extended_fields import ExtendedFields


class HealthResponse(ExtendedFields):
    """Health check response model."""

    status: str


class InitializeRequest(ExtendedFields):
    """Initialize request model."""

    protocol_version: str
    client_info: dict[str, Any]


class InitializeResponse(ExtendedFields):
    """Initialize response model."""

    protocol_version: str
    capabilities: dict[str, Any]
    instructions: str


class EntityResponse(ExtendedFields):
    """Entity response model."""

    id: str
    name: str
    type: str
    description: str
    properties: dict[str, Any] | None = None
    relationships: list[dict[str, Any]] | None = None


class SearchRequest(ExtendedFields):
    """Search request model."""

    query: str = Field(
        ...,
        min_length=1,
        description="Search query string",
        json_schema_extra={"error_messages": {"min_length": "Query cannot be empty"}}
    )
    limit: int = Field(
        default=20,
        gt=0,
        description="Maximum number of results",
        json_schema_extra={"error_messages": {"gt": "Limit must be greater than 0"}}
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate that query is not empty."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v


class SearchResponse(ExtendedFields):
    """Search response model."""

    results: list[dict[str, Any]]
    total: int


class MatchRoleRequest(ExtendedFields):
    """Match role request model."""

    required_skills: list[str]
    years_experience: dict[str, int] = {}


class MatchRoleResponse(ExtendedFields):
    """Match role response model."""

    match_score: float
    skill_gaps: list[str]
    matching_skills: list[dict[str, Any]]


class ResourceRequest(ExtendedFields):
    """Resource request model."""

    resource_type: str
    resource_id: str


class ToolRequest(ExtendedFields):
    """Tool request model."""

    tool_name: str
    parameters: dict[str, Any]


class ExplainMatchRequest(ExtendedFields):
    """Match explanation request."""

    skill_id: str
    role_requirement: str


class ExplainMatchResponse(ExtendedFields):
    """Match explanation response."""

    explanation: str
    evidence: list[dict[str, Any]]


class GraphSearchRequest(ExtendedFields):
    """Graph search request."""

    query: str
    top_k: int = 10


class ToolDispatchRequest(ExtendedFields):
    """Tool dispatch request model."""

    tool_name: str = Field(
        ...,
        min_length=1,
        description="Name of the tool to dispatch",
        json_schema_extra={"error_messages": {"min_length": "Tool name is required"}}
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool parameters",
        json_schema_extra={"error_messages": {"type": "Parameters must be a dictionary"}}
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context"
    )

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate that tool name is not empty."""
        if not v.strip():
            raise ValueError("Tool name is required")
        return v


class ResourceResponse(ExtendedFields):
    """Resource response model."""

    type: str
    description: str
    properties: list[str]
    relationships: list[str]


class ToolDispatchResponse(ExtendedFields):
    """Tool dispatch response model."""

    result: str
    data: dict[str, Any]
    message: str
