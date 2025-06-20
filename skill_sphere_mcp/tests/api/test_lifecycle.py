import pytest
from fastapi.testclient import TestClient
from fastapi import status

from skill_sphere_mcp.app import app

@pytest.mark.asyncio
async def test_initialize_and_shutdown_lifecycle():
    client = TestClient(app)
    
    # Test initialize
    init_payload = {
        "jsonrpc": "2.0",
        "method": "mcp.initialize",
        "params": {},
        "id": 1
    }
    response = client.post("/mcp/rpc", json=init_payload)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "result" in json_data

    # Test initialized
    initialized_payload = {
        "jsonrpc": "2.0",
        "method": "mcp.initialized",
        "params": {},
        "id": 2
    }
    response = client.post("/mcp/rpc", json=initialized_payload)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "result" in json_data

    # Test shutdown
    shutdown_payload = {
        "jsonrpc": "2.0",
        "method": "mcp.shutdown",
        "params": {},
        "id": 3
    }
    response = client.post("/mcp/rpc", json=shutdown_payload)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "result" in json_data
