"""Tests for Node2Vec implementation."""

# pylint: disable=redefined-outer-name

from collections.abc import Callable
from unittest.mock import AsyncMock

import numpy as np
import pytest
import pytest_asyncio
from neo4j import AsyncSession

from skill_sphere_mcp.graph.node2vec import Node2VecModelConfig, Node2VecTrainingConfig
from skill_sphere_mcp.graph.node2vec.config import Node2VecConfig
from skill_sphere_mcp.graph.node2vec.model import Node2Vec

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
TEST_CONTEXT_SIZE = 1
EXPECTED_CONTEXT_SIZE = 1
EXPECTED_CONTEXT_SIZE_MIDDLE = 2

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


@pytest_asyncio.fixture
async def test_mock_session() -> AsyncMock:
    """Create mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def test_mock_result() -> AsyncMock:
    """Create mock Neo4j result."""
    return AsyncMock()


@pytest_asyncio.fixture
async def test_sample_graph() -> dict[str, list[str]]:
    """Create sample graph data."""
    return {
        "1": ["2", "3"],
        "2": ["1", "3", "4"],
        "3": ["1", "2", "4"],
        "4": ["2", "3"],
    }


@pytest_asyncio.fixture
async def test_node2vec() -> Node2Vec:
    """Create Node2Vec instance with test configuration."""
    config = Node2VecConfig(
        model=Node2VecModelConfig(
            dimension=TEST_DIMENSION,
            p=DEFAULT_P,
            q=DEFAULT_Q,
        ),
        training=Node2VecTrainingConfig(
            walk_length=TEST_WALK_LENGTH,
            num_walks=TEST_NUM_WALKS,
            window_size=TEST_WINDOW_SIZE,
            num_neg_samples=TEST_NUM_NEG_SAMPLES,
            learning_rate=DEFAULT_LEARNING_RATE,
            epochs=TEST_EPOCHS,
        ),
    )
    return Node2Vec(config)


def test_node2vec_config_defaults() -> None:
    """Test Node2VecConfig default values."""
    config = Node2VecConfig()
    assert config.model.dimension == DEFAULT_DIMENSION
    assert config.training.walk_length == DEFAULT_WALK_LENGTH
    assert config.training.num_walks == DEFAULT_NUM_WALKS
    assert config.model.p == DEFAULT_P
    assert config.model.q == DEFAULT_Q
    assert config.training.window_size == DEFAULT_WINDOW_SIZE
    assert config.training.num_neg_samples == DEFAULT_NUM_NEG_SAMPLES
    assert config.training.learning_rate == DEFAULT_LEARNING_RATE
    assert config.training.epochs == DEFAULT_EPOCHS


def test_node2vec_config_custom() -> None:
    """Test Node2VecConfig with custom values."""
    config = Node2VecConfig(
        model=Node2VecModelConfig(
            dimension=CUSTOM_DIMENSION,
            p=CUSTOM_P,
            q=CUSTOM_Q,
        ),
        training=Node2VecTrainingConfig(
            walk_length=CUSTOM_WALK_LENGTH,
            num_walks=CUSTOM_NUM_WALKS,
            window_size=CUSTOM_WINDOW_SIZE,
            num_neg_samples=CUSTOM_NUM_NEG_SAMPLES,
            learning_rate=CUSTOM_LEARNING_RATE,
            epochs=CUSTOM_EPOCHS,
        ),
    )
    assert config.model.dimension == CUSTOM_DIMENSION
    assert config.training.walk_length == CUSTOM_WALK_LENGTH
    assert config.training.num_walks == CUSTOM_NUM_WALKS
    assert config.model.p == CUSTOM_P
    assert config.model.q == CUSTOM_Q
    assert config.training.window_size == CUSTOM_WINDOW_SIZE
    assert config.training.num_neg_samples == CUSTOM_NUM_NEG_SAMPLES
    assert config.training.learning_rate == CUSTOM_LEARNING_RATE
    assert config.training.epochs == CUSTOM_EPOCHS


def make_aiter(items: list) -> Callable[..., AsyncIterator]:
    """Create an async iterator factory for mocking Neo4j query results."""

    def _aiter(_self) -> AsyncIterator:
        return AsyncIterator(items)

    return _aiter


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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
    result = test_node2vec.alias_draw(alias, 0, test_node2vec.get_rng())
    assert isinstance(result, int)
    assert 0 <= result < len(alias["J"])


def test_node2vec_walk(
    test_node2vec: Node2Vec, test_sample_graph: dict[str, list[str]]
) -> None:
    """Test random walk generation."""
    # Initialize alias nodes first
    test_node2vec.preprocess_transition_probs(test_sample_graph)
    walk = test_node2vec.node2vec_walk("1", test_sample_graph)
    assert len(walk) <= test_node2vec.config.training.walk_length
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
    assert len(walks) == test_node2vec.config.training.num_walks * len(
        test_sample_graph
    )
    assert all(len(walk) <= test_node2vec.config.training.walk_length for walk in walks)
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
        assert embeddings[node].shape == (test_node2vec.config.model.dimension,)
        assert np.allclose(np.linalg.norm(embeddings[node]), 1.0)


def test_initialize_embeddings_empty(test_node2vec: Node2Vec) -> None:
    """Test embedding initialization with empty node set."""
    test_node2vec.initialize_embeddings(set())
    embeddings = test_node2vec.get_all_embeddings()
    assert len(embeddings) == 0


def test_get_context_nodes(test_node2vec: Node2Vec) -> None:
    """Test context node retrieval."""
    walk = ["1", "2", "3", "4", "5"]
    context = test_node2vec.get_context_nodes(walk, 2)
    assert len(context) == EXPECTED_CONTEXT_SIZE_MIDDLE
    assert context == ["2", "4"]


def test_get_context_nodes_boundary(test_node2vec: Node2Vec) -> None:
    """Test context node retrieval at walk boundaries."""
    walk = ["1", "2", "3"]
    context_start = test_node2vec.get_context_nodes(walk, 0)
    context_end = test_node2vec.get_context_nodes(walk, 2)
    assert len(context_start) == EXPECTED_CONTEXT_SIZE
    assert len(context_end) == EXPECTED_CONTEXT_SIZE
    assert context_start == ["2"]
    assert context_end == ["2"]


def test_process_positive_samples(test_node2vec: Node2Vec) -> None:
    """Test processing of positive samples."""
    node = "1"
    context_nodes = ["2", "3"]
    test_node2vec.initialize_embeddings({node, "2", "3"})
    test_node2vec.process_positive_samples(node, context_nodes)
    embeddings = test_node2vec.get_all_embeddings()
    assert node in embeddings
    assert "2" in embeddings
    assert "3" in embeddings


def test_process_negative_samples(test_node2vec: Node2Vec) -> None:
    """Test processing of negative samples."""
    node = "1"
    context_nodes = ["2", "3"]
    all_nodes = {"1", "2", "3", "4", "5"}
    test_node2vec.initialize_embeddings(all_nodes)
    test_node2vec.process_negative_samples(node, context_nodes, all_nodes)
    embeddings = test_node2vec.get_all_embeddings()
    assert node in embeddings
    assert all(n in embeddings for n in all_nodes)


def test_update_embedding(test_node2vec: Node2Vec) -> None:
    """Test embedding update."""
    node1 = "1"
    node2 = "2"
    test_node2vec.initialize_embeddings({node1, node2})
    initial_emb1 = test_node2vec.get_embedding(node1).copy()
    initial_emb2 = test_node2vec.get_embedding(node2).copy()
    test_node2vec.update_embedding(node1, node2, 1.0)
    updated_emb1 = test_node2vec.get_embedding(node1)
    updated_emb2 = test_node2vec.get_embedding(node2)
    assert not np.array_equal(initial_emb1, updated_emb1)
    assert not np.array_equal(initial_emb2, updated_emb2)


def test_get_embedding(test_node2vec: Node2Vec) -> None:
    """Test embedding retrieval."""
    node_id = "1"
    embedding = rng.random(test_node2vec.config.model.dimension)
    test_node2vec.set_embedding(node_id, embedding)
    retrieved = test_node2vec.get_embedding(node_id)
    assert np.array_equal(retrieved, embedding)


def test_get_all_embeddings(test_node2vec: Node2Vec) -> None:
    """Test retrieval of all embeddings."""
    embeddings = {
        "1": rng.random(test_node2vec.config.model.dimension),
        "2": rng.random(test_node2vec.config.model.dimension),
    }
    test_node2vec.set_all_embeddings(embeddings)
    retrieved = test_node2vec.get_all_embeddings()
    assert retrieved == embeddings


@pytest_asyncio.fixture
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
        assert embeddings[node_id].shape == (test_node2vec.config.model.dimension,)
        assert np.allclose(np.linalg.norm(embeddings[node_id]), 1.0)
