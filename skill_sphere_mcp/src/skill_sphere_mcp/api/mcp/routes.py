"""MCP API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession

from ...db.deps import get_db_session
from ...db.utils import get_entity_by_id
from ..jsonrpc import JSONRPCRequest, JSONRPCResponse
from ..mcp.handlers import explain_match, graph_search, match_role
from ..mcp.handlers import search as search_handler
from ..mcp.models import SearchRequest
from ..mcp.rpc import handle_rpc_request
from ..mcp.utils import get_initialize_response_dict, get_resource
from ..models import HealthResponse

router = APIRouter()


@router.get("/v1/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.get("/mcp/entities/{entity_id}")
async def get_entity(
    entity_id: str, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Get an entity by ID."""
    return await get_entity_by_id(session, entity_id)


@router.post("/mcp/search")
async def search(
    request: SearchRequest, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Search for entities."""
    return await search_handler(request, session)


@router.post("/mcp/initialize")
async def initialize() -> dict[str, Any]:
    """Initialize the MCP."""
    return get_initialize_response_dict()


@router.get("/mcp/resources/list")
async def list_resources() -> list[str]:
    """List available resources."""
    return ["nodes", "relationships", "search"]


@router.get("/mcp/resources/get/{resource}")
async def get_resource_schema(resource: str) -> dict[str, Any]:
    """Get a resource schema."""
    try:
        return await get_resource(resource)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/mcp/rpc/tools/dispatch")
async def tool_dispatch(
    request: dict[str, Any], session: Annotated[AsyncSession, Depends(get_db_session)]
) -> Any:
    """Dispatch a tool request."""
    tool_name = request.get("tool_name")
    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing tool name")

    if tool_name == "match_role":
        return await match_role(request.get("parameters", {}), session)
    if tool_name == "explain_match":
        return await explain_match(request.get("parameters", {}), session)
    if tool_name == "graph_search":
        return await graph_search(request.get("parameters", {}), session)
    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")


@router.post("/mcp/rpc")
async def rpc(
    request: JSONRPCRequest, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> JSONRPCResponse:
    """Handle JSON-RPC requests."""
    return await handle_rpc_request(request, session)
