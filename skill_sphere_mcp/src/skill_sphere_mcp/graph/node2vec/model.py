"""Main Node2Vec implementation."""

import logging
from collections import defaultdict

import numpy as np
from neo4j import AsyncSession

from .config import Node2VecConfig, PreprocessConfig, TransitionConfig
from .sampling import alias_draw, alias_setup
from .state import Node2VecState
from .training import (
    NegativeSamplingConfig,
    SamplingConfig,
    get_context_nodes,
    process_negative_samples,
    process_positive_samples,
    update_embedding,
)
from .walks import WalkConfig, generate_walks, node2vec_walk

logger = logging.getLogger(__name__)


class Node2Vec:
    """Node2Vec implementation for graph embeddings."""

    def __init__(self, config: Node2VecConfig | None = None):
        """Initialize Node2Vec.

        Args:
            config: Node2Vec configuration parameters
        """
        self.config = config or Node2VecConfig()
        self._rng = np.random.default_rng(42)  # Fixed seed for reproducibility
        self._state = Node2VecState(
            embeddings={},
            node_ids={},
            alias_nodes={},
            alias_edges={},
            walks=[],
            graph={},
            preprocessed=False,
        )

    async def get_graph(self, session: AsyncSession) -> dict[str, list[str]]:
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

    def _preprocess_node_transition_probs(self) -> None:
        """Preprocess node transition probabilities."""
        for node in self._state.graph:
            unnormalized_probs = [
                self._get_edge_weight() for _ in sorted(self._state.graph[node])
            ]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [
                float(u_prob) / norm_const for u_prob in unnormalized_probs
            ]
            self._state.alias_nodes[node] = alias_setup(normalized_probs)

    def _preprocess_edge_transition_probs(self, config: TransitionConfig) -> None:
        """Preprocess edge transition probabilities."""
        for src in self._state.graph:
            for dst in self._state.graph[src]:
                unnormalized_probs = []
                for dst_nbr in sorted(self._state.graph[dst]):
                    if dst_nbr == src:
                        unnormalized_probs.append(self._get_edge_weight() / config.p)
                    elif dst_nbr in self._state.graph[src]:
                        unnormalized_probs.append(self._get_edge_weight())
                    else:
                        unnormalized_probs.append(self._get_edge_weight() / config.q)
                norm_const = sum(unnormalized_probs)
                normalized_probs = [
                    float(u_prob) / norm_const for u_prob in unnormalized_probs
                ]
                self._state.alias_edges[(src, dst)] = alias_setup(normalized_probs)

    def preprocess_transition_probs(
        self,
        graph: dict[str, list[str]],
        config: TransitionConfig | None = None,
    ) -> None:
        """Preprocess transition probabilities for random walks."""
        if config is None:
            config = TransitionConfig(
                p=self.config.model.p,
                q=self.config.model.q,
                weight_key="weight",
                directed=False,
                unweighted=True,
            )

        self._state.alias_nodes = {}
        self._state.alias_edges = {}
        self._state.graph = defaultdict(list)

        # Build graph
        for src, neighbors in graph.items():
            self._state.graph[src].extend(neighbors)
            if not config.directed:
                for dst in neighbors:
                    self._state.graph[dst].append(src)

        # Preprocess node and edge transition probabilities
        self._preprocess_node_transition_probs()
        self._preprocess_edge_transition_probs(config)

    def _get_edge_weight(self) -> float:
        """Get edge weight for unweighted graphs.

        Returns:
            Edge weight (1.0 for unweighted graphs)
        """
        return 1.0

    def _train_embeddings(self, walks: list[list[str]]) -> None:
        """Train embeddings using random walks.

        Args:
            walks: List of random walks
        """
        nodes = set(self._state.graph.keys())
        for _ in range(self.config.training.epochs):
            for walk in walks:
                for center_idx, node in enumerate(walk):
                    context_nodes = get_context_nodes(
                        walk, center_idx, self.config.training.window_size
                    )
                    process_positive_samples(
                        node,
                        context_nodes,
                        self._state.embeddings,
                        SamplingConfig(
                            learning_rate=self.config.training.learning_rate
                        ),
                    )
                    process_negative_samples(
                        node,
                        context_nodes,
                        nodes,
                        self._state.embeddings,
                        NegativeSamplingConfig(
                            num_samples=self.config.training.num_neg_samples,
                            learning_rate=self.config.training.learning_rate,
                            rng=self._rng,
                        ),
                    )

    async def fit(self, session: AsyncSession) -> None:
        """Fit Node2Vec model.

        Args:
            session: Neo4j session
        """
        # Get graph structure
        self._state.graph = await self.get_graph(session)

        # Preprocess transition probabilities
        self.preprocess_transition_probs(self._state.graph)

        # Initialize embeddings
        self.initialize_embeddings(set(self._state.graph.keys()))

        # Generate random walks
        walk_config = WalkConfig(
            graph=self._state.graph,
            alias_nodes=self._state.alias_nodes,
            alias_edges=self._state.alias_edges,
            walk_length=self.config.training.walk_length,
            rng=self._rng,
        )
        walks = generate_walks(walk_config, self.config.training.num_walks)

        # Train embeddings
        self._train_embeddings(walks)

        # Final normalization of all embeddings
        for node in self._state.embeddings:
            emb = self._state.embeddings[node]
            norm = np.linalg.norm(emb)
            if norm > 0:
                self._state.embeddings[node] = emb / norm

    def initialize_embeddings(self, nodes: set[str]) -> None:
        """Initialize embeddings for nodes.

        Args:
            nodes: Set of nodes
        """
        for node in nodes:
            embedding = self._rng.normal(0, 1, self.config.model.dimension)
            # Normalize to unit length
            embedding = embedding / np.linalg.norm(embedding)
            self._state.embeddings[node] = embedding

    def get_embedding(self, node_id: str) -> np.ndarray | None:
        """Get embedding for a node.

        Args:
            node_id: Node ID

        Returns:
            Node embedding or None if not found
        """
        return self._state.embeddings.get(node_id)

    def set_embedding(self, node_id: str, embedding: np.ndarray) -> None:
        """Set embedding for a node.

        Args:
            node_id: Node ID
            embedding: Node embedding
        """
        self._state.embeddings[node_id] = embedding

    def get_all_embeddings(self) -> dict[str, np.ndarray]:
        """Get all node embeddings.

        Returns:
            Dictionary mapping node IDs to embeddings
        """
        return self._state.embeddings.copy()

    def set_all_embeddings(self, embeddings: dict[str, np.ndarray]) -> None:
        """Set all node embeddings.

        Args:
            embeddings: Dictionary mapping node IDs to embeddings
        """
        self._state.embeddings = embeddings.copy()

    def get_context_nodes(self, walk: list[str], center_idx: int) -> list[str]:
        """Get context nodes for a center node in a walk."""
        window_size = self.config.training.window_size
        start = max(0, center_idx - window_size)
        end = min(len(walk), center_idx + window_size + 1)
        # Include all nodes in window except center
        return [walk[i] for i in range(start, end) if i != center_idx]

    def process_positive_samples(self, node: str, context_nodes: list[str]) -> None:
        """Process positive samples for training.

        Args:
            node: Center node
            context_nodes: Context nodes
        """
        process_positive_samples(
            node,
            context_nodes,
            self._state.embeddings,
            SamplingConfig(learning_rate=self.config.training.learning_rate),
        )
        # Normalize embeddings after update
        for n in [node] + context_nodes:
            if n in self._state.embeddings:
                emb = self._state.embeddings[n]
                norm = np.linalg.norm(emb)
                if norm > 0:
                    self._state.embeddings[n] = emb / norm

    def process_negative_samples(
        self, node: str, context_nodes: list[str], nodes: set[str]
    ) -> None:
        """Process negative samples for training.

        Args:
            node: Center node
            context_nodes: Context nodes
            nodes: Set of all nodes
        """
        process_negative_samples(
            node,
            context_nodes,
            nodes,
            self._state.embeddings,
            NegativeSamplingConfig(
                num_samples=self.config.training.num_neg_samples,
                learning_rate=self.config.training.learning_rate,
                rng=self._rng,
            ),
        )
        # Normalize embeddings after update
        for n in [node] + context_nodes:
            if n in self._state.embeddings:
                emb = self._state.embeddings[n]
                norm = np.linalg.norm(emb)
                if norm > 0:
                    self._state.embeddings[n] = emb / norm

    def update_embedding(self, node1: str, node2: str, label: float) -> None:
        """Update embeddings using gradient descent and normalize after update."""
        update_embedding(
            node1,
            node2,
            label,
            self._state.embeddings,
            self.config.training.learning_rate,
        )
        # Normalize both embeddings after update
        for node in [node1, node2]:
            if node in self._state.embeddings:
                emb = self._state.embeddings[node]
                norm = np.linalg.norm(emb)
                if norm > 0:
                    self._state.embeddings[node] = emb / norm

    def node2vec_walk(
        self, start_node: str, graph: dict[str, list[str]] | None = None
    ) -> list[str]:
        """Generate a random walk starting from a node.
        Optionally accept a graph for test compatibility."""
        if graph is not None:
            # Use provided graph for test compatibility
            walk_config = WalkConfig(
                graph=graph,
                alias_nodes=self._state.alias_nodes,
                alias_edges=self._state.alias_edges,
                walk_length=self.config.training.walk_length,
                rng=self._rng,
            )
            return node2vec_walk(start_node, walk_config)
        walk_config = WalkConfig(
            graph=self._state.graph,
            alias_nodes=self._state.alias_nodes,
            alias_edges=self._state.alias_edges,
            walk_length=self.config.training.walk_length,
            rng=self._rng,
        )
        return node2vec_walk(start_node, walk_config)

    def generate_walks(
        self, graph: dict[str, list[str]], num_walks: int | None = None
    ) -> list[list[str]]:
        """Generate random walks for all nodes.
        num_walks is optional for test compatibility."""
        if num_walks is None:
            num_walks = self.config.training.num_walks
        walk_config = WalkConfig(
            graph=graph,
            alias_nodes=self._state.alias_nodes,
            alias_edges=self._state.alias_edges,
            walk_length=self.config.training.walk_length,
            rng=self._rng,
        )
        return generate_walks(walk_config, num_walks)

    def get_alias_nodes(self) -> dict[str, dict[str, list[int]]]:
        """Return alias nodes table."""
        return self._state.alias_nodes

    def get_alias_edges(self) -> dict[tuple[str, str], dict[str, list[int]]]:
        """Return alias edges table."""
        return self._state.alias_edges

    def get_rng(self) -> np.random.Generator:
        """Return the random number generator."""
        return self._rng

    @staticmethod
    def alias_setup(probs: list[float]) -> dict[str, list[int]]:
        """Expose alias_setup as a static method."""
        return alias_setup(probs)

    @staticmethod
    def alias_draw(
        alias: dict[str, list[int]], idx: int, rng: np.random.Generator
    ) -> int:
        """Expose alias_draw as a static method."""
        return alias_draw(alias, idx, rng)

    async def preprocess(
        self,
        session: AsyncSession,
        config: PreprocessConfig | None = None,
    ) -> None:
        """Preprocess graph for Node2Vec."""
        if self._state.preprocessed:
            return

        # Get graph structure
        self._state.graph = await self.get_graph(session)

        # Convert PreprocessConfig to TransitionConfig if needed
        if config is not None:
            transition_config = TransitionConfig(
                p=config.p,
                q=config.q,
                weight_key=config.weight_key,
                directed=config.directed,
                unweighted=config.unweighted,
            )
        else:
            transition_config = None

        # Preprocess transition probabilities
        self.preprocess_transition_probs(self._state.graph, transition_config)

        self._state.preprocessed = True
