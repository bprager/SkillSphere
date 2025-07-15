import pytest

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient

from skill_sphere_mcp.middleware.protocol_version import MCP_PROTOCOL_VERSION
from skill_sphere_mcp.middleware.protocol_version import ProtocolVersionMiddleware


app = FastAPI()

# Add the middleware to the app
app.add_middleware(ProtocolVersionMiddleware)

@app.get("/test")
async def test_endpoint():
    return {"message": "success"}

client = TestClient(app)

def test_request_with_correct_protocol_version():
    headers = {"MCP-Protocol-Version": MCP_PROTOCOL_VERSION}
    response = client.get("/test", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "success"}
    assert response.headers.get("MCP-Protocol-Version") == MCP_PROTOCOL_VERSION

def test_request_with_missing_protocol_version():
    response = client.get("/test")
    assert response.status_code == 200  # Missing version is allowed
    assert response.json() == {"message": "success"}
    assert response.headers.get("MCP-Protocol-Version") == MCP_PROTOCOL_VERSION

def test_request_with_incorrect_protocol_version():
    headers = {"MCP-Protocol-Version": "wrong-version"}
    response = client.get("/test", headers=headers)
    assert response.status_code == 400
    assert response.json() == "Unsupported protocol version: wrong-version"
