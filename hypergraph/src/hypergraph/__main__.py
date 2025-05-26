"""Main entry point for the hypergraph ingestion pipeline."""

import logging
from pathlib import Path

import yaml
from langchain_community.embeddings import OllamaEmbeddings

from hypergraph.core.config import Settings
from hypergraph.core.utils import chunk, sha256
from hypergraph.db.graph import GraphWriter
from hypergraph.db.registry import Registry
from hypergraph.embeddings.faiss import FaissManager
from hypergraph.llm.triples import TripleExtractor

# ───────────────────────────── Logging ────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("ingestion")


def main():
    """Process all markdown files in the doc root and compute Node2Vec embeddings."""
    # Load configuration
    settings = Settings()

    # Load schema
    schema = yaml.safe_load(
        Path(settings.graph_schema_yaml).read_text(encoding="utf-8")
    )
    rel_hints = [r["type"] for r in schema.get("relationships", [])]
    known_skills = schema.get("prompt_steering", {}).get("known_skills", [])
    known_tools = schema.get("prompt_steering", {}).get("known_tools", [])
    alias_map = schema.get("prompt_steering", {}).get("alias_map", {})

    # Initialize components
    reg = Registry(Path(settings.registry_path))
    gw = GraphWriter(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_pass)
    emb = OllamaEmbeddings(model="nomic-embed-text", base_url=settings.ollama_base_url)
    extractor = TripleExtractor(
        model="gemma3:12b",
        base_url=settings.ollama_base_url,
        rel_hints=rel_hints,
        known_skills=known_skills,
        known_tools=known_tools,
        alias_map=alias_map,
    )

    try:
        # Process each markdown file
        for md_file in Path(settings.doc_root).rglob("*.md"):
            # Skip if unchanged
            doc_sha = sha256(md_file)
            doc_id = md_file.stem
            if reg.get(doc_id) == doc_sha:
                log.info("SKIP %s (unchanged)", doc_id)
                continue

            # Process file
            text = md_file.read_text("utf-8")
            chunks = chunk(text, settings.chunk_size, settings.chunk_overlap)

            # Compute embeddings
            vectors = emb.embed_documents(chunks)
            FaissManager.add_vectors(vectors, settings.faiss_index_path)

            # Extract & write triples
            for ch in chunks:
                triples = extractor.extract(ch, settings.glean_max_rounds)
                gw.write(triples)

            # Update registry
            reg.upsert(doc_id, doc_sha)
            log.info("OK   %s", doc_id)

        # Compute Node2Vec embeddings
        gw.run_node2vec(
            dim=settings.node2vec_dim,
            walks=settings.node2vec_walks,
            walk_length=settings.node2vec_walk_length,
        )
    finally:
        gw.close()


if __name__ == "__main__":
    main()
