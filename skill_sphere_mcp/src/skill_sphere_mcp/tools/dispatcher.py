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
        raise HTTPException(status_code=400, detail="Missing required_skills parameter")
    if not isinstance(parameters.get("years_experience", {}), dict):
        raise HTTPException(
            status_code=400, detail="years_experience must be a dictionary"
        )


def _validate_explain_match_params(parameters: dict[str, Any]) -> None:
    """Validate explain_match parameters."""
    if not parameters.get("skill_id"):
        raise HTTPException(status_code=400, detail="Missing skill_id parameter")
    if not parameters.get("role_requirement"):
        raise HTTPException(
            status_code=400, detail="Missing role_requirement parameter"
        )


def _validate_generate_cv_params(parameters: dict[str, Any]) -> None:
    """Validate generate_cv parameters."""
    if not parameters.get("target_keywords"):
        raise HTTPException(status_code=400, detail="Missing target_keywords parameter")
    if parameters.get("format") not in ["markdown", "html", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid format parameter")


def _validate_graph_search_params(parameters: dict[str, Any]) -> None:
    """Validate graph_search parameters."""
    if not parameters.get("query"):
        raise HTTPException(status_code=400, detail="Missing query parameter")
    if parameters.get("top_k", 0) <= 0:
        raise HTTPException(status_code=400, detail="top_k must be greater than 0")


async def dispatch_tool(
    tool_name: str, parameters: dict[str, Any], session: AsyncSession
) -> Any:
    """Dispatch a tool call to the appropriate handler.

    Args:
        tool_name: Name of the tool to dispatch
        parameters: Tool parameters
        session: Database session

    Returns:
        Tool execution result

    Raises:
        HTTPException: If tool is not found or parameters are invalid
    """
    logger.info("Dispatching tool: %s", tool_name)

    tool_handlers = {
        TOOL_MATCH_ROLE: (_validate_match_role_params, match_role),
        TOOL_EXPLAIN_MATCH: (_validate_explain_match_params, explain_match),
        TOOL_GENERATE_CV: (_validate_generate_cv_params, generate_cv),
        TOOL_GRAPH_SEARCH: (_validate_graph_search_params, graph_search),
    }

    if tool_name not in tool_handlers:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

    validate_func, handler_func = tool_handlers[tool_name]
    validate_func(parameters)
    try:
        return await handler_func(parameters, session)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
