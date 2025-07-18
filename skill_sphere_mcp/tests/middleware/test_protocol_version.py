from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from skill_sphere_mcp.middleware.protocol_version import (
    MCP_PROTOCOL_VERSION,
    ProtocolVersionMiddleware,
)

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
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "success"}
    assert response.headers.get("MCP-Protocol-Version") == MCP_PROTOCOL_VERSION


def test_request_with_missing_protocol_version():
    response = client.get("/test")
    assert response.status_code == status.HTTP_200_OK  # Missing version is allowed
    assert response.json() == {"message": "success"}
    assert response.headers.get("MCP-Protocol-Version") == MCP_PROTOCOL_VERSION


def test_request_with_incorrect_protocol_version():
    headers = {"MCP-Protocol-Version": "wrong-version"}
    response = client.get("/test", headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == "Unsupported protocol version: wrong-version"
