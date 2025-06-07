"""MCP API package."""

from .handlers import explain_match
from .handlers import graph_search
from .handlers import match_role
from .models import ExplainMatchRequest
from .models import ExplainMatchResponse
from .models import GraphSearchRequest
from .models import MatchRoleRequest
from .models import MatchRoleResponse
from .models import ResourceRequest
from .models import ToolRequest
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
