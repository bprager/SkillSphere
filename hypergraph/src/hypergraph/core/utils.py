"""Utility functions for the hypergraph pipeline."""

import hashlib

from pathlib import Path
from typing import List


def sha256(path: Path) -> str:
    """Compute SHA-256 hash of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chunk(text: str, size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks of specified size."""
    words = text.split()
    step = size - overlap
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step)]
