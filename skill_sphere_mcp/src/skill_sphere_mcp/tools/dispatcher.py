"""Tool dispatch functionality."""

import logging

from typing import Any

from fastapi import HTTPException
from neo4j import AsyncSession

from ..cv import generate_cv
from ..tools.handlers import explain_match
from ..tools.handlers import graph_search
from ..tools.handlers import match_role


logger = logging.getLogger(__name__)

# Tool name constants
TOOL_MATCH_ROLE = "skill.match_role"
TOOL_EXPLAIN_MATCH = "skill.explain_match"
TOOL_GENERATE_CV = "cv.generate"
TOOL_GRAPH_SEARCH = "graph.search"


def _validate_match_role_params(parameters: dict[str, Any]) -> None:
    """Validate match_role parameters."""
    if not parameters.get("required_skills"):
        raise HTTPException(status_code=422, detail="Required skills are missing")
    if not parameters.get("years_experience"):
        raise HTTPException(status_code=422, detail="Years of experience are required")


def _validate_explain_match_params(parameters: dict[str, Any]) -> None:
    """Validate explain_match parameters."""
    if not parameters.get("skill_id"):
        raise HTTPException(status_code=422, detail="Skill ID is required")
    if not parameters.get("role_requirement"):
        raise HTTPException(status_code=422, detail="Role requirement is required")


def _validate_generate_cv_params(parameters: dict[str, Any]) -> None:
    """Validate generate_cv parameters."""
    if not parameters.get("profile_id"):
        raise HTTPException(status_code=422, detail="Profile ID is required")
    if not parameters.get("format"):
        raise HTTPException(status_code=422, detail="Format is required")


def _validate_graph_search_params(parameters: dict[str, Any]) -> None:
    """Validate graph_search parameters."""
    if not parameters.get("query"):
        raise HTTPException(status_code=422, detail="Query is required")
    top_k = parameters.get("top_k", 10)
    if not isinstance(top_k, int) or top_k <= 0:
        raise HTTPException(status_code=422, detail="top_k must be a positive integer")


async def dispatch_tool(tool_name: str, parameters: dict[str, Any], session: AsyncSession) -> dict[str, Any]:
    """Dispatch tool execution to appropriate handler.

    Args:
        tool_name: Name of tool to dispatch
        parameters: Tool parameters
        session: Database session

    Returns:
        Tool execution result

    Raises:
        HTTPException: If tool name is invalid or parameters are invalid
    """
    if not tool_name or not tool_name.strip():
        raise HTTPException(status_code=422, detail="Tool name is required")

    # Map tool names to handlers
    handlers = {
        TOOL_MATCH_ROLE: match_role,
        TOOL_EXPLAIN_MATCH: explain_match,
        TOOL_GENERATE_CV: generate_cv,
        TOOL_GRAPH_SEARCH: graph_search,
    }

    # Get handler
    handler = handlers.get(tool_name)
    if not handler:
        raise HTTPException(status_code=422, detail=f"Unknown tool: {tool_name}")

    # Validate parameters
    try:
        if tool_name == TOOL_MATCH_ROLE:
            _validate_match_role_params(parameters)
        elif tool_name == TOOL_EXPLAIN_MATCH:
            _validate_explain_match_params(parameters)
        elif tool_name == TOOL_GENERATE_CV:
            _validate_generate_cv_params(parameters)
        elif tool_name == TOOL_GRAPH_SEARCH:
            _validate_graph_search_params(parameters)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    # Execute handler
    try:
        return await handler(parameters, session)
    except HTTPException as e:
        if e.status_code == 422:
            raise
        if e.status_code == 400 and (
            "Invalid years_experience" in str(e.detail)
            or "Invalid parameters" in str(e.detail)
        ):
            raise HTTPException(status_code=422, detail=str(e.detail)) from e
        raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Some error") from e
