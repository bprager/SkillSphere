"""Main entry point for the hypergraph ingestion pipeline."""

import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import List

import yaml

from langchain_ollama import OllamaEmbeddings

from hypergraph.core.config import Settings
from hypergraph.core.utils import chunk
from hypergraph.core.utils import sha256
from hypergraph.db.graph import GraphWriter
from hypergraph.db.registry import Registry
from hypergraph.embeddings.faiss_manager import FaissManager
from hypergraph.llm.triples import TripleExtractor
from hypergraph.llm.triples import TripleExtractorConfig


# ───────────────────────────── Logging ────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("ingestion")


@dataclass
class SchemaConfig:
    """Configuration from schema.yaml."""

    rel_hints: List[str]
    known_skills: List[str]
    known_tools: List[str]
    alias_map: Dict[str, str]


@dataclass
class IngestionContext:
    """Holds all components and settings for the ingestion pipeline."""

    reg: Registry
    gw: GraphWriter
    emb: OllamaEmbeddings
    extractor: TripleExtractor
    settings: Settings


def load_schema(settings: Settings) -> SchemaConfig:
    """Load and parse schema.yaml."""
    schema = yaml.safe_load(Path(settings.graph_schema_yaml).read_text(encoding="utf-8"))
    return SchemaConfig(
        rel_hints=[r["type"] for r in schema.get("relationships", [])],
        known_skills=schema.get("prompt_steering", {}).get("known_skills", []),
        known_tools=schema.get("prompt_steering", {}).get("known_tools", []),
        alias_map=schema.get("prompt_steering", {}).get("alias_map", {}),
    )


def init_context(settings: Settings, schema: SchemaConfig) -> IngestionContext:
    """Initialize all required components and return as a context object."""
    reg = Registry(Path(settings.registry_path))
    gw = GraphWriter(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_pass)
    emb = OllamaEmbeddings(model="nomic-embed-text", base_url=settings.ollama_base_url)
    extractor_config = TripleExtractorConfig(
        rel_hints=schema.rel_hints,
        known_skills=schema.known_skills,
        known_tools=schema.known_tools,
        alias_map=schema.alias_map,
    )
    extractor = TripleExtractor(
        model="gemma3:12b",
        base_url=settings.ollama_base_url,
        config=extractor_config,
    )
    return IngestionContext(reg=reg, gw=gw, emb=emb, extractor=extractor, settings=settings)


def process_file(md_file: Path, ctx: IngestionContext):
    """Process a single markdown file."""
    doc_sha = sha256(md_file)
    doc_id = md_file.stem
    if ctx.reg.get(doc_id) == doc_sha:
        log.info("SKIP %s (unchanged)", doc_id)
        return

    text = md_file.read_text("utf-8")
    chunks = chunk(text, ctx.settings.chunk_size, ctx.settings.chunk_overlap)

    vectors = ctx.emb.embed_documents(chunks)
    FaissManager.add_vectors(vectors, ctx.settings.faiss_index_path)

    for ch in chunks:
        triples = ctx.extractor.extract(ch, ctx.settings.glean_max_rounds)
        ctx.gw.write(triples)

    ctx.reg.upsert(doc_id, doc_sha)
    log.info("OK   %s", doc_id)


def main():
    """Process all markdown files in the doc root and compute Node2Vec embeddings."""
    settings = Settings()
    schema = load_schema(settings)
    ctx = init_context(settings, schema)

    try:
        for md_file in Path(ctx.settings.doc_root).rglob("*.md"):
            process_file(md_file, ctx)

        ctx.gw.run_node2vec(
            dim=ctx.settings.node2vec_dim,
            walks=ctx.settings.node2vec_walks,
            walk_length=ctx.settings.node2vec_walk_length,
        )
    finally:
        ctx.gw.close()


if __name__ == "__main__":
    main()
