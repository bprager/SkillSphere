"""SQLite registry for tracking document ingestion status."""

import sqlite3

from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Optional


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
        """Initialize registry with SQLite database path."""
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute(CREATE_SQL)

    def get(self, doc_id: str) -> Optional[str]:
        """Retrieve the hash of a document by its ID."""
        row = self.conn.execute(
            "SELECT hash FROM doc_registry WHERE doc_id=?", (doc_id,)
        ).fetchone()
        return row[0] if row else None

    def upsert(self, doc_id: str, sha: str):
        """Update or insert a document's hash and ingestion timestamp."""
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO doc_registry (doc_id, hash, last_ingested) VALUES (?,?,?) "
            "ON CONFLICT(doc_id) DO UPDATE SET "
            "hash=excluded.hash, last_ingested=excluded.last_ingested",
            (doc_id, sha, ts),
        )
        self.conn.commit()
