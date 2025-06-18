"""Tests for CV generation functionality."""

from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
import pytest_asyncio

from fastapi import HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.cv.generator import generate_cv


@pytest_asyncio.fixture
async def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_generate_cv_success(mock_session: AsyncMock) -> None:
    """Test successful CV generation with markdown format."""
    # Mock database response
    mock_record = {
        "p": {
            "name": "John Doe",
            "title": "Software Engineer",
            "summary": "Experienced developer",
            "email": "john@example.com",
            "phone": "123-456-7890",
            "location": "New York",
        },
        "skills": [
            {"name": "Python", "level": "Expert"},
            {"name": "FastAPI", "level": "Intermediate"},
        ],
        "companies": [
            {
                "name": "Tech Corp",
                "position": "Senior Developer",
                "start_date": "2020-01",
                "end_date": "2023-12",
                "description": "Led development team",
            }
        ],
        "education": [
            {
                "institution": "University",
                "degree": "BS Computer Science",
                "start_date": "2016-09",
                "end_date": "2020-05",
            }
        ],
    }
    mock_session.run.return_value.single.return_value = mock_record

    result = await generate_cv(
        {
            "target_keywords": ["Python", "FastAPI"],
            "format": "markdown",
        },
        mock_session,
    )

    assert result["format"] == "markdown"
    assert "content" in result
    content = result["content"]
    assert "John Doe" in content
    assert "Email: john@example.com" in content
    assert "Phone: 123-456-7890" in content
    assert "Summary" in content
    assert "Skills" in content
    assert "Python" in content
    assert "FastAPI" in content
    assert "Experience" in content
    assert "Tech Corp" in content
    assert "Education" in content
    assert "University" in content


@pytest.mark.asyncio
async def test_generate_cv_html_format(mock_session: AsyncMock) -> None:
    """Test CV generation with HTML format."""
    mock_record = {
        "p": {"name": "John Doe", "title": "Developer"},
        "skills": [{"name": "Python"}],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record

    result = await generate_cv(
        {
            "target_keywords": ["Python"],
            "format": "html",
        },
        mock_session,
    )

    assert result["format"] == "html"
    assert "content" in result
    content = result["content"]
    assert "<h1>John Doe</h1>" in content
    assert "<h2>Skills</h2>" in content
    assert "<li>Python</li>" in content


@pytest.mark.asyncio
async def test_generate_cv_pdf_format(mock_session: AsyncMock) -> None:
    """Test CV generation with PDF format."""
    mock_record = {
        "p": {"name": "John Doe", "title": "Developer"},
        "skills": [{"name": "Python"}],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record

    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {
                "target_keywords": ["Python"],
                "format": "pdf",
            },
            mock_session,
        )
    assert exc_info.value.status_code == 501
    assert "PDF format not implemented" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_generate_cv_missing_keywords(mock_session: AsyncMock) -> None:
    """Test CV generation with missing target keywords."""
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {
                "format": "markdown",
            },
            mock_session,
        )
    assert exc_info.value.status_code == 422
    assert "target_keywords" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_generate_cv_invalid_format(mock_session: AsyncMock) -> None:
    """Test CV generation with invalid format."""
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {
                "target_keywords": ["Python"],
                "format": "invalid",
            },
            mock_session,
        )
    assert exc_info.value.status_code == 422
    assert "format" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_generate_cv_empty_profile(mock_session: AsyncMock) -> None:
    """Test CV generation with empty profile data."""
    mock_record = {
        "p": {"name": "John Doe"},
        "skills": [],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record

    result = await generate_cv(
        {
            "target_keywords": ["Python"],
            "format": "markdown",
        },
        mock_session,
    )

    assert result["format"] == "markdown"
    assert "content" in result
    content = result["content"]
    assert "John Doe" in content
    assert "Skills" in content
    assert "Experience" in content
    assert "Education" in content


@pytest.mark.asyncio
async def test_generate_cv_database_error(mock_session: AsyncMock) -> None:
    """Test CV generation with database error."""
    mock_session.run.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {
                "target_keywords": ["Python"],
                "format": "markdown",
            },
            mock_session,
        )
    assert exc_info.value.status_code == 500
    assert "Database error" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_generate_cv_no_profile_found(mock_session: AsyncMock) -> None:
    """Test CV generation when no profile is found."""
    mock_session.run.return_value.single.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {
                "target_keywords": ["Python"],
                "format": "markdown",
            },
            mock_session,
        )
    assert exc_info.value.status_code == 404
    assert "Profile not found" in str(exc_info.value.detail) 