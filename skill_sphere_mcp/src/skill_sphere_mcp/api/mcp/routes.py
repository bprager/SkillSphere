"""MCP API routes."""

from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from neo4j import AsyncSession

from ...db.deps import get_db_session
from ...db.utils import get_entity_by_id
from ..jsonrpc import JSONRPCRequest
from ..jsonrpc import JSONRPCResponse
from ..mcp.handlers import explain_match
from ..mcp.handlers import graph_search
from ..mcp.handlers import handle_search
from ..mcp.handlers import match_role
from ..mcp.models import EntityResponse
from ..mcp.models import SearchRequest
from ..mcp.rpc import handle_rpc_request
from ..mcp.utils import get_initialize_response_dict
from ..mcp.utils import get_resource
from ..models import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.get("/mcp/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> EntityResponse:
    """Get an entity by ID.

    Args:
        entity_id: The ID of the entity to retrieve
        session: Neo4j database session

    Returns:
        EntityResponse containing the entity data and relationships

    Raises:
        HTTPException: If entity is not found or ID is invalid
    """
    if not entity_id or not entity_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Invalid entity ID. Must be a non-empty string containing only alphanumeric characters, hyphens, and underscores.",
        )

    try:
        entity_data = await get_entity_by_id(session, entity_id)
        return EntityResponse(**entity_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process entity data: {str(e)}"
        ) from e


@router.post("/mcp/search")
async def search(
    request: SearchRequest, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Search for entities."""
    return await handle_search(request.model_dump(), session)


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


@router.post("/match_role")
async def match_role_endpoint(
    request: dict[str, Any], session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Match role endpoint."""
    return await match_role(request, session)


@router.post("/explain_match")
async def explain_match_endpoint(
    request: dict[str, Any], session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Explain match endpoint."""
    return await explain_match(request, session)


@router.post("/graph_search")
async def graph_search_endpoint(
    request: dict[str, Any], session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Graph search endpoint."""
    return await graph_search(request, session)


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
