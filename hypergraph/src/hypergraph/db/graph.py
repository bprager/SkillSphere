"""Neo4j graph writer and Node2Vec embedding computation."""

from neo4j import GraphDatabase


class GraphWriter:
    """Handles writing triples to Neo4j and computing Node2Vec embeddings."""

    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection."""
        self._drv = GraphDatabase.driver(uri, auth=(user, password))

    @staticmethod
    def _merge(tx, s: str, r: str, o: str):
        """Merge a subject-relation-object triple into the graph."""
        tx.run(
            "MERGE (a:Entity {name:$s})\n"
            "MERGE (b:Entity {name:$o})\n"
            "MERGE (a)-[:`" + r + "`]->(b)",
            s=s,
            o=o,
        )

    def write(self, triples: list[dict]):
        """Write a list of subject-relation-object triples to Neo4j."""
        with self._drv.session() as ses:
            for t in triples:
                if {"subject", "relation", "object"}.issubset(t):
                    ses.execute_write(
                        self._merge, t["subject"], t["relation"], t["object"]
                    )

    def run_node2vec(self, dim: int, walks: int, walk_length: int) -> None:
        """Project the graph into GDS and compute Node2Vec embeddings."""
        gname = "skill_graph_tmp"

        with self._drv.session() as ses:
            # 1️⃣  Project nodes and relationships
            ses.run(f"CALL gds.graph.project('{gname}', '*', '*')")

            # 2️⃣  Write Node2Vec embeddings to a node property
            ses.run(
                f"""
          CALL gds.node2vec.write('{gname}', {{
            embeddingDimension: {dim},
            walkLength:        {walk_length},
            iterations:        1,
            walksPerNode:      {walks},
            writeProperty:     'embedding'
            }})
        """
            )

            # 3️⃣  Drop the temporary in-memory graph
            ses.run(f"CALL gds.graph.drop('{gname}')")

    def close(self):
        """Close the Neo4j database connection."""
        self._drv.close()
