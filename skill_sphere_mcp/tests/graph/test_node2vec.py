"""Tests for Node2Vec implementation."""

# pylint: disable=redefined-outer-name

from typing import Any, Callable
from unittest.mock import AsyncMock

import numpy as np
import pytest
from neo4j import AsyncSession

from skill_sphere_mcp.graph.node2vec import Node2Vec, Node2VecConfig

# Constants for test configuration
DEFAULT_DIMENSION = 128
DEFAULT_WALK_LENGTH = 80
DEFAULT_NUM_WALKS = 10
DEFAULT_P = 1.0
DEFAULT_Q = 1.0
DEFAULT_WINDOW_SIZE = 5
DEFAULT_NUM_NEG_SAMPLES = 5
DEFAULT_LEARNING_RATE = 0.025
DEFAULT_EPOCHS = 5

# Constants for test values
TEST_DIMENSION = 4
TEST_WALK_LENGTH = 3
TEST_NUM_WALKS = 2
TEST_WINDOW_SIZE = 1
TEST_NUM_NEG_SAMPLES = 1
TEST_EPOCHS = 1
TEST_CONTEXT_SIZE = 2

# Constants for custom configuration
CUSTOM_DIMENSION = 64
CUSTOM_WALK_LENGTH = 40
CUSTOM_NUM_WALKS = 5
CUSTOM_P = 2.0
CUSTOM_Q = 0.5
CUSTOM_WINDOW_SIZE = 3
CUSTOM_NUM_NEG_SAMPLES = 3
CUSTOM_LEARNING_RATE = 0.01
CUSTOM_EPOCHS = 3

# Constants for alias sampling
ALIAS_Q_VALUE = 5

# Constants for test graph
EXPECTED_NUM_NODES = 4

# Create a random number generator for testing
rng = np.random.default_rng(42)


class AsyncIterator:
    """Async iterator for mocking Neo4j query results in tests."""

    def __init__(self, items: list) -> None:
        self._iter = iter(items)

    def __aiter__(self) -> "AsyncIterator":
        return self

    async def __anext__(self) -> dict:
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration from None


@pytest.fixture
def test_mock_session() -> AsyncMock:
    """Create mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def test_mock_result() -> AsyncMock:
    """Create mock Neo4j result."""
    return AsyncMock()


@pytest.fixture
def test_sample_graph() -> dict[str, list[str]]:
    """Create sample graph data."""
    return {
        "1": ["2", "3"],
        "2": ["1", "3", "4"],
        "3": ["1", "2", "4"],
        "4": ["2", "3"],
    }


@pytest.fixture
def test_node2vec() -> Node2Vec:
    """Create Node2Vec instance with test configuration."""
    config = Node2VecConfig(
        dimension=TEST_DIMENSION,
        walk_length=TEST_WALK_LENGTH,
        num_walks=TEST_NUM_WALKS,
        window_size=TEST_WINDOW_SIZE,
        num_neg_samples=TEST_NUM_NEG_SAMPLES,
        epochs=TEST_EPOCHS,
    )
    return Node2Vec(config)


def test_node2vec_config_defaults() -> None:
    """Test Node2VecConfig default values."""
    config = Node2VecConfig()
    assert config.dimension == DEFAULT_DIMENSION
    assert config.walk_length == DEFAULT_WALK_LENGTH
    assert config.num_walks == DEFAULT_NUM_WALKS
    assert config.p == DEFAULT_P
    assert config.q == DEFAULT_Q
    assert config.window_size == DEFAULT_WINDOW_SIZE
    assert config.num_neg_samples == DEFAULT_NUM_NEG_SAMPLES
    assert config.learning_rate == DEFAULT_LEARNING_RATE
    assert config.epochs == DEFAULT_EPOCHS


def test_node2vec_config_custom() -> None:
    """Test Node2VecConfig with custom values."""
    config = Node2VecConfig(
        dimension=CUSTOM_DIMENSION,
        walk_length=CUSTOM_WALK_LENGTH,
        num_walks=CUSTOM_NUM_WALKS,
        p=CUSTOM_P,
        q=CUSTOM_Q,
        window_size=CUSTOM_WINDOW_SIZE,
        num_neg_samples=CUSTOM_NUM_NEG_SAMPLES,
        learning_rate=CUSTOM_LEARNING_RATE,
        epochs=CUSTOM_EPOCHS,
    )
    assert config.dimension == CUSTOM_DIMENSION
    assert config.walk_length == CUSTOM_WALK_LENGTH
    assert config.num_walks == CUSTOM_NUM_WALKS
    assert config.p == CUSTOM_P
    assert config.q == CUSTOM_Q
    assert config.window_size == CUSTOM_WINDOW_SIZE
    assert config.num_neg_samples == CUSTOM_NUM_NEG_SAMPLES
    assert config.learning_rate == CUSTOM_LEARNING_RATE
    assert config.epochs == CUSTOM_EPOCHS


def make_aiter(items: list) -> Callable[..., AsyncIterator]:
    def _aiter(*args: Any, **kwargs: Any) -> AsyncIterator:
        return AsyncIterator(items)

    return _aiter


@pytest.mark.asyncio
async def test_get_graph(
    test_node2vec: Node2Vec, test_mock_session: AsyncMock, test_mock_result: AsyncMock
) -> None:
    """Test graph retrieval from Neo4j."""
    # Setup mock result
    records = [
        {"node_id": 1, "neighbors": [2, 3]},
        {"node_id": 2, "neighbors": [1, 3, 4]},
        {"node_id": 3, "neighbors": [1, 2, 4]},
        {"node_id": 4, "neighbors": [2, 3]},
    ]
    test_mock_result.__aiter__ = make_aiter(records)
    test_mock_session.run.return_value = test_mock_result

    # Get graph
    graph = await test_node2vec.get_graph(test_mock_session)

    # Verify graph structure
    assert len(graph) == EXPECTED_NUM_NODES
    assert graph["1"] == ["2", "3"]
    assert graph["2"] == ["1", "3", "4"]
    assert graph["3"] == ["1", "2", "4"]
    assert graph["4"] == ["2", "3"]


@pytest.mark.asyncio
async def test_get_graph_empty(
    test_node2vec: Node2Vec, test_mock_session: AsyncMock, test_mock_result: AsyncMock
) -> None:
    """Test graph retrieval with empty result."""
    # Setup mock result for empty graph
    test_mock_result.__aiter__ = make_aiter([])
    test_mock_session.run.return_value = test_mock_result

    # Get graph
    graph = await test_node2vec.get_graph(test_mock_session)

    # Verify empty graph
    assert len(graph) == 0


@pytest.mark.asyncio
async def test_get_graph_error(
    test_node2vec: Node2Vec, test_mock_session: AsyncMock
) -> None:
    """Test graph retrieval error handling."""
    # Setup mock session to raise an exception
    test_mock_session.run.side_effect = Exception("Database error")

    # Test that the exception is propagated
    with pytest.raises(Exception) as exc_info:
        await test_node2vec.get_graph(test_mock_session)
    assert str(exc_info.value) == "Database error"


def test_preprocess_transition_probs(
    test_node2vec: Node2Vec, test_sample_graph: dict[str, list[str]]
) -> None:
    """Test transition probability preprocessing."""
    test_node2vec.preprocess_transition_probs(test_sample_graph)

    # Verify alias nodes
    alias_nodes = test_node2vec.get_alias_nodes()
    assert "1" in alias_nodes
    assert "2" in alias_nodes
    assert "3" in alias_nodes
    assert "4" in alias_nodes

    # Verify alias edges
    alias_edges = test_node2vec.get_alias_edges()
    assert ("1", "2") in alias_edges
    assert ("2", "1") in alias_edges
    assert ("2", "3") in alias_edges
    assert ("3", "2") in alias_edges


def test_alias_setup(test_node2vec: Node2Vec) -> None:
    """Test alias sampling setup."""
    probs = [0.1, 0.2, 0.3, 0.4]
    alias = test_node2vec.alias_setup(probs)

    assert "J" in alias
    assert "q" in alias
    assert len(alias["J"]) == len(probs)
    assert len(alias["q"]) == len(probs)


def test_alias_draw(test_node2vec: Node2Vec) -> None:
    """Test alias sampling."""
    alias: dict[str, list[int]] = {
        "J": [1, 0, 1, 2],
        "q": [ALIAS_Q_VALUE, ALIAS_Q_VALUE, ALIAS_Q_VALUE, ALIAS_Q_VALUE],
    }
    result = test_node2vec.alias_draw(alias, 0)
    assert isinstance(result, int)
    assert result in [0, 1]


def test_node2vec_walk(
    test_node2vec: Node2Vec, test_sample_graph: dict[str, list[str]]
) -> None:
    """Test random walk generation."""
    # Initialize alias nodes first
    test_node2vec.preprocess_transition_probs(test_sample_graph)
    walk = test_node2vec.node2vec_walk("1", test_sample_graph)
    assert len(walk) <= test_node2vec.walk_length
    assert walk[0] == "1"
    assert all(node in test_sample_graph for node in walk)


def test_node2vec_walk_isolated_node(
    test_node2vec: Node2Vec, test_sample_graph: dict[str, list[str]]
) -> None:
    """Test random walk generation for isolated node."""
    # Add isolated node to graph
    test_sample_graph["5"] = []

    # Test walk
    walk = test_node2vec.node2vec_walk("5", test_sample_graph)
    assert len(walk) == 1
    assert walk[0] == "5"


def test_generate_walks(
    test_node2vec: Node2Vec, test_sample_graph: dict[str, list[str]]
) -> None:
    """Test walk generation for all nodes."""
    # Initialize alias nodes first
    test_node2vec.preprocess_transition_probs(test_sample_graph)
    walks = test_node2vec.generate_walks(test_sample_graph)
    assert len(walks) == test_node2vec.num_walks * len(test_sample_graph)
    assert all(len(walk) <= test_node2vec.walk_length for walk in walks)
    assert all(walk[0] in test_sample_graph for walk in walks)


def test_generate_walks_empty_graph(test_node2vec: Node2Vec) -> None:
    """Test walk generation for empty graph."""
    empty_graph: dict[str, list[str]] = {}
    walks = test_node2vec.generate_walks(empty_graph)
    assert len(walks) == 0


def test_initialize_embeddings(test_node2vec: Node2Vec) -> None:
    """Test embedding initialization."""
    nodes = {"1", "2", "3"}
    test_node2vec.initialize_embeddings(nodes)

    embeddings = test_node2vec.get_all_embeddings()
    assert len(embeddings) == len(nodes)
    for node in nodes:
        assert node in embeddings
        assert embeddings[node].shape == (test_node2vec.dimension,)
        assert np.allclose(np.linalg.norm(embeddings[node]), 1.0)


def test_initialize_embeddings_empty(test_node2vec: Node2Vec) -> None:
    """Test embedding initialization with empty node set."""
    test_node2vec.initialize_embeddings(set())
    embeddings = test_node2vec.get_all_embeddings()
    assert len(embeddings) == 0


def test_get_context_nodes(test_node2vec: Node2Vec) -> None:
    """Test context node retrieval."""
    walk = ["1", "2", "3", "4", "5"]
    context = test_node2vec.get_context_nodes(walk, 2)  # Center at "3"
    assert "2" in context
    assert "3" in context
    assert "4" in context


def test_get_context_nodes_boundary(test_node2vec: Node2Vec) -> None:
    """Test context node retrieval at walk boundaries."""
    walk = ["1", "2", "3", "4", "5"]

    # Test start of walk
    context = test_node2vec.get_context_nodes(walk, 0)
    assert "1" in context
    assert "2" in context
    assert len(context) == TEST_CONTEXT_SIZE

    # Test end of walk
    context = test_node2vec.get_context_nodes(walk, 4)
    assert "4" in context
    assert "5" in context
    assert len(context) == TEST_CONTEXT_SIZE


def test_process_positive_samples(test_node2vec: Node2Vec) -> None:
    """Test positive sample processing."""
    node = "1"
    context_nodes = ["2", "3"]
    test_node2vec.initialize_embeddings({node, *context_nodes})
    test_node2vec.process_positive_samples(node, context_nodes)

    embeddings = test_node2vec.get_all_embeddings()
    assert "1" in embeddings
    assert "2" in embeddings
    assert "3" in embeddings


def test_process_negative_samples(test_node2vec: Node2Vec) -> None:
    """Test negative sample processing."""
    node = "1"
    context_nodes = ["2", "3"]
    nodes = {"1", "2", "3", "4", "5"}
    test_node2vec.initialize_embeddings(nodes)
    test_node2vec.process_negative_samples(node, context_nodes, nodes)

    embeddings = test_node2vec.get_all_embeddings()
    assert "1" in embeddings
    assert all(n in embeddings for n in nodes)


def test_update_embedding(test_node2vec: Node2Vec) -> None:
    """Test embedding update."""
    node1 = "1"
    node2 = "2"
    test_node2vec.initialize_embeddings({node1, node2})
    embeddings = test_node2vec.get_all_embeddings()
    original_vec1 = embeddings[node1].copy()
    original_vec2 = embeddings[node2].copy()

    test_node2vec.update_embedding(node1, node2, 1.0)

    # Verify embeddings were updated and normalized
    embeddings = test_node2vec.get_all_embeddings()
    assert not np.array_equal(embeddings[node1], original_vec1)
    assert not np.array_equal(embeddings[node2], original_vec2)
    assert np.allclose(np.linalg.norm(embeddings[node1]), 1.0)
    assert np.allclose(np.linalg.norm(embeddings[node2]), 1.0)


def test_get_embedding(test_node2vec: Node2Vec) -> None:
    """Test embedding retrieval."""
    node_id = "1"
    embedding = rng.random(test_node2vec.dimension)
    test_node2vec.set_embedding(node_id, embedding)

    result = test_node2vec.get_embedding(node_id)
    assert result is not None
    assert np.array_equal(result, embedding)

    # Test non-existing node
    assert test_node2vec.get_embedding("999") is None


def test_get_all_embeddings(test_node2vec: Node2Vec) -> None:
    """Test retrieval of all embeddings."""
    embeddings = {
        "1": rng.random(test_node2vec.dimension),
        "2": rng.random(test_node2vec.dimension),
    }
    test_node2vec.set_all_embeddings(embeddings)

    result = test_node2vec.get_all_embeddings()
    assert result == embeddings


@pytest.mark.asyncio
async def test_fit(
    test_node2vec: Node2Vec, test_mock_session: AsyncMock, test_mock_result: AsyncMock
) -> None:
    """Test the complete training process."""
    # Setup mock result for graph retrieval
    records = [
        {"node_id": 1, "neighbors": [2, 3]},
        {"node_id": 2, "neighbors": [1, 3, 4]},
        {"node_id": 3, "neighbors": [1, 2, 4]},
        {"node_id": 4, "neighbors": [2, 3]},
    ]
    test_mock_result.__aiter__ = make_aiter(records)
    test_mock_session.run.return_value = test_mock_result

    # Run training
    await test_node2vec.fit(test_mock_session)

    # Verify embeddings were created
    embeddings = test_node2vec.get_all_embeddings()
    assert len(embeddings) == EXPECTED_NUM_NODES
    for node_id in ["1", "2", "3", "4"]:
        assert node_id in embeddings
        assert embeddings[node_id].shape == (test_node2vec.dimension,)
        assert np.allclose(np.linalg.norm(embeddings[node_id]), 1.0)
