# mypy: disable-error-code="union-attr"
"""Node2Vec embeddings and graph search functionality."""

import logging

from typing import Any

import numpy as np

from neo4j import AsyncSession
from sklearn.metrics.pairwise import cosine_similarity

from .node2vec.model import Node2Vec


logger = logging.getLogger(__name__)


class Node2VecEmbeddings:
    """Manages Node2Vec embeddings for graph nodes."""

    def __init__(self, dimension: int = 128):
        """Initialize Node2Vec embeddings.

        Args:
            dimension: Embedding dimension size
        """
        self.dimension = dimension
        self._embeddings: dict[str, np.ndarray] = {}
        self._node_ids: dict[str, int] = {}
        self.model: Any | None = None  # type: ignore[python-version, unused-ignore, syntax]

    async def load_embeddings(self, session: AsyncSession) -> None:
        """Load embeddings from graph."""
        # Get all nodes from graph
        result = await session.run("MATCH (n) RETURN n")
        nodes = [record async for record in result]

        # If no nodes found, return early
        if not nodes:
            self.model = None
            return

        # Create Node2Vec instance
        node2vec = Node2Vec()

        # Train model
        await node2vec.fit(session)
        self.model = node2vec

        # Store embeddings
        self._embeddings = {
            str(node["node_id"]): embedding
            for node in nodes
            if (embedding := node2vec.get_embedding(str(node["node_id"]))) is not None
        }
        self._node_ids = {str(node["node_id"]): int(node["node_id"]) for node in nodes}

        logger.info("Computed Node2Vec embeddings for %d nodes", len(nodes))

    async def search(
        self, session: AsyncSession, query_embedding: np.ndarray, top_k: int = 10
    ) -> list[dict[str, Any]]:
        """Search for similar nodes using cosine similarity.

        Args:
            session: Neo4j session
            query_embedding: Query vector
            top_k: Number of results to return

        Returns:
            List of similar nodes with scores
        """
        if not self._embeddings:
            await self.load_embeddings(session)

        # Compute similarities
        similarities = {}
        for node_id, embedding in self._embeddings.items():
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1), embedding.reshape(1, -1)
            )[0][0]
            similarities[node_id] = similarity

        # Get top-k results
        top_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        # Fetch node details
        results = []
        for node_id, score in top_results:
            query = """
            MATCH (n) WHERE id(n) = $node_id
            RETURN n, labels(n) as labels, properties(n) as props
            """
            result = await session.run(query, node_id=int(node_id))
            record = await result.single()
            if record:
                results.append(
                    {
                        "node_id": node_id,
                        "score": float(score),
                        "labels": record["labels"],
                        "properties": record["props"],
                    }
                )

        return results

    # type: ignore[python-version, unused-ignore, syntax, union-attr]
    def get_embedding(self, node_id: str) -> np.ndarray | None:
        """Get embedding for a specific node."""
        return self._embeddings.get(node_id)

    def set_all_embeddings(self, new_embeddings: dict[str, np.ndarray]) -> None:
        """Set all node embeddings.

        Args:
            new_embeddings: Dictionary mapping node IDs to their embeddings
        """
        self._embeddings = new_embeddings.copy()

    def get_all_embeddings(self) -> dict[str, np.ndarray]:
        """Get all node embeddings.

        Returns:
            Dictionary mapping node IDs to their embeddings
        """
        return self._embeddings.copy()


# Global embeddings instance
embeddings = Node2VecEmbeddings()
