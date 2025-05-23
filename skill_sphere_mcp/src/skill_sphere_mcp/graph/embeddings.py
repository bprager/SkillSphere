"""Node2Vec embeddings and graph search functionality."""

import logging
from typing import Any, Optional

import networkx as nx  # type: ignore[import-untyped]
import numpy as np
from neo4j import AsyncSession
from node2vec import Node2Vec  # type: ignore[import-untyped]
from sklearn.metrics.pairwise import cosine_similarity

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

    async def load_embeddings(self, session: AsyncSession) -> None:
        """Load or compute embeddings for all nodes in the graph."""
        # Query to get all nodes and their relationships
        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN id(n) as node_id, labels(n) as labels, properties(n) as props,
               collect({target: id(m), type: type(r)}) as edges
        """
        result = await session.run(query)
        nodes = [record async for record in result]

        # Create graph for Node2Vec
        g = nx.Graph()
        for node in nodes:
            g.add_node(str(node["node_id"]))
            for edge in node["edges"]:
                if edge["target"] is not None:
                    g.add_edge(
                        str(node["node_id"]), str(edge["target"]), type=edge["type"]
                    )

        # Compute Node2Vec embeddings
        node2vec = Node2Vec(
            g, p=1, q=1, vector_size=self.dimension, walk_length=30, num_walks=200
        )
        model = node2vec.fit(session=4)

        # Store embeddings
        for node in nodes:
            node_id = str(node["node_id"])
            self._node_ids[node_id] = int(node["node_id"])
            self._embeddings[node_id] = model.wv[node_id]

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

    def get_embedding(self, node_id: str) -> Optional[np.ndarray]:
        """Get embedding for a specific node."""
        return self._embeddings.get(node_id)


# Global embeddings instance
embeddings = Node2VecEmbeddings()
