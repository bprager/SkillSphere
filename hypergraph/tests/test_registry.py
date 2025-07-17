"""Tests for the registry module."""

# pylint: disable=import-error, wrong-import-position
import sys

from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from hypergraph.db.registry import Registry


def test_registry_upsert_get(settings: Any) -> None:
    """Test registry upsert and get operations."""
    # Create registry
    reg = Registry(Path(settings.registry_path))

    # Test upsert
    reg.upsert("test_doc", "abc123")

    # Test get
    assert reg.get("test_doc") == "abc123"

    # Test update
    reg.upsert("test_doc", "def456")
    assert reg.get("test_doc") == "def456"

    # Test non-existent
    assert reg.get("non_existent") is None
