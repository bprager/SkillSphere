import pytest
from fastapi.testclient import TestClient
from fastapi import status
import numpy as np

from skill_sphere_mcp.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/v1/healthz")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_entity_not_found(monkeypatch):
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

    monkeypatch.setattr("skill_sphere_mcp.db.connection.neo4j_conn.get_session", mock_get_session)

    response = client.get("/v1/entity/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Entity not found"}

@pytest.mark.asyncio
async def test_search_semantic(monkeypatch):
    # Mock the embedding model and neo4j session
    class MockModel:
        def encode(self, query):
            return np.array([0.1, 0.2, 0.3])

    monkeypatch.setattr("skill_sphere_mcp.routes.MODEL", MockModel())

    class MockRecord:
        def __init__(self, id, embedding):
            self._id = id
            self._embedding = embedding
        def __getitem__(self, key):
            if key == "id":
                return self._id
            if key == "embedding":
                return self._embedding

    class MockResult:
        async def __aiter__(self):
            yield MockRecord(1, [0.1, 0.2, 0.3])
        async def __anext__(self):
            raise StopAsyncIteration

    class MockSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def run(self, *args, **kwargs):
            return MockResult()

    async def mock_get_session():
        yield MockSession()

    monkeypatch.setattr("skill_sphere_mcp.db.connection.neo4j_conn.get_session", mock_get_session)

    response = client.post("/v1/search", json={"query": "test", "k": 1})
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert isinstance(json_data, list)
    assert len(json_data) <= 1
    if json_data:
        assert "entity_id" in json_data[0]
        assert "score" in json_data[0]
