"""Tests for Node2Vec embeddings and graph search functionality."""

# pylint: disable=redefined-outer-name

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
import pytest_asyncio
from neo4j import AsyncSession

from skill_sphere_mcp.graph.embeddings import Node2VecEmbeddings, embeddings

# Create a random number generator for testing
rng = np.random.default_rng(42)

# Constants for test configuration
TEST_DIMENSION = 128
TEST_DIMENSION_SMALL = 64
TEST_TOP_K = 2
TEST_NUM_NODES = 2
TEST_NUM_EMPTY = 0
TEST_MIN_SCORE = -1.0
TEST_MAX_SCORE = 1.0
EXPECTED_EMBEDDINGS_COUNT = 2


@pytest_asyncio.fixture
async def mock_session() -> AsyncMock:
    """Create mock Neo4j session."""
    session = AsyncMock(spec=AsyncSession)
    session.close = AsyncMock()
    return session


@pytest_asyncio.fixture(autouse=True)
async def cleanup_session(mock_session: AsyncMock) -> AsyncGenerator[None, None]:
    """Cleanup fixture to close Neo4j session after each test."""
    yield
    await mock_session.close()


@pytest_asyncio.fixture
async def mock_result() -> AsyncMock:
    """Create mock Neo4j result."""
    result = AsyncMock()
    result.__aiter__ = AsyncMock()
    result.__anext__ = AsyncMock()
    return result


@pytest_asyncio.fixture
async def sample_nodes() -> list[dict]:
    """Create sample node data."""
    return [
        {
            "node_id": 1,
            "labels": ["Node"],
            "props": {"name": "Node1"},
            "edges": [{"target": 2, "type": "RELATES_TO"}],
        },
        {
            "node_id": 2,
            "labels": ["Node"],
            "props": {"name": "Node2"},
            "edges": [{"target": 1, "type": "RELATES_TO"}],
        },
    ]


@pytest_asyncio.fixture
async def mock_embeddings() -> dict[str, np.ndarray]:
    """Create mock embeddings."""
    return {
        "1": rng.random(128),
        "2": rng.random(128),
    }


@pytest_asyncio.fixture
async def test_embeddings_initialization() -> None:
    """Test Node2VecEmbeddings initialization."""
    emb = Node2VecEmbeddings(dimension=TEST_DIMENSION_SMALL)
    assert emb.dimension == TEST_DIMENSION_SMALL
    assert emb.get_embedding("1") is None


class AsyncRecordIterator:
    """Async iterator for mock Neo4j records."""

    def __init__(self, records: list):
        self.records = records
        self.index = 0

    def __aiter__(self) -> "AsyncRecordIterator":
        return self

    async def __anext__(self) -> Any:
        if self.index >= len(self.records):
            raise StopAsyncIteration
        record = self.records[self.index]
        self.index += 1
        return record


@pytest_asyncio.fixture
async def test_load_embeddings(
    mock_session: AsyncMock, mock_result: AsyncMock, sample_nodes: list[dict]
) -> None:
    """Test loading embeddings from graph."""
    # Setup mock result
    mock_result.__aiter__ = lambda self: AsyncRecordIterator(sample_nodes)
    mock_session.run.return_value = mock_result

    # Create embeddings instance
    emb = Node2VecEmbeddings(dimension=TEST_DIMENSION)

    # Mock Node2Vec
    with patch("skill_sphere_mcp.graph.embeddings.Node2Vec") as mock_node2vec:
        mock_model = MagicMock()
        mock_model.get_all_embeddings.return_value = {
            "1": rng.random(TEST_DIMENSION),
            "2": rng.random(TEST_DIMENSION),
        }
        mock_instance = mock_node2vec.return_value
        mock_instance.fit = AsyncMock()

        # Load embeddings
        await emb.load_embeddings(mock_session)

        # Verify Node2Vec was created and fit was called
        mock_node2vec.assert_called_once()
        mock_instance.fit.assert_called_once_with(mock_session)

        # Verify embeddings were stored
        assert emb.model is not None
        embeddings = emb.get_all_embeddings()
        assert len(embeddings) == EXPECTED_EMBEDDINGS_COUNT
        assert "1" in embeddings
        assert "2" in embeddings


@pytest_asyncio.fixture
async def test_load_embeddings_empty_graph(
    mock_session: AsyncMock, mock_result: AsyncMock
) -> None:
    """Test loading embeddings from an empty graph."""
    # Setup mock result for empty graph
    mock_result.__aiter__ = lambda self: AsyncRecordIterator([])
    mock_session.run.return_value = mock_result

    # Create embeddings instance
    emb = Node2VecEmbeddings(dimension=TEST_DIMENSION)

    # Mock Node2Vec
    with patch("skill_sphere_mcp.graph.embeddings.Node2Vec") as mock_node2vec:
        mock_model = MagicMock()
        mock_model.wv = {}
        mock_node2vec.return_value.fit.return_value = mock_model

        # Load embeddings
        await emb.load_embeddings(mock_session)

        # Verify empty embeddings
        assert emb.get_embedding("1") is None
        assert emb.get_embedding("2") is None


@pytest_asyncio.fixture
async def test_load_embeddings_error_handling(mock_session: AsyncMock) -> None:
    """Test error handling in load_embeddings."""
    # Setup mock session to raise an exception
    mock_session.run.side_effect = Exception("Database error")

    # Create embeddings instance
    emb = Node2VecEmbeddings(dimension=128)

    # Test that the exception is propagated
    with pytest.raises(Exception) as exc_info:
        await emb.load_embeddings(mock_session)
    assert str(exc_info.value) == "Database error"


@pytest_asyncio.fixture
async def test_search(
    mock_session: AsyncMock,
    mock_embeddings: dict[str, np.ndarray],
) -> None:
    """Test searching for similar nodes."""
    # Setup mock result for node details
    search_result = AsyncMock()
    search_result.single.return_value = {
        "labels": ["Node"],
        "props": {"name": "TestNode"},
    }
    mock_session.run.return_value = search_result

    # Create embeddings instance with mock data
    emb = Node2VecEmbeddings(dimension=TEST_DIMENSION)
    emb.set_all_embeddings(mock_embeddings)

    # Create query embedding
    query_embedding = rng.random(TEST_DIMENSION)

    # Test search
    results = await emb.search(mock_session, query_embedding, top_k=TEST_TOP_K)

    # Verify results
    assert len(results) == TEST_TOP_K
    for result in results:
        assert "node_id" in result
        assert "score" in result
        assert "labels" in result
        assert "properties" in result
        assert isinstance(result["score"], float)
        assert TEST_MIN_SCORE <= result["score"] <= TEST_MAX_SCORE


@pytest_asyncio.fixture
async def test_search_empty_embeddings(mock_session: AsyncMock) -> None:
    """Test search with empty embeddings."""
    # Create embeddings instance
    emb = Node2VecEmbeddings(dimension=TEST_DIMENSION)

    # Setup mock result for load_embeddings
    empty_result = AsyncMock()
    empty_result.__aiter__ = lambda self: AsyncRecordIterator([])
    mock_session.run.return_value = empty_result

    # Create query embedding
    query_embedding = rng.random(TEST_DIMENSION)

    # Test search
    results = await emb.search(mock_session, query_embedding, top_k=TEST_TOP_K)

    # Verify empty results
    assert len(results) == TEST_NUM_EMPTY


@pytest_asyncio.fixture
async def test_search_invalid_node(
    mock_session: AsyncMock, mock_embeddings: dict[str, np.ndarray]
) -> None:
    """Test search with invalid node in results."""
    # Setup mock result to return None for node details
    invalid_result = AsyncMock()
    invalid_result.single.return_value = None
    mock_session.run.return_value = invalid_result

    # Create embeddings instance with mock data
    emb = Node2VecEmbeddings(dimension=TEST_DIMENSION)
    emb.set_all_embeddings(mock_embeddings)

    # Create query embedding
    query_embedding = rng.random(TEST_DIMENSION)

    # Test search
    results = await emb.search(mock_session, query_embedding, top_k=TEST_TOP_K)

    # Verify results exclude invalid nodes
    assert len(results) == TEST_NUM_EMPTY


def test_get_embedding(mock_embeddings: dict[str, np.ndarray]) -> None:
    """Test getting embedding for a specific node."""
    emb = Node2VecEmbeddings(dimension=TEST_DIMENSION)
    emb.set_all_embeddings(mock_embeddings)

    # Test existing node
    embedding = emb.get_embedding("1")
    assert embedding is not None
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (TEST_DIMENSION,)

    # Test non-existing node
    embedding = emb.get_embedding("3")
    assert embedding is None


@pytest_asyncio.fixture
async def test_global_embeddings_instance() -> None:
    """Test that the global embeddings instance is properly initialized."""
    # Verify that embeddings is an instance of Node2VecEmbeddings
    assert isinstance(embeddings, Node2VecEmbeddings)
    assert embeddings.dimension == TEST_DIMENSION
