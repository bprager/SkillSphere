"""State management for Node2Vec."""

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class Node2VecState:
    """Node2Vec state attributes."""

    embeddings: Dict[str, np.ndarray]
    node_ids: Dict[str, int]
    alias_nodes: Dict[str, Dict[str, List[int]]]
    alias_edges: Dict[Tuple[str, str], Dict[str, List[int]]]
    walks: List[List[str]]
    graph: Dict[str, List[str]]
    preprocessed: bool = False

    def __post_init__(self):
        """Initialize default values."""
        self.embeddings = {}
        self.node_ids = {}
        self.alias_nodes = {}
        self.alias_edges = {}
        self.walks = []
        self.graph = {}
        self.preprocessed = False
