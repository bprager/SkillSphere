"""State management for Node2Vec."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node2VecState:
    """Node2Vec state attributes."""

    embeddings: dict[str, Any] = field(default_factory=dict)
    node_ids: dict[str, int] = field(default_factory=dict)
    alias_nodes: dict[str, dict[str, list[int]]] = field(default_factory=dict)
    alias_edges: dict[tuple[str, str], dict[str, list[int]]] = field(
        default_factory=dict
    )
    walks: list[list[str]] = field(default_factory=list)
    graph: dict[str, list[str]] = field(default_factory=dict)
    preprocessed: bool = False
