"""Tests for the main module."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_ollama import OllamaEmbeddings

# pylint: disable=import-error
from hypergraph.__main__ import main
from hypergraph.db.graph import GraphWriter
from hypergraph.db.registry import Registry
from hypergraph.llm.triples import TripleExtractor

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# pylint: disable=redefined-outer-name


@pytest.fixture
def mock_schema():
    """Create mock schema."""
    return {
        "relationships": [
            {"type": "USES"},
            {"type": "KNOWS"},
        ],
        "prompt_steering": {
            "known_skills": ["Python", "Neo4j"],
            "known_tools": ["pytest", "black"],
            "alias_map": {"py": "Python"},
        },
    }


@pytest.fixture
def mock_md_file(tmp_path):
    """Create a temporary markdown file for testing."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    test_file = docs_dir / "test.md"
    test_file.write_text("# Test Document\n\nThis is a test document about Python and pytest.")
    return test_file


def test_main_flow(
    settings,
    mock_schema,
    mock_md_file,
    monkeypatch,
):
    """Test the main ingestion flow."""

    # Mock file operations
    def mock_read_text(*_args, **_kwargs):
        return "# Test Document\n\nThis is a test document about Python and pytest."

    def mock_rglob(*_args, **_kwargs):
        return [mock_md_file]

    # Mock embeddings
    mock_vectors = [[0.1, 0.2, 0.3] for _ in range(2)]  # 2 chunks
    mock_embeddings = MagicMock(spec=OllamaEmbeddings)
    mock_embeddings.embed_documents.return_value = mock_vectors

    # Mock triple extraction
    mock_triples = [
        {"subject": "Python", "relation": "USES", "object": "pytest"},
        {"subject": "Developer", "relation": "KNOWS", "object": "Python"},
    ]
    mock_extractor = MagicMock(spec=TripleExtractor)
    mock_extractor.extract.return_value = mock_triples

    # Mock registry
    mock_registry = MagicMock(spec=Registry)
    mock_registry.get.return_value = None  # Simulate new file

    # Mock graph writer
    mock_graph_writer = MagicMock(spec=GraphWriter)

    # Apply all mocks
    with patch.multiple(
        "hypergraph.__main__",
        Settings=lambda: settings,
        OllamaEmbeddings=lambda **kwargs: mock_embeddings,
        TripleExtractor=lambda **kwargs: mock_extractor,
        Registry=lambda path: mock_registry,
        GraphWriter=lambda *args, **kwargs: mock_graph_writer,
        sha256=lambda path: "test_hash",
    ), patch("yaml.safe_load", return_value=mock_schema):
        # Mock Path methods
        monkeypatch.setattr(Path, "rglob", mock_rglob)
        monkeypatch.setattr(Path, "read_text", mock_read_text)

        main()

        # Verify calls
        mock_registry.get.assert_called_once_with("test")
        mock_embeddings.embed_documents.assert_called_once()
        assert mock_extractor.extract.call_count >= 1  # At least one call for chunk(s)
        mock_graph_writer.write.assert_called_once()
        mock_registry.upsert.assert_called_once_with("test", "test_hash")


def test_skip_unchanged_file(
    settings,
    mock_schema,
    mock_md_file,
    monkeypatch,
):
    """Test that unchanged files are skipped."""
    # Mock registry to return existing hash
    mock_registry = MagicMock(spec=Registry)
    mock_registry.get.return_value = "test_hash"  # Simulate unchanged file

    # Mock file operations
    def mock_rglob(*_args, **_kwargs):
        return [mock_md_file]

    # Mock graph writer
    mock_graph_writer = MagicMock(spec=GraphWriter)

    # Apply mocks
    with patch.multiple(
        "hypergraph.__main__",
        Settings=lambda: settings,
        Registry=lambda path: mock_registry,
        GraphWriter=lambda *args, **kwargs: mock_graph_writer,
        sha256=lambda path: "test_hash",
    ), patch("yaml.safe_load", return_value=mock_schema):
        # Mock Path methods
        monkeypatch.setattr(Path, "rglob", mock_rglob)

        main()

        # Verify no processing occurred
        mock_registry.get.assert_called_once_with("test")
        mock_graph_writer.write.assert_not_called()
        mock_registry.upsert.assert_not_called()


def test_error_handling(
    settings,
    mock_schema,
    mock_md_file,
    monkeypatch,
):
    """Test error handling in the main flow."""
    # Mock registry to raise an error
    mock_registry = MagicMock(spec=Registry)
    mock_registry.get.side_effect = Exception("Test error")

    # Mock file operations
    def mock_rglob(*_args, **_kwargs):
        return [mock_md_file]

    # Apply mocks
    with patch.multiple(
        "hypergraph.__main__",
        Settings=lambda: settings,
        Registry=lambda path: mock_registry,
        sha256=lambda path: "test_hash",
    ), patch("yaml.safe_load", return_value=mock_schema):
        # Mock Path methods
        monkeypatch.setattr(Path, "rglob", mock_rglob)

        # Should raise an exception
        with pytest.raises(Exception) as exc_info:
            main()
        assert str(exc_info.value) == "Test error"
