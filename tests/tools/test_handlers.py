import pytest
from unittest.mock import AsyncMock

from fastapi import HTTPException
from skill_sphere_mcp.tools.handlers import (
    explain_match,
    generate_cv,
    graph_search,
    match_role,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_explain_match_success(mock_session: AsyncMock) -> None:
    """Test successful match explanation."""
    mock_record = {
        "s": {"name": "Python"},
        "projects": [{"name": "Project 1"}],
        "certifications": [{"name": "Cert 1"}],
    }
    mock_session.run.return_value.single.return_value = mock_record

    result = await explain_match(
        {"skill_id": "123", "role_requirement": "Python developer"},
        mock_session,
    )
    assert "explanation" in result
    assert "evidence" in result
    assert len(result["evidence"]) == 2


@pytest.mark.asyncio
async def test_explain_match_missing_params(mock_session: AsyncMock) -> None:
    """Test match explanation with missing parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await explain_match({}, mock_session)
    assert exc_info.value.status_code == 400
    assert "Missing required parameters" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_explain_match_skill_not_found(mock_session: AsyncMock) -> None:
    """Test match explanation with non-existent skill."""
    mock_session.run.return_value.single.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await explain_match(
            {"skill_id": "999", "role_requirement": "Python developer"},
            mock_session,
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_graph_search_success(mock_session: AsyncMock) -> None:
    """Test successful graph search."""
    mock_records = [{"n": {"name": "Node 1"}}, {"n": {"name": "Node 2"}}]
    mock_session.run.return_value.all.return_value = mock_records

    result = await graph_search({"query": "test", "top_k": 2}, mock_session)
    assert "results" in result
    assert len(result["results"]) == 2


@pytest.mark.asyncio
async def test_graph_search_missing_query(mock_session: AsyncMock) -> None:
    """Test graph search with missing query."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({}, mock_session)
    assert exc_info.value.status_code == 400
    assert "Missing query parameter" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_graph_search_invalid_top_k(mock_session: AsyncMock) -> None:
    """Test graph search with invalid top_k."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({"query": "test", "top_k": 0}, mock_session)
    assert exc_info.value.status_code == 400
    assert "top_k must be greater than 0" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_generate_cv_success(mock_session: AsyncMock) -> None:
    """Test successful CV generation."""
    mock_record = {
        "p": {"name": "John"},
        "skills": [{"name": "Python"}],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record

    result = await generate_cv(
        {"target_keywords": ["Python"], "format": "markdown"},
        mock_session,
    )
    assert "content" in result
    assert "format" in result
    assert result["format"] == "markdown"
    assert "# John" in result["content"]


@pytest.mark.asyncio
async def test_generate_cv_missing_params(mock_session: AsyncMock) -> None:
    """Test CV generation with missing parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv({}, mock_session)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_generate_cv_profile_not_found(mock_session: AsyncMock) -> None:
    """Test CV generation with non-existent profile."""
    mock_session.run.return_value.single.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {"target_keywords": ["Python"], "format": "markdown"},
            mock_session,
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_generate_cv_invalid_format(mock_session: AsyncMock) -> None:
    """Test CV generation with invalid format."""
    mock_record = {
        "p": {"name": "John"},
        "skills": [{"name": "Python"}],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {"target_keywords": ["Python"], "format": "invalid"},
            mock_session,
        )
    assert exc_info.value.status_code == 400
