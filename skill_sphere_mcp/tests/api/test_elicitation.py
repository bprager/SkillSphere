import pytest
from fastapi.testclient import TestClient
from fastapi import status

from skill_sphere_mcp.app import app

@pytest.mark.asyncio
async def test_elicitation_request():
    client = TestClient(app)
    response = client.post("/elicitation/request", json={"tool_name": "test_tool"})
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "prompt" in json_data
    assert "elicitation_schema" in json_data
    assert "defaults" in json_data
    assert json_data["prompt"] == "Please provide input for tool: test_tool"
    assert "example_param" in json_data["elicitation_schema"]["properties"]
    assert json_data["defaults"]["example_param"] == "default value"
