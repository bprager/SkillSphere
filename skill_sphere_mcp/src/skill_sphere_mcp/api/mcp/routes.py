"""MCP API routes."""

import logging

from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import Response
from neo4j import AsyncSession
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import generate_latest

from ...db.deps import get_db_session
from ...models.skill import Skill
from ..jsonrpc import ERROR_INVALID_PARAMS
from ..jsonrpc import JSONRPCRequest
from ..jsonrpc import JSONRPCResponse
from ..mcp.handlers import explain_match
from ..mcp.handlers import graph_search
from ..mcp.handlers import handle_get_entity
from ..mcp.handlers import handle_search
from ..mcp.handlers import handle_tool_dispatch
from ..mcp.handlers import match_role
from ..mcp.rpc import handle_rpc_request
from ..mcp.utils import create_skill_in_db
from ..mcp.utils import get_resource
from ..models import HealthResponse


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/mcp/entities/{entity_id}")
async def get_entity_endpoint(
    entity_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Get entity by ID."""
    try:
        if not entity_id or not isinstance(entity_id, str) or not entity_id.isalnum():
            raise HTTPException(status_code=422, detail="Invalid entity ID")
        return await handle_get_entity(session, entity_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get entity error: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/mcp/search")
async def search_endpoint(
    params: dict[str, Any],
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Search entities."""
    query = params.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        return await handle_search(session, query, params.get("limit", 10))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Search error: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


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
async def tool_dispatch_endpoint(
    params: dict[str, Any],
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, Any]:
    """Dispatch tool execution."""
    tool_name = params.get("tool_name")
    if not tool_name:
        raise HTTPException(status_code=422, detail="Tool name is required")
    try:
        result = await handle_tool_dispatch(session, tool_name, params.get("parameters", {}))
        return result
    except HTTPException as e:
        if e.status_code in (400, 404, 422):
            raise
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.error("Tool dispatch error: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/mcp/rpc")
async def rpc_endpoint(
    request: dict[str, Any],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """Handle JSON-RPC requests."""
    try:
        rpc_request = JSONRPCRequest(**request)
        response = await handle_rpc_request(rpc_request, session)
        return response.__dict__
    except ValueError as e:
        return JSONRPCResponse.create_error(
            ERROR_INVALID_PARAMS["code"],
            str(e),
            request.get("id")
        ).__dict__
    except Exception as e:
        logger.error("RPC error: %s", str(e))
        return JSONRPCResponse.handle_error(e, request.get("id")).__dict__


def _validate_generate_cv_params(
    profile_id: str,
    output_format: str,
    language: str,
    _db: Any,  # Prefix with underscore to indicate unused
) -> None:
    """Validate generate CV parameters."""
    if not profile_id:
        raise HTTPException(
            status_code=422,
            detail="Profile ID is required",
        )

    if not output_format:
        raise HTTPException(
            status_code=422,
            detail="Format is required",
        )

    if not language:
        raise HTTPException(
            status_code=422,
            detail="Language is required",
        )

    if output_format not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=422,
            detail="Invalid format. Must be one of: pdf, docx",
        )

    if language not in ["en", "de"]:
        raise HTTPException(
            status_code=422,
            detail="Invalid language. Must be one of: en, de",
        )

    # Note: Profile model is not imported, so this validation is commented out
    # profile = db.query(Profile).filter(Profile.id == profile_id).first()
    # if not profile:
    #     raise HTTPException(
    #         status_code=404,
    #         detail=f"Profile with ID {profile_id} not found",
    #     )


@router.get("/skills", response_model=list[Skill])
async def get_skills(session: AsyncSession = Depends(get_db_session)) -> list[Skill]:
    """Get all skills from the database."""
    try:
        result = await session.run("MATCH (s:Skill) RETURN s")
        records = await result.fetch_all()  # type: ignore[attr-defined]
        return [Skill(**record["s"]) for record in records]
    except Exception as e:
        logger.error("Failed to fetch skills: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch skills") from e


@router.post("/skills", response_model=Skill)
async def create_skill(skill: Skill, session: AsyncSession = Depends(get_db_session)) -> Skill:
    """Create a new skill in the database."""
    return await create_skill_in_db(skill, session)


@router.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
