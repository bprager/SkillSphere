"""ingestion_worker.py
Clean, fully reviewed ingestion script for Bernd’s Hypergraph-of-Thought pipeline.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar, Iterable, List, Optional

import numpy as np  # type: ignore
import yaml
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from neo4j import GraphDatabase
from pydantic_settings import BaseSettings, SettingsConfigDict

# ──────────────────────── Optional FAISS ──────────────────────────
try:
    import faiss  # type: ignore
except ModuleNotFoundError:
    faiss = None  # type: ignore

# ─────────────────────────── Logging ───────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("ingestion")

# ───────────────────────── Configuration ──────────────────────────
class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_pass: str = "password"
    ollama_base_url: str = "http://127.0.0.1:11434"

    graph_schema_yaml: str = "./graph_schema.yaml"
    doc_root: str = "./docs"
    registry_path: str = "./doc_registry.sqlite3"
    faiss_index_path: str = "./faiss.index"

    chunk_size: int = 1500
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

SET = Settings()
SCHEMA = yaml.safe_load(Path(SET.graph_schema_yaml).read_text())
REL_HINTS: list[str] = [r["type"] for r in SCHEMA.get("relationships", [])]
KNOWN_SKILLS: list[str] = SCHEMA.get("prompt_steering", {}).get("known_skills", [])
KNOWN_TOOLS: list[str] = SCHEMA.get("prompt_steering", {}).get("known_tools", [])
ALIAS_MAP: dict = SCHEMA.get("prompt_steering", {}).get("alias_map", {})

# ───────────────────── Registry (SQLite) ─────────────────────────
CREATE_SQL = """
CREATE TABLE IF NOT EXISTS doc_registry (
  doc_id TEXT PRIMARY KEY,
  hash   TEXT NOT NULL,
  last_ingested DATETIME NOT NULL
);
"""

class Registry:
    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute(CREATE_SQL)

    def get(self, doc_id: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT hash FROM doc_registry WHERE doc_id=?", (doc_id,)
        ).fetchone()
        return row[0] if row else None

    def upsert(self, doc_id: str, sha: str):
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO doc_registry (doc_id, hash, last_ingested) VALUES (?,?,?) "
            "ON CONFLICT(doc_id) DO UPDATE SET hash=excluded.hash, last_ingested=excluded.last_ingested",
            (doc_id, sha, ts),
        )
        self.conn.commit()

# ──────────────────────────── Helpers ─────────────────────────────
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chunk(text: str, size: int, overlap: int) -> List[str]:
    words = text.split()
    step = size - overlap
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step)]

# ────────────────────────── Embeddings (Ollama) ────────────────────
class OllamaEmbeddingsCompat(OllamaEmbeddings):
    """Force older `/api/embed` endpoint used by Ollama ≤0.6.x."""
    embeddings_endpoint: ClassVar[str] = "/api/embed"

EMB = OllamaEmbeddingsCompat(model="nomic-embed-text", base_url=SET.ollama_base_url)

_FAISS_INDEX: Optional[object] = None

def add_to_faiss(vectors: List[List[float]]):
    global _FAISS_INDEX
    if not faiss:
        return
    dim = len(vectors[0])
    if _FAISS_INDEX is None:
        idx_path = Path(SET.faiss_index_path)
        _FAISS_INDEX = faiss.read_index(str(idx_path)) if idx_path.exists() else faiss.IndexFlatIP(dim)
    _FAISS_INDEX.add(np.array(vectors, dtype="float32"))  # type: ignore
    faiss.write_index(_FAISS_INDEX, str(SET.faiss_index_path))

# ────────────────────── LLM Extraction (Ollama) ───────────────────
LLM = ChatOllama(model="gemma3:12b", base_url=SET.ollama_base_url)
PROMPT_TEMPLATE = (
    "You are an information-extraction assistant. Output strict JSON (list of triples).\n"
    "Use relation names: {rels}. Prefer SKILL names: {skills}. Prefer TOOL names: {tools}.\n"
    "Alias map: {aliases}.\n"
    "Text:```{chunk}```"
)

def _clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```", 2)
        if len(parts) >= 2:
            raw = parts[1]
    for i, ch in enumerate(raw):
        if ch in "[{":
            return raw[i:]
    return raw


def extract_triples(text_chunk: str, retries: int = 2) -> List[dict]:
    prompt = PROMPT_TEMPLATE.format(
        rels=", ".join(REL_HINTS),
        skills=", ".join(KNOWN_SKILLS),
        tools=", ".join(KNOWN_TOOLS),
        aliases=json.dumps(ALIAS_MAP),
        chunk=text_chunk,
    )
    for attempt in range(retries):
        resp = LLM.invoke(prompt)
        cleaned = _clean_json(resp.content)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(cleaned) or []
            except Exception:
                if attempt + 1 < retries:
                    prompt = (
                        prompt
                        + "\n\nONLY return valid JSON -- no commentary, no markdown fences."
                    )
                else:
                    log.warning("LLM JSON parse failed after %d attempts", retries)
    return []

# ───────────────────────── Neo4j Writer ───────────────────────────
class GraphWriter:
    def __init__(self):
        self._drv = GraphDatabase.driver(
            SET.neo4j_uri, auth=(SET.neo4j_user, SET.neo4j_pass)
        )

    def close(self):
        self._drv.close()

    @staticmethod
    def _merge(tx, s: str, r: str, o: str):
        tx.run(
            f"MERGE (a:Entity {{name:$s}})\n"
            f"MERGE (b:Entity {{name:$o}})\n"
            f"MERGE (a)-[:`{r}`]->(b)",
            s=s,
            o=o,
        )

    def write(self, triples: List[dict]):
        with self._drv.session() as session:
            for t in triples:
                if {"subject", "relation", "object"}.issubset(t):
                    session.execute_write(
                        self._merge, t["subject"], t["relation"], t["object"]
                    )

# ───────────────────────── Ingestion Logic ───────────────────────
def ingest_file(path: Path, reg: Registry, gw: GraphWriter):
    doc_id = path.stem
    sha = sha256(path)
    if reg.get(doc_id) == sha:
        log.info("SKIP %s (unchanged)", doc_id)
        return

    text = path.read_text("utf-8")
    chunks = chunk(text, SET.chunk_size, SET.chunk_overlap)

    # Embeddings
    vectors = EMB.embed_documents(chunks)
    add_to_faiss(vectors)

    # Extraction and writing
    for ch in chunks:
        triples = extract_triples(ch)
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
    finally:
        gw.close()

if __name__ == "__main__":
    main()

