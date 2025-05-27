import pytest
from typing import Any
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_load_embeddings(
    mock_session: AsyncMock,
    mock_result: AsyncMock,
    sample_nodes: list[dict],
    _args: Any,
    _kwargs: Any,
) -> None:
    """Test loading embeddings from graph."""

    # ... existing code ...
