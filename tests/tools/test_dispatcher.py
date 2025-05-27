import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from skill_sphere_mcp.tools.dispatcher import dispatch_tool


@pytest.mark.asyncio
async def test_dispatch_tool_unknown(
    mock_session: AsyncMock,
) -> None:
    """Test dispatching unknown tool."""
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool("unknown_tool", {}, mock_session)
    assert exc_info.value.status_code == 400
    assert "Unknown tool" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_dispatch_tool_missing_params(
    mock_session: AsyncMock,
) -> None:
    """Test dispatching tool with missing parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool("explain_match", {}, mock_session)
    assert exc_info.value.status_code == 400
    assert "Missing required parameters" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_dispatch_tool_invalid_params(
    mock_session: AsyncMock,
) -> None:
    """Test dispatching tool with invalid parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool("explain_match", {"invalid": "param"}, mock_session)
    assert exc_info.value.status_code == 400
    assert "Invalid parameters" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_dispatch_tool_success(
    mock_session: AsyncMock,
) -> None:
    """Test successful tool dispatch."""
    result = await dispatch_tool(
        "explain_match",
        {"skill_id": "123", "role_requirement": "Python"},
        mock_session,
    )
    assert isinstance(result, dict)
    assert "explanation" in result
    assert "evidence" in result
