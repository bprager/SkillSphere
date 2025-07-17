"""Tool dispatcher for MCP operations."""

import logging
from typing import Any

from fastapi import HTTPException
from neo4j import AsyncSession
from pydantic import BaseModel

from skill_sphere_mcp.tools.handlers import (
    ExplainMatchOutputModel,
    GraphSearchOutputModel,
    MatchRoleOutputModel,
    explain_match,
    graph_search,
    match_role,
)

# HTTP Status Constants
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_BAD_REQUEST = 400


async def generate_cv(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Generate CV in the specified format.

    This is a stub function to satisfy mypy type checking.
    The actual implementation would generate a CV based on the provided arguments.

    Returns:
        Empty dictionary as placeholder result
    """
    # Stub for generate_cv to satisfy mypy
    return {}


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

    # Validate format
    valid_formats = ["markdown", "html", "pdf"]
    format_value = parameters.get("format")
    if format_value not in valid_formats:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid format: {format_value}. Valid formats are: {', '.join(valid_formats)}",
        )


def _validate_graph_search_params(parameters: dict[str, Any]) -> None:
    """Validate graph_search parameters."""
    if not parameters.get("query"):
        raise HTTPException(status_code=422, detail="Query is required")
    top_k = parameters.get("top_k", 10)
    if not isinstance(top_k, int) or top_k <= 0:
        raise HTTPException(status_code=422, detail="top_k must be a positive integer")


async def dispatch_tool(
    tool_name: str,
    parameters: dict[str, Any],
    session: AsyncSession,
    structured_output: bool = False,
) -> dict[str, Any]:
    """Dispatch tool execution to appropriate handler.

    Args:
        tool_name: Name of tool to dispatch
        parameters: Tool parameters
        session: Database session
        structured_output: Whether to wrap results in structured_result key

    Returns:
        Tool execution result

    Raises:
        HTTPException: If tool name is invalid or parameters are invalid
    """
    if not tool_name or not tool_name.strip():
        raise HTTPException(
            status_code=HTTP_UNPROCESSABLE_ENTITY, detail="Tool name is required"
        )

    # Map tool names to handlers, output models, and validators
    tool_config: dict[str, tuple[Any, type[BaseModel] | None, Any]] = {
        TOOL_MATCH_ROLE: (
            match_role,
            MatchRoleOutputModel,
            _validate_match_role_params,
        ),
        TOOL_EXPLAIN_MATCH: (
            explain_match,
            ExplainMatchOutputModel,
            _validate_explain_match_params,
        ),
        TOOL_GENERATE_CV: (generate_cv, None, _validate_generate_cv_params),
        TOOL_GRAPH_SEARCH: (
            graph_search,
            GraphSearchOutputModel,
            _validate_graph_search_params,
        ),
    }

    # Get configuration for the tool
    config = tool_config.get(tool_name)
    if not config:
        raise HTTPException(
            status_code=HTTP_UNPROCESSABLE_ENTITY, detail=f"Unknown tool: {tool_name}"
        )

    handler, output_model, validator = config

    # Validate parameters using the appropriate validator
    try:
        validator(parameters)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Tool dispatch error for %s: %s", tool_name, str(e))
        logger.error("Exception type: %s", type(e).__name__)
        logger.error("Exception args: %s", e.args)
        raise HTTPException(status_code=500, detail="Some error") from e

    # Execute handler and handle result
    try:
        result = await handler(parameters, session)
        return _format_result(result, output_model, structured_output)
    except HTTPException as e:
        if e.status_code == HTTP_UNPROCESSABLE_ENTITY:
            raise
        if e.status_code == HTTP_BAD_REQUEST and (
            "Invalid years_experience" in str(e.detail)
            or "Invalid parameters" in str(e.detail)
        ):
            raise HTTPException(
                status_code=HTTP_UNPROCESSABLE_ENTITY, detail=str(e.detail)
            ) from e
        raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
    except Exception as e:
        logger.error("Tool dispatch error for %s: %s", tool_name, str(e))
        raise HTTPException(status_code=500, detail="Some error") from e


def _format_result(
    result: Any, output_model: type[BaseModel] | None, structured_output: bool
) -> dict[str, Any]:
    """Format the result based on output model and structured output flag."""
    if output_model:
        # Validate and return structured result
        if isinstance(result, output_model):
            validated_result = result.model_dump()
        else:
            # If result is dict, validate by parsing
            validated = output_model.parse_obj(result)
            validated_result = validated.model_dump()

        # Return structured or raw based on parameter
        if structured_output:
            return {"structured_result": validated_result}
        return validated_result
    # No output model, return raw result
    if isinstance(result, dict):
        return result
    return {"result": result}
