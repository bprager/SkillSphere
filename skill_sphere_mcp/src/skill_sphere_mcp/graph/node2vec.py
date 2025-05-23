"""Node2Vec implementation for graph embeddings."""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from neo4j import AsyncSession
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)


class Node2Vec:
    """Node2Vec implementation for graph embeddings."""

    def __init__(
        self,
        dimension: int = 128,
        walk_length: int = 80,
        num_walks: int = 10,
        p: float = 1.0,
        q: float = 1.0,
        window_size: int = 5,
        num_neg_samples: int = 5,
        learning_rate: float = 0.025,
        epochs: int = 5,
    ):
        """Initialize Node2Vec.

        Args:
            dimension: Embedding dimension
            walk_length: Length of random walks
            num_walks: Number of walks per node
            p: Return parameter
            q: In-out parameter
            window_size: Context window size
            num_neg_samples: Number of negative samples
            learning_rate: Learning rate
            epochs: Number of training epochs
        """
        self.dimension = dimension
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.p = p
        self.q = q
        self.window_size = window_size
        self.num_neg_samples = num_neg_samples
        self.learning_rate = learning_rate
        self.epochs = epochs

        self._embeddings: Dict[str, np.ndarray] = {}
        self._node_ids: Dict[str, int] = {}
        self._alias_nodes: Dict[str, Dict[str, List[int]]] = {}
        self._alias_edges: Dict[Tuple[str, str], Dict[str, List[int]]] = {}

    async def _get_graph(self, session: AsyncSession) -> Dict[str, List[str]]:
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

    def _preprocess_transition_probs(self, graph: Dict[str, List[str]]) -> None:
        """Preprocess transition probabilities for random walks.

        Args:
            graph: Dictionary mapping node IDs to their neighbors
        """
        # Preprocess node transition probabilities
        for node in graph:
            unnormalized_probs = [1.0] * len(graph[node])
            norm_const = sum(unnormalized_probs)
            normalized_probs = [
                float(u_prob) / norm_const for u_prob in unnormalized_probs
            ]
            self._alias_nodes[node] = self._alias_setup(normalized_probs)

        # Preprocess edge transition probabilities
        for node in graph:
            for neighbor in graph[node]:
                unnormalized_probs = []
                for next_node in graph[neighbor]:
                    if next_node == node:
                        unnormalized_probs.append(1.0 / self.p)
                    elif next_node in graph[node]:
                        unnormalized_probs.append(1.0)
                    else:
                        unnormalized_probs.append(1.0 / self.q)
                norm_const = sum(unnormalized_probs)
                normalized_probs = [
                    float(u_prob) / norm_const for u_prob in unnormalized_probs
                ]
                self._alias_edges[(node, neighbor)] = self._alias_setup(
                    normalized_probs
                )

    def _alias_setup(self, probs: List[float]) -> Dict[str, List[int]]:
        """Set up alias sampling.

        Args:
            probs: List of probabilities

        Returns:
            Dictionary with alias sampling tables
        """
        K = len(probs)
        q = np.zeros(K)
        J = np.zeros(K, dtype=np.int32)

        smaller = []
        larger = []
        for kk, prob in enumerate(probs):
            q[kk] = K * prob
            if q[kk] < 1.0:
                smaller.append(kk)
            else:
                larger.append(kk)

        while len(smaller) > 0 and len(larger) > 0:
            small = smaller.pop()
            large = larger.pop()

            J[small] = large
            q[large] = q[large] + q[small] - 1.0
            if q[large] < 1.0:
                smaller.append(large)
            else:
                larger.append(large)

        return {"J": J.tolist(), "q": q.tolist()}

    def _alias_draw(self, alias: Dict[str, List[int]], idx: int) -> int:
        """Draw sample from alias table.

        Args:
            alias: Alias sampling tables
            idx: Index to sample from

        Returns:
            Sampled index
        """
        J = alias["J"]
        q = alias["q"]

        if np.random.random() < q[idx]:
            return idx
        else:
            return J[idx]

    def _node2vec_walk(self, start_node: str, graph: Dict[str, List[str]]) -> List[str]:
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

    def _generate_walks(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Generate random walks for all nodes.

        Args:
            graph: Dictionary mapping node IDs to their neighbors

        Returns:
            List of random walks
        """
        walks = []
        nodes = list(graph.keys())
        for _ in range(self.num_walks):
            np.random.shuffle(nodes)
            for node in nodes:
                walks.append(self._node2vec_walk(node, graph))
        return walks

    def _train_embeddings(self, walks: List[List[str]]) -> None:
        """Train embeddings using skip-gram model.

        Args:
            walks: List of random walks
        """
        # Initialize embeddings
        nodes = set()
        for walk in walks:
            nodes.update(walk)
        for node in nodes:
            self._embeddings[node] = np.random.randn(self.dimension)
            self._embeddings[node] = normalize(self._embeddings[node].reshape(1, -1))[0]

        # Train embeddings
        for _ in range(self.epochs):
            for walk in walks:
                for i, node in enumerate(walk):
                    # Positive samples
                    for j in range(
                        max(0, i - self.window_size),
                        min(len(walk), i + self.window_size + 1),
                    ):
                        if i != j:
                            self._update_embedding(node, walk[j], 1.0)

                    # Negative samples
                    for _ in range(self.num_neg_samples):
                        neg_node = np.random.choice(list(nodes))
                        if (
                            neg_node
                            not in walk[
                                max(0, i - self.window_size) : min(
                                    len(walk), i + self.window_size + 1
                                )
                            ]
                        ):
                            self._update_embedding(node, neg_node, -1.0)

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
        self._preprocess_transition_probs(graph)

        logger.info("Generating random walks...")
        walks = self._generate_walks(graph)

        logger.info("Training embeddings...")
        self._train_embeddings(walks)

        logger.info("Node2Vec training complete")

    def get_embedding(self, node_id: str) -> Optional[np.ndarray]:
        """Get embedding for a node.

        Args:
            node_id: Node ID

        Returns:
            Node embedding vector or None if not found
        """
        return self._embeddings.get(node_id)

    def get_all_embeddings(self) -> Dict[str, np.ndarray]:
        """Get all node embeddings.

        Returns:
            Dictionary mapping node IDs to their embeddings
        """
        return self._embeddings.copy()
