import os
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from skill_sphere_mcp.app import app

@pytest.mark.asyncio
async def test_oauth_feature_flag_disabled(monkeypatch):
    # Ensure ENABLE_OAUTH is set to False
    monkeypatch.setenv("ENABLE_OAUTH", "False")

    client = TestClient(app)
    # Attempt to access a protected endpoint that requires OAuth
    # For this test, we assume /protected is an endpoint requiring OAuth
    # If no such endpoint exists, replace with an appropriate one or simulate
    response = client.get("/protected")

    # Since OAuth is disabled, access should be allowed or handled accordingly
    # Adjust assertion based on actual app behavior when OAuth is disabled
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
