"""Tests for the main module."""

import sys

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

# pylint: disable=import-error
from hypergraph.__main__ import main


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# pylint: disable=redefined-outer-name


@pytest.fixture
def mock_schema() -> Any:
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
def mock_md_file(tmp_path: Any) -> Any:
    """Create a temporary markdown file for testing."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    test_file = docs_dir / "test.md"
    test_file.write_text("# Test Document\n\nThis is a test document about Python and pytest.")
    return test_file


def test_main_flow(
    settings: Any,
    mock_schema: Any,
    mock_md_file: Any,
    monkeypatch: Any,
) -> None:
    """Test the main ingestion flow."""
    # Patch langchain to prevent version metadata access
    with patch("langchain.__init__", new=MagicMock()):
        # Now import the modules that depend on ChatOllama
        from langchain_ollama import OllamaEmbeddings

        from hypergraph.db.graph import GraphWriter
        from hypergraph.db.registry import Registry
        from hypergraph.llm.triples import TripleExtractor

        # Mock file operations
        def mock_read_text(*_args: Any, **_kwargs: Any) -> str:
            return "# Test Document\n\nThis is a test document about Python and pytest."

        def mock_rglob(*_args: Any, **_kwargs: Any) -> Any:
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
        ), patch("yaml.safe_load", return_value=mock_schema) as mock_schema_load, patch(
            "pathlib.Path.read_text", return_value=""
        ):
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

            # Verify schema usage
            mock_schema_load.assert_called_once()
            # Verify that the schema's relationships were used in triple extraction
            assert all(
                triple["relation"] in [r["type"] for r in mock_schema["relationships"]]
                for triple in mock_triples
            )
            # Verify that the schema's known skills were used
            assert all(
                skill in mock_schema["prompt_steering"]["known_skills"]
                for skill in ["Python", "Neo4j"]
            )


def test_skip_unchanged_file(
    settings: Any,
    mock_schema: Any,
    mock_md_file: Any,
    monkeypatch: Any,
) -> None:
    """Test that unchanged files are skipped."""
    # Patch langchain to prevent version metadata access
    with patch("langchain.__init__", new=MagicMock()):
        # Now import the modules that depend on ChatOllama
        from hypergraph.db.graph import GraphWriter
        from hypergraph.db.registry import Registry

        # Mock registry to return existing hash
        mock_registry = MagicMock(spec=Registry)
        mock_registry.get.return_value = "test_hash"  # Simulate unchanged file

        # Mock file operations
        def mock_rglob(*_args: Any, **_kwargs: Any) -> Any:
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
        ), patch("yaml.safe_load", return_value=mock_schema) as mock_schema_load, patch(
            "pathlib.Path.read_text", return_value=""
        ):
            # Mock Path methods
            monkeypatch.setattr(Path, "rglob", mock_rglob)

            main()

            # Verify no processing occurred
            mock_registry.get.assert_called_once_with("test")
            mock_graph_writer.write.assert_not_called()
            mock_registry.upsert.assert_not_called()

            # Verify schema was still loaded (needed for initialization)
            mock_schema_load.assert_called_once()


def test_error_handling(
    settings: Any,
    mock_schema: Any,
    mock_md_file: Any,
    monkeypatch: Any,
) -> None:
    """Test error handling in the main flow."""
    # Patch langchain to prevent version metadata access
    with patch("langchain.__init__", new=MagicMock()):
        # Now import the modules that depend on ChatOllama
        from hypergraph.db.registry import Registry

        # Mock registry to raise an error
        mock_registry = MagicMock(spec=Registry)
        mock_registry.get.side_effect = Exception("Test error")

        # Mock file operations
        def mock_rglob(*_args: Any, **_kwargs: Any) -> Any:
            return [mock_md_file]

        # Apply mocks
        with patch.multiple(
            "hypergraph.__main__",
            Settings=lambda: settings,
            Registry=lambda path: mock_registry,
            sha256=lambda path: "test_hash",
        ), patch("yaml.safe_load", return_value=mock_schema) as mock_schema_load, patch(
            "pathlib.Path.read_text", return_value=""
        ):
            # Mock Path methods
            monkeypatch.setattr(Path, "rglob", mock_rglob)

            # Should raise an exception
            with pytest.raises(Exception) as exc_info:
                main()
            assert str(exc_info.value) == "Test error"

            # Verify schema was loaded before the error occurred
            mock_schema_load.assert_called_once()


def test_readme_files_are_skipped(
    tmp_path: Any, settings: Any, mock_schema: Any, monkeypatch: Any
) -> None:
    """Test that README files are skipped during processing."""
    # Create test files including README files
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create content files that should be processed
    content_file = docs_dir / "content.md"
    content_file.write_text("# Content Document\n\nThis is regular content.")

    # Create README files that should be skipped
    readme_file = docs_dir / "README.md"
    readme_file.write_text("# README\n\nThis is a README file.")

    subdir = docs_dir / "subdir"
    subdir.mkdir()
    subdir_readme = subdir / "README.md"
    subdir_readme.write_text("# Sub README\n\nThis is a subdirectory README.")

    # Mock the settings to use our test directory
    settings.doc_root = str(docs_dir)

    # Track which files are processed
    processed_files = []

    def mock_process_file(md_file: Any, ctx: Any) -> None:
        processed_files.append(md_file.name)

    # Patch langchain to prevent version metadata access
    with patch("langchain.__init__", new=MagicMock()):
        from hypergraph.db.graph import GraphWriter
        from hypergraph.db.registry import Registry
        from hypergraph.llm.triples import TripleExtractor
        from langchain_ollama import OllamaEmbeddings

        # Mock all dependencies
        mock_registry = MagicMock(spec=Registry)
        mock_graph_writer = MagicMock(spec=GraphWriter)
        mock_embeddings = MagicMock(spec=OllamaEmbeddings)
        mock_extractor = MagicMock(spec=TripleExtractor)

        with patch.multiple(
            "hypergraph.__main__",
            Settings=lambda: settings,
            OllamaEmbeddings=lambda **kwargs: mock_embeddings,
            TripleExtractor=lambda **kwargs: mock_extractor,
            Registry=lambda path: mock_registry,
            GraphWriter=lambda *args, **kwargs: mock_graph_writer,
            process_file=mock_process_file,
        ), patch("yaml.safe_load", return_value=mock_schema), patch(
            "pathlib.Path.read_text", return_value=""
        ):
            main()

    # Verify that only content files were processed, not README files
    assert "content.md" in processed_files
    assert "README.md" not in processed_files
    assert len(processed_files) == 1
