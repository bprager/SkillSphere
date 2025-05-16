"""ingestion_worker.py — v2.0
================================
Pipeline to ingest Bernd’s Markdown records into a **Hypergraph‑of‑Thought**
(Neo4j) **with two major upgrades**:

1. **Gleaning Loop** – repeatedly asks the LLM for *additional* triples until no
   new information is returned (or max 3 rounds).
2. **Node2Vec Graph Embedding** – runs Neo4j GDS Node2Vec on the final graph and
   stores 128‑dim vector embeddings on every node (`.embedding`).  Optionally
   adds them to FAISS for similarity queries.

The rest of the design (SHA‑registry, `.env` config, Ollama models) is unchanged.
Every step is annotated for clarity.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar, Iterable, List, Optional, Set, Tuple

import numpy as np  # type: ignore
import yaml
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from neo4j import GraphDatabase
from pydantic_settings import BaseSettings, SettingsConfigDict

# ────────────────────────── Optional FAISS ─────────────────────────
try:
    import faiss  # type: ignore
except ModuleNotFoundError:
    faiss = None  # type: ignore

# ───────────────────────────── Logging ────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("ingestion")

# ───────────────────────── Configuration Model ────────────────────
class Settings(BaseSettings):
    # External services
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_pass: str = "password"
    ollama_base_url: str = "http://127.0.0.1:11434"

    # Paths
    graph_schema_yaml: str = "./graph_schema.yaml"
    doc_root: str = "./docs"
    registry_path: str = "./doc_registry.sqlite3"
    faiss_index_path: str = "./faiss.index"

    # Ingestion
    chunk_size: int = 1500
    chunk_overlap: int = 200
    glean_max_rounds: int = 3  # max LLM passes per chunk

    # Node2Vec
    node2vec_dim: int = 128
    node2vec_walks: int = 10
    node2vec_walk_length: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

SET = Settings()

# ─────────────────────────── Schema Hints ─────────────────────────
SCHEMA = yaml.safe_load(Path(SET.graph_schema_yaml).read_text())
REL_HINTS: list[str] = [r["type"] for r in SCHEMA.get("relationships", [])]
KNOWN_SKILLS = SCHEMA.get("prompt_steering", {}).get("known_skills", [])
KNOWN_TOOLS = SCHEMA.get("prompt_steering", {}).get("known_tools", [])
ALIAS_MAP = SCHEMA.get("prompt_steering", {}).get("alias_map", {})

# ───────────────────────── Registry (SQLite) ──────────────────────
CREATE_SQL = """
CREATE TABLE IF NOT EXISTS doc_registry (
  doc_id TEXT PRIMARY KEY,
  hash   TEXT NOT NULL,
  last_ingested DATETIME NOT NULL
);
"""

class Registry:
    """Tracks SHA‑256 of every document to allow incremental updates."""

    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute(CREATE_SQL)

    def get(self, doc_id: str) -> Optional[str]:
        row = self.conn.execute("SELECT hash FROM doc_registry WHERE doc_id=?", (doc_id,)).fetchone()
        return row[0] if row else None

    def upsert(self, doc_id: str, sha: str):
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO doc_registry (doc_id, hash, last_ingested) VALUES (?,?,?) "
            "ON CONFLICT(doc_id) DO UPDATE SET hash=excluded.hash, last_ingested=excluded.last_ingested",
            (doc_id, sha, ts),
        )
        self.conn.commit()

# ───────────────────────── Utility Functions ─────────────────────

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chunk(text: str, size: int, overlap: int) -> List[str]:
    words = text.split()
    step = size - overlap
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step)]

# ───────────────────── Embedding (Ollama / FAISS) ─────────────────
class OllamaEmbeddingsCompat(OllamaEmbeddings):
    """Use legacy `/api/embed` endpoint (Ollama ≤0.6)."""
    embeddings_endpoint: ClassVar[str] = "/api/embed"

EMB = OllamaEmbeddingsCompat(model="nomic-embed-text", base_url=SET.ollama_base_url)

_FAISS_INDEX = None  # lazy‑initialised global

def add_to_faiss(vectors: List[List[float]]):
    if not faiss:
        return
    global _FAISS_INDEX
    dim = len(vectors[0])
    if _FAISS_INDEX is None:
        idx_path = Path(SET.faiss_index_path)
        _FAISS_INDEX = faiss.read_index(str(idx_path)) if idx_path.exists() else faiss.IndexFlatIP(dim)
    _FAISS_INDEX.add(np.array(vectors, dtype="float32"))  # type: ignore[arg-type]
    faiss.write_index(_FAISS_INDEX, str(SET.faiss_index_path))

# ───────────────────────── LLM Helpers ───────────────────────────
LLM = ChatOllama(model="gemma3:12b", base_url=SET.ollama_base_url)

PROMPT_TEMPLATE = (
    "You are an information‑extraction assistant. Output **ONLY** valid JSON — a list of triples "
    "with keys 'subject', 'relation', 'object'.\n"
    "Use relation names from: {rels}. Prefer skill names from: {skills}. Prefer tool names from: {tools}.\n"
    "Alias map (apply before output): {aliases}.\n"
    "Already extracted triples (avoid duplicates):\n{known}\n"
    "Text to analyse:```\n{chunk}```"
)


def _clean_json(raw: str) -> str:
    """Remove markdown fences & leading prose; return substring starting at first '[' or '{'."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```", 2)
        if len(parts) >= 2:
            raw = parts[1]
    for i, ch in enumerate(raw):
        if ch in "[{":
            return raw[i:]
    return raw


def parse_triples(text: str) -> List[dict]:
    """Try JSON then YAML."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            return yaml.safe_load(text) or []
        except Exception:
            return []


def glean_triples(chunk: str) -> List[dict]:
    """Multi‑turn gleaning loop until no new triples or max rounds reached."""
    collected: List[dict] = []
    for round_i in range(1, SET.glean_max_rounds + 1):
        prompt = PROMPT_TEMPLATE.format(
            rels=", ".join(REL_HINTS),
            skills=", ".join(KNOWN_SKILLS),
            tools=", ".join(KNOWN_TOOLS),
            aliases=json.dumps(ALIAS_MAP),
            known=json.dumps(collected),
            chunk=chunk,
        )
        resp = LLM.invoke(prompt)
        triples = parse_triples(_clean_json(resp.content))
        # Filter out ones we already have
        new = [t for t in triples if t not in collected]
        if not new:
            break
        collected.extend(new)
    return collected

# ───────────────────── Neo4j Writer & Node2Vec ───────────────────
class GraphWriter:
    def __init__(self):
        self._drv = GraphDatabase.driver(SET.neo4j_uri, auth=(SET.neo4j_user, SET.neo4j_pass))

    # ---------- ingestion ---------
    @staticmethod
    def _merge(tx, s: str, r: str, o: str):
        tx.run(
            "MERGE (a:Entity {name:$s})\n"
            "MERGE (b:Entity {name:$o})\n"
            "MERGE (a)-[:`" + r + "`]->(b)",
            s=s,
            o=o,
        )

    def write(self, triples: List[dict]):
        with self._drv.session() as ses:
            for t in triples:
                if {"subject", "relation", "object"}.issubset(t):
                    ses.execute_write(self._merge, t["subject"], t["relation"], t["object"])

    # ---------- Node2Vec ---------
    def run_node2vec(self):
        """Project graph → run Node2Vec → write embeddings to property `embedding`."""
        gname = "skill_graph_tmp"
        n2v_query = f"""
            CALL gds.graph.project('{gname}', '*', '*')
            YIELD graphName
            CALL gds.node2vec.write('{gname}', {{
              embeddingDimension: {SET.node2vec_dim},
              walkLength: {SET.node2vec_walk_length},
              iterations: 1,
              walksPerNode: {SET.node2vec_walks},
              writeProperty: 'embedding'
            }})
            YIELD nodePropertiesWritten
            CALL gds.graph.drop('{gname}') YIELD graphName;
        """
        with self._drv.session() as ses:
            ses.run(n2v_query)
        log.info("Node2Vec embeddings written to property 'embedding'.")

    def close(self):
        self._drv.close()

# ───────────────────────── Ingestion Routine ─────────────────────

def ingest_file(path: Path, reg: Registry, gw: GraphWriter):
    """Ingest a single markdown file if content changed."""
    sha = sha256(path)
    doc_id = path.stem
    if reg.get(doc_id) == sha:
        log.info("SKIP %s (unchanged)", doc_id)
        return

    text = path.read_text("utf-8")
    chunks = chunk(text, SET.chunk_size, SET.chunk_overlap)

    # Embeddings (for dedup / cache, future use)
    vectors = EMB.embed_documents(chunks)
    add_to_faiss(vectors)

    # Extract & write triples
    for ch in chunks:
        triples = glean_triples(ch)
        gw.write(triples)
    reg.upsert(doc_id, sha)
    log.info("OK   %s", doc_id)

# ───────────────────────── Main Driver ───────────────────────────

def main():
    reg = Registry(Path(SET.registry_path))
    gw = GraphWriter()
    try:
        for md_file in Path(SET.doc_root).rglob("*.md"):
            ingest_file(md_file, reg, gw)
        # After all inserts, compute Node2Vec embeddings once.
        gw.run_node2vec()
    finally:
        gw.close()

if __name__ == "__main__":
    main()

