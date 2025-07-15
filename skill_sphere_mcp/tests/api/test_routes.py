"""Tests for API routes."""

from unittest.mock import AsyncMock

import numpy as np
import pytest

from fastapi import status
from fastapi.testclient import TestClient
from tests.constants import AsyncIterator

from skill_sphere_mcp.app import app
from skill_sphere_mcp.db.deps import get_db_session


client = TestClient(app)

def test_health_check():
    response = client.get("/v1/healthz")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_entity_not_found():
    # Mock the neo4j session to return no record
    async def mock_run(*args, **kwargs):
        class MockResult:
            async def single(self):
                return None
        return MockResult()

    class MockSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def run(self, *args, **kwargs):
            return await mock_run()

    async def mock_get_session():
        yield MockSession()

    app.dependency_overrides[get_db_session] = mock_get_session

    response = client.get("/v1/entity/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Entity not found"}

    app.dependency_overrides = {}  # Clean up after test

@pytest.mark.asyncio
async def test_search_semantic():
    """Test semantic search endpoint."""
    # Mock the database session
    async def mock_get_session():
        mock_session = AsyncMock()
        mock_result = AsyncIterator([
            {
                "n": {
                    "id": "1",
                    "name": "Python",
                    "type": "Skill",
                    "description": "Python programming language"
                }
            }
        ])
        mock_session.run.return_value = mock_result
        yield mock_session

    app.dependency_overrides[get_db_session] = mock_get_session
    
    try:
        response = client.post("/v1/search", json={"query": "Python", "k": 10})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "entity_id" in data[0]
        assert "score" in data[0]
    finally:
        app.dependency_overrides.clear()
