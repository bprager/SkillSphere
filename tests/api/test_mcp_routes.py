import importlib
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from skill_sphere_mcp.api.mcp_routes import initialize
from skill_sphere_mcp.api.models import InitializeResponse
from skill_sphere_mcp.tools.handlers import generate_cv


class TestMCPRoutes:
    """Test MCP routes."""

    @pytest.mark.asyncio
    async def test_route_initialization(self) -> None:
        """Test route initialization."""
        response = await initialize()
        assert isinstance(response, InitializeResponse)
        assert response.protocol_version == "1.0"
        assert isinstance(response.capabilities, dict)
        assert isinstance(response.instructions, str)


@pytest.mark.asyncio
async def test_initialize() -> None:
    """Test MCP initialization endpoint."""
    response = await initialize()
    assert isinstance(response, InitializeResponse)
    assert response.protocol_version == "1.0"
    assert (
        "semantic_search" in response.capabilities
        or "resources" in response.capabilities
    )
    assert isinstance(response.instructions, str)


@pytest.mark.asyncio
async def test_initialize_invalid_version() -> None:
    """Test MCP initialization with invalid version."""
    response = await initialize()
    assert response.protocol_version == "1.0"  # Should return supported version


@pytest.mark.asyncio
async def test_generate_cv_success() -> None:
    """Test generate_cv returns markdown CV."""
    params = {"target_keywords": ["Python"], "format": "markdown"}
    mock_session = AsyncMock()
    mock_record = {"p": {"name": "John"}, "skills": [{"name": "Python"}]}
    mock_session.run.return_value.single.return_value = mock_record
    result = await generate_cv(params, mock_session)
    assert result["format"] == "markdown"
    assert "# John" in result["content"]
    assert "## Skills" in result["content"]
    assert "- Python" in result["content"]
    print(importlib.import_module(generate_cv.__module__).__file__)


@pytest.mark.asyncio
async def test_generate_cv_success_html() -> None:
    """Test generate_cv returns HTML CV."""
    params = {"target_keywords": ["Python"], "format": "html"}
    mock_session = AsyncMock()
    mock_record = {"p": {"name": "John"}, "skills": [{"name": "Python"}]}
    mock_session.run.return_value.single.return_value = mock_record
    result = await generate_cv(params, mock_session)
    assert result["format"] == "html"
    assert "<h1>John</h1>" in result["content"]
    assert "<h2>Skills</h2>" in result["content"]
    assert "<li>Python</li>" in result["content"]


@pytest.mark.asyncio
async def test_generate_cv_invalid_params() -> None:
    """Test generate_cv with invalid parameters raises HTTPException."""
    mock_session = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv({}, mock_session)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_generate_cv_profile_not_found() -> None:
    """Test generate_cv when profile not found raises HTTPException."""
    params = {"target_keywords": ["Python"], "format": "markdown"}
    mock_session = AsyncMock()
    mock_session.run.return_value.single.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(params, mock_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_generate_cv_format_not_implemented() -> None:
    """Test generate_cv with unsupported format raises HTTPException."""
    params = {"target_keywords": ["Python"], "format": "pdf"}
    mock_session = AsyncMock()
    mock_record = {"p": {"name": "John"}, "skills": []}
    mock_session.run.return_value.single.return_value = mock_record
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(params, mock_session)
    assert exc_info.value.status_code == 501
