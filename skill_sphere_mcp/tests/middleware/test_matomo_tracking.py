from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, Request
from starlette.responses import Response
from starlette.testclient import TestClient

from skill_sphere_mcp.middleware.matomo_tracking import MatomoTrackingMiddleware

app = FastAPI()
app.add_middleware(MatomoTrackingMiddleware)


@app.post("/mcp/rpc")
async def mcp_rpc(request: Request) -> Response:
    return Response(content="OK")


client = TestClient(app)


@pytest.mark.asyncio
@patch("skill_sphere_mcp.middleware.matomo_tracking.httpx.AsyncClient.post")
async def test_matomo_tracking_middleware(mock_post: AsyncMock) -> None:
    mock_post.return_value = AsyncMock()

    json_rpc_request = {
        "jsonrpc": "2.0",
        "method": "mcp.tool",
        "params": {"tool_name": "test_tool"},
        "id": "1234",
    }

    response = client.post("/mcp/rpc", json=json_rpc_request)
    expected_status_code = 200
    assert response.status_code == expected_status_code
    # Ensure Matomo tracking post was called
    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert "matomo.php" in args[0]
    params = kwargs.get("params", {})
    assert params.get("idsite") is not None
    assert params.get("e_c") == "MCP"
    assert params.get("e_a") == "/mcp/rpc"  # The actual endpoint path
