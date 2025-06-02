"""MCP API package."""

from .handlers import explain_match, graph_search, match_role
from .models import (
                     ExplainMatchRequest,
                     ExplainMatchResponse,
                     GraphSearchRequest,
                     MatchRoleRequest,
                     MatchRoleResponse,
                     ResourceRequest,
                     ToolRequest,
)
from .routes import router
from .rpc import handle_rpc_request
from .utils import get_resource

__all__ = [
    "ExplainMatchRequest",
    "ExplainMatchResponse",
    "GraphSearchRequest",
    "MatchRoleRequest",
    "MatchRoleResponse",
    "ResourceRequest",
    "ToolRequest",
    "explain_match",
    "get_resource",
    "graph_search",
    "handle_rpc_request",
    "match_role",
    "router",
]
