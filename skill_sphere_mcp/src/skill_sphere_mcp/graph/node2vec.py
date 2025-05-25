"""Node2Vec implementation for graph embeddings."""

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np
from neo4j import AsyncSession
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)


@dataclass
class Node2VecConfig:
    """Node2Vec configuration parameters."""

    dimension: int = 128
    walk_length: int = 80
    num_walks: int = 10
    p: float = 1.0
    q: float = 1.0
    window_size: int = 5
    num_neg_samples: int = 5
    learning_rate: float = 0.025
    epochs: int = 5


@dataclass
class TransitionConfig:
    """Configuration for transition probabilities."""

    p: float
    q: float
    weight_key: str
    directed: bool
    unweighted: bool


@dataclass
class PreprocessConfig:
    """Configuration for graph preprocessing."""

    p: float = 1.0
    q: float = 1.0
    weight_key: str = "weight"
    directed: bool = False
    unweighted: bool = False


# pylint: disable=too-many-instance-attributes
class Node2Vec:
    """Node2Vec implementation for graph embeddings."""

    def __init__(self, config: Node2VecConfig | None = None):
        """Initialize Node2Vec.

        Args:
            config: Node2Vec configuration parameters
        """
        self.config = config or Node2VecConfig()
        self.dimension = self.config.dimension
        self.walk_length = self.config.walk_length
        self.num_walks = self.config.num_walks
        self.p = self.config.p
        self.q = self.config.q
        self.window_size = self.config.window_size
        self.num_neg_samples = self.config.num_neg_samples
        self.learning_rate = self.config.learning_rate
        self.epochs = self.config.epochs
        self._rng = np.random.default_rng(42)  # Fixed seed for reproducibility

        self._embeddings: dict[str, np.ndarray] = {}
        self._node_ids: dict[str, int] = {}
        self._alias_nodes: dict[str, dict[str, list[int]]] = {}
        self._alias_edges: dict[tuple[str, str], dict[str, list[int]]] = {}
        self._walks: list[list[str]] = []
        self._model: Any = None
        self._graph: dict[str, list[str]] = {}
        self._preprocessed = False

    async def _get_graph(self, session: AsyncSession) -> dict[str, list[str]]:
        """Get graph structure from Neo4j.

        Args:
            session: Neo4j session

        Returns:
            Dictionary mapping node IDs to their neighbors
        """
        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN id(n) as node_id, collect(id(m)) as neighbors
        """
        result = await session.run(query)
        graph = {}
        async for record in result:
            node_id = str(record["node_id"])
            neighbors = [str(n) for n in record["neighbors"] if n is not None]
            graph[node_id] = neighbors
        return graph

    def _preprocess_transition_probs(
        self,
        config: TransitionConfig,
        nodes: list[str],
        edges: list[tuple[str, str, float]],
    ) -> None:
        """Preprocess transition probabilities for random walks."""
        self._alias_nodes = {}
        self._alias_edges = {}
        self._graph = defaultdict(list)

        # Build graph
        for src, dst, _ in edges:
            self._graph[src].append(dst)
            if not config.directed:
                self._graph[dst].append(src)

        # Preprocess node transition probabilities
        for node in nodes:
            unnormalized_probs = [
                self._get_edge_weight() for _ in sorted(self._graph[node])
            ]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [
                float(u_prob) / norm_const for u_prob in unnormalized_probs
            ]
            self._alias_nodes[node] = self._alias_setup(normalized_probs)

        # Preprocess edge transition probabilities
        for edge in edges:
            src, dst, _ = edge
            unnormalized_probs = []
            for dst_nbr in sorted(self._graph[dst]):
                if dst_nbr == src:
                    unnormalized_probs.append(self._get_edge_weight() / config.p)
                elif dst_nbr in self._graph[src]:
                    unnormalized_probs.append(self._get_edge_weight())
                else:
                    unnormalized_probs.append(self._get_edge_weight() / config.q)
            norm_const = sum(unnormalized_probs)
            normalized_probs = [
                float(u_prob) / norm_const for u_prob in unnormalized_probs
            ]
            self._alias_edges[edge[:2]] = self._alias_setup(normalized_probs)

    def _alias_setup(self, probs: list[float]) -> dict[str, list[int]]:
        """Set up alias sampling.

        Args:
            probs: List of probabilities

        Returns:
            Dictionary with alias sampling tables
        """
        k = len(probs)
        q = np.zeros(k)
        j = np.zeros(k, dtype=np.int32)

        smaller = []
        larger = []
        for kk, prob in enumerate(probs):
            q[kk] = k * prob
            if q[kk] < 1.0:
                smaller.append(kk)
            else:
                larger.append(kk)

        while len(smaller) > 0 and len(larger) > 0:
            small = smaller.pop()
            large = larger.pop()

            j[small] = large
            q[large] = q[large] + q[small] - 1.0
            if q[large] < 1.0:
                smaller.append(large)
            else:
                larger.append(large)

        return {"J": j.tolist(), "q": q.tolist()}

    def _alias_draw(self, alias: dict[str, list[int]], idx: int) -> int:
        """Draw sample from alias table."""
        j = alias["J"]
        q = alias["q"]

        if self._rng.random() < q[idx]:
            return idx
        return j[idx]

    def _node2vec_walk(self, start_node: str, graph: dict[str, list[str]]) -> list[str]:
        """Generate a random walk starting from a node.

        Args:
            start_node: Starting node ID
            graph: Dictionary mapping node IDs to their neighbors

        Returns:
            List of node IDs in the walk
        """
        walk = [start_node]
        while len(walk) < self.walk_length:
            cur = walk[-1]
            if len(graph[cur]) > 0:
                if len(walk) == 1:
                    walk.append(graph[cur][self._alias_draw(self._alias_nodes[cur], 0)])
                else:
                    prev = walk[-2]
                    next_node = graph[cur][
                        self._alias_draw(self._alias_edges[(prev, cur)], 0)
                    ]
                    walk.append(next_node)
            else:
                break
        return walk

    def _generate_walks(self, graph: dict[str, list[str]]) -> list[list[str]]:
        """Generate random walks for all nodes."""
        walks = []
        nodes = list(graph.keys())
        for _ in range(self.num_walks):
            self._rng.shuffle(nodes)
            for node in nodes:
                walks.append(self._node2vec_walk(node, graph))
        return walks

    def _initialize_embeddings(self, nodes: set[str]) -> None:
        """Initialize random embeddings for nodes."""
        for node in nodes:
            self._embeddings[node] = self._rng.standard_normal(self.dimension)
            self._embeddings[node] = normalize(self._embeddings[node].reshape(1, -1))[0]

    def _get_context_nodes(self, walk: list[str], center_idx: int) -> list[str]:
        """Get context nodes within window size."""
        start = max(0, center_idx - self.window_size)
        end = min(len(walk), center_idx + self.window_size + 1)
        return walk[start:end]

    def _process_positive_samples(self, node: str, context_nodes: list[str]) -> None:
        """Process positive samples for a node."""
        for context_node in context_nodes:
            if context_node != node:
                self._update_embedding(node, context_node, 1.0)

    def _process_negative_samples(
        self, node: str, context_nodes: list[str], nodes: set[str]
    ) -> None:
        """Process negative samples for a node."""
        for _ in range(self.num_neg_samples):
            neg_node = self._rng.choice(list(nodes))
            if neg_node not in context_nodes:
                self._update_embedding(node, neg_node, -1.0)

    def _train_embeddings(self, walks: list[list[str]]) -> None:
        """Train embeddings using skip-gram model."""
        # Initialize embeddings
        nodes = {node for walk in walks for node in walk}
        self._initialize_embeddings(nodes)

        # Train embeddings
        for _ in range(self.epochs):
            for walk in walks:
                for i, node in enumerate(walk):
                    context_nodes = self._get_context_nodes(walk, i)
                    self._process_positive_samples(node, context_nodes)
                    self._process_negative_samples(node, context_nodes, nodes)

    def _update_embedding(self, node1: str, node2: str, label: float) -> None:
        """Update embeddings using gradient descent.

        Args:
            node1: First node ID
            node2: Second node ID
            label: 1.0 for positive samples, -1.0 for negative
        """
        vec1 = self._embeddings[node1]
        vec2 = self._embeddings[node2]

        # Compute gradient
        score = np.dot(vec1, vec2)
        grad = label * (1.0 - 1.0 / (1.0 + np.exp(-score)))

        # Update embeddings
        self._embeddings[node1] += self.learning_rate * grad * vec2
        self._embeddings[node2] += self.learning_rate * grad * vec1

        # Normalize
        self._embeddings[node1] = normalize(self._embeddings[node1].reshape(1, -1))[0]
        self._embeddings[node2] = normalize(self._embeddings[node2].reshape(1, -1))[0]

    async def fit(self, session: AsyncSession) -> None:
        """Train Node2Vec embeddings.

        Args:
            session: Neo4j session
        """
        logger.info("Loading graph structure...")
        graph = await self._get_graph(session)

        logger.info("Preprocessing transition probabilities...")
        nodes = list(graph.keys())
        edges = [(src, dst, 1.0) for src, dsts in graph.items() for dst in dsts]
        self._preprocess_transition_probs(
            TransitionConfig(
                p=1.0, q=1.0, weight_key="weight", directed=False, unweighted=True
            ),
            nodes,
            edges,
        )

        logger.info("Generating random walks...")
        walks = self._generate_walks(graph)

        logger.info("Training embeddings...")
        self._train_embeddings(walks)

        logger.info("Node2Vec training complete")

    def get_embedding(self, node_id: str) -> np.ndarray | None:
        """Get embedding for a node.

        Args:
            node_id: Node ID

        Returns:
            Node embedding vector or None if not found
        """
        return self._embeddings.get(node_id)

    def get_all_embeddings(self) -> dict[str, np.ndarray]:
        """Get all node embeddings.

        Returns:
            Dictionary mapping node IDs to their embeddings
        """
        return self._embeddings.copy()

    async def get_graph(self, session: AsyncSession) -> dict[str, list[str]]:
        """Get the graph structure from Neo4j."""
        return await self._get_graph(session)

    def preprocess_transition_probs(self, graph: dict[str, list[str]]) -> None:
        """Preprocess transition probabilities for the graph.

        Args:
            graph: Dictionary mapping node IDs to their neighbors
        """
        nodes = list(graph.keys())
        edges = [(src, dst, 1.0) for src, dsts in graph.items() for dst in dsts]
        self._preprocess_transition_probs(
            TransitionConfig(
                p=1.0, q=1.0, weight_key="weight", directed=False, unweighted=True
            ),
            nodes,
            edges,
        )

    def get_alias_nodes(self) -> dict[str, dict[str, list[int]]]:
        """Get the alias nodes dictionary."""
        return self._alias_nodes.copy()

    def get_alias_edges(self) -> dict[tuple[str, str], dict[str, list[int]]]:
        """Get the alias edges dictionary."""
        return self._alias_edges.copy()

    def alias_setup(self, probs: list[float]) -> dict[str, list[int]]:
        """Set up alias sampling.

        Args:
            probs: List of probabilities

        Returns:
            Dictionary with alias sampling tables
        """
        return self._alias_setup(probs)

    def alias_draw(self, alias: dict[str, list[int]], idx: int) -> int:
        """Draw sample from alias table."""
        return self._alias_draw(alias, idx)

    def node2vec_walk(self, start_node: str, graph: dict[str, list[str]]) -> list[str]:
        """Generate a random walk starting from a node.

        Args:
            start_node: Starting node ID
            graph: Dictionary mapping node IDs to their neighbors

        Returns:
            List of node IDs in the walk
        """
        return self._node2vec_walk(start_node, graph)

    def initialize_embeddings(self, nodes: set[str]) -> None:
        """Initialize random embeddings for nodes."""
        self._initialize_embeddings(nodes)

    def get_context_nodes(self, walk: list[str], center_idx: int) -> list[str]:
        """Get context nodes within window size."""
        return self._get_context_nodes(walk, center_idx)

    def process_positive_samples(self, node: str, context_nodes: list[str]) -> None:
        """Process positive samples for a node."""
        self._process_positive_samples(node, context_nodes)

    def process_negative_samples(
        self, node: str, context_nodes: list[str], nodes: set[str]
    ) -> None:
        """Process negative samples for a node."""
        self._process_negative_samples(node, context_nodes, nodes)

    def update_embedding(self, node1: str, node2: str, label: float) -> None:
        """Update embeddings using gradient descent.

        Args:
            node1: First node ID
            node2: Second node ID
            label: 1.0 for positive samples, -1.0 for negative
        """
        self._update_embedding(node1, node2, label)

    def set_embedding(self, node_id: str, embedding: np.ndarray) -> None:
        """Set embedding for a node.

        Args:
            node_id: Node ID
            embedding: Embedding vector
        """
        self._embeddings[node_id] = embedding

    def set_all_embeddings(self, embeddings: dict[str, np.ndarray]) -> None:
        """Set all node embeddings.

        Args:
            embeddings: Dictionary mapping node IDs to their embeddings
        """
        self._embeddings = embeddings.copy()

    def generate_walks(self, graph: dict[str, list[str]]) -> list[list[str]]:
        """Generate random walks for all nodes."""
        return self._generate_walks(graph)

    async def preprocess(
        self,
        session: AsyncSession,
        config: PreprocessConfig | None = None,
    ) -> None:
        """Preprocess the graph for random walks."""
        if self._preprocessed:
            return

        self._graph = await self._get_graph(session)
        nodes = list(self._graph.keys())
        edges = [(src, dst, 1.0) for src, dsts in self._graph.items() for dst in dsts]

        if config is None:
            config = PreprocessConfig()
        transition_config = TransitionConfig(
            p=config.p,
            q=config.q,
            weight_key=config.weight_key,
            directed=config.directed,
            unweighted=config.unweighted,
        )
        self._preprocess_transition_probs(transition_config, nodes, edges)
        self._preprocessed = True

    def _get_edge_weight(self) -> float:
        """Get edge weight between two nodes."""
        return 1.0  # Default weight since we don't store edge properties
