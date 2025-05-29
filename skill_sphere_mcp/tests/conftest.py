"""Shared pytest fixtures."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from fastapi.testclient import TestClient

from skill_sphere_mcp.app import create_app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    """Create a test client for the FastAPI app."""
    yield TestClient(create_app())
