"""Tests for the GraphWriter class."""

# pylint: disable=import-error, redefined-outer-name, unused-argument, protected-access, wrong-import-position
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from unittest.mock import MagicMock, patch

import pytest_asyncio

from hypergraph.db.graph import GraphWriter


@pytest_asyncio.fixture
def mock_driver() -> Any:
    """Mock the Neo4j driver."""
    with patch("hypergraph.db.graph.GraphDatabase.driver") as mock:
        yield mock


@pytest_asyncio.fixture
def graph_writer(mock_driver: Any) -> Any:
    """Create a GraphWriter instance with mocked driver."""
    return GraphWriter("bolt://localhost:7687", "neo4j", "password")


def test_graph_writer_init(mock_driver: Any) -> None:
    """Test GraphWriter initialization."""
    writer = GraphWriter("bolt://localhost:7687", "neo4j", "password")
    mock_driver.assert_called_once_with("bolt://localhost:7687", auth=("neo4j", "password"))
    assert writer._drv == mock_driver.return_value


def test_merge_triple(graph_writer: Any) -> None:
    """Test merging a triple into the graph."""
    mock_tx = MagicMock()
    graph_writer._merge(mock_tx, "Python", "USES", "pytest")
    mock_tx.run.assert_called_once()
    call_args = mock_tx.run.call_args[0][0]
    assert "MERGE (a:Entity {name:$s})" in call_args
    assert "MERGE (b:Entity {name:$o})" in call_args
    assert "MERGE (a)-[:`USES`]->(b)" in call_args


def test_write_triples(graph_writer: Any) -> None:
    """Test writing multiple triples to the graph."""
    mock_session = MagicMock()
    graph_writer._drv.session.return_value.__enter__.return_value = mock_session

    triples = [
        {"subject": "Python", "relation": "USES", "object": "pytest"},
        {"subject": "Python", "relation": "KNOWS", "object": "black"},
    ]
    graph_writer.write(triples)

    expected_write_calls = 2
    assert mock_session.execute_write.call_count == expected_write_calls


def test_write_invalid_triple(graph_writer: Any) -> None:
    """Test writing an invalid triple (missing required fields)."""
    mock_session = MagicMock()
    graph_writer._drv.session.return_value.__enter__.return_value = mock_session

    triples = [
        {"subject": "Python", "relation": "USES"},  # Missing 'object'
        {"subject": "Python", "object": "black"},  # Missing 'relation'
    ]
    graph_writer.write(triples)

    assert mock_session.execute_write.call_count == 0


def test_run_node2vec(graph_writer: Any) -> None:
    """Test running Node2Vec embedding computation."""
    mock_session = MagicMock()
    graph_writer._drv.session.return_value.__enter__.return_value = mock_session

    graph_writer.run_node2vec(dim=128, walks=10, walk_length=80)

    # Verify the three Neo4j operations were called
    expected_run_calls = 3
    assert mock_session.run.call_count == expected_run_calls

    # Check graph projection
    project_call = mock_session.run.call_args_list[0][0][0]
    assert "CALL gds.graph.project" in project_call

    # Check Node2Vec computation
    node2vec_call = mock_session.run.call_args_list[1][0][0]
    assert "CALL gds.node2vec.write" in node2vec_call
    assert "embeddingDimension: $dim" in node2vec_call
    assert "walkLength:$walk_length" in node2vec_call.replace(" ", "")
    assert "walksPerNode:$walks" in node2vec_call.replace(" ", "")

    # Check graph cleanup
    drop_call = mock_session.run.call_args_list[2][0][0]
    assert "CALL gds.graph.drop" in drop_call


def test_close(graph_writer: Any) -> None:
    """Test closing the Neo4j connection."""
    graph_writer.close()
    graph_writer._drv.close.assert_called_once()
