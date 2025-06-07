"""RPC handlers for the MCP API."""

from typing import Any

from neo4j import AsyncSession

from ..jsonrpc import JSONRPCHandler
from ..jsonrpc import JSONRPCRequest
from ..jsonrpc import JSONRPCResponse
from .handlers import explain_match
from .handlers import graph_search
from .handlers import handle_search
from .handlers import match_role
from .models import SearchRequest
from .utils import get_initialize_response_dict
from .utils import get_resource


rpc_handler = JSONRPCHandler()


@rpc_handler.register("mcp.initialize")
async def rpc_initialize(
    _params: dict[str, Any], _session: AsyncSession | None = None
) -> dict[str, Any]:
    """Handle initialize RPC method."""
    return get_initialize_response_dict()


@rpc_handler.register("mcp.resources.list")
async def rpc_list_resources(
    _params: dict[str, Any], _session: AsyncSession | None = None
) -> list[str]:
    """Handle resources/list RPC method."""
    return ["nodes", "relationships", "search"]


@rpc_handler.register("mcp.resources.get")
async def rpc_get_resource(
    params: dict[str, Any], _session: AsyncSession | None = None
) -> dict[str, Any]:
    """Handle resources/get RPC method."""
    resource = params.get("resource")
    if not resource:
        raise ValueError("Missing resource parameter")
    return await get_resource(resource)


@rpc_handler.register("mcp.search")
async def rpc_search(
    params: dict[str, Any], session: AsyncSession
) -> list[dict[str, Any]]:
    """Handle search RPC method."""
    query = params.get("query")
    if not query:
        raise ValueError("Missing query parameter")
    limit = params.get("limit", 10)
    request = SearchRequest(query=query, limit=limit)
    response = await handle_search(request.model_dump(), session)
    return response.get("results", [])  # type: ignore[no-any-return]


@rpc_handler.register("mcp.tool")
async def rpc_tool(params: dict[str, Any], session: AsyncSession) -> dict[str, Any]:
    """Handle tool dispatch requests."""
    tool_name = params.get("name")
    if not tool_name:
        raise ValueError("Missing tool name")

    if tool_name == "match_role":
        return await match_role(params.get("parameters", {}), session)
    if tool_name == "explain_match":
        return await explain_match(params.get("parameters", {}), session)
    if tool_name == "graph_search":
        return await graph_search(params.get("parameters", {}), session)
    raise ValueError(f"Unknown tool: {tool_name}")


@rpc_handler.register("mcp.skill.match_role")
async def rpc_match_role_handler(
    params: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Handle skill matching requests."""
    return await match_role(params, session)


async def handle_rpc_request(
    request: JSONRPCRequest, session: AsyncSession | None = None
) -> JSONRPCResponse:
    """Handle JSON-RPC requests."""
    try:
        return await rpc_handler.handle_request(request, session)
    except (ValueError, TypeError, KeyError, RuntimeError) as e:
        return JSONRPCResponse.handle_error(e, request.id)
