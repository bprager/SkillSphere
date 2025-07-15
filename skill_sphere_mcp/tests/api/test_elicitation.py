import pytest

from fastapi import status
from fastapi.testclient import TestClient

from skill_sphere_mcp.app import app


@pytest.mark.asyncio
async def test_elicitation_request():
    client = TestClient(app)
    response = client.post("/elicitation/request", json={"prompt": "Test prompt"})
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "response" in json_data
    assert "metadata" in json_data
    assert json_data["response"].startswith("Elicitation response for: Test prompt")
    assert json_data["metadata"]["status"] == "placeholder"
