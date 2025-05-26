"""FAISS vector store for document embeddings."""

from pathlib import Path
from typing import List

import numpy as np  # type: ignore
import faiss  # type: ignore


# pylint: disable=R0903  # Too few public methods (1/2) - this is a simple manager class
class FaissManager:
    """Manages FAISS index operations."""

    _index = None

    @classmethod
    def add_vectors(cls, vectors: List[List[float]], index_path: str):
        """Add vector embeddings to the FAISS index and persist to disk."""
        if not faiss:
            return

        dim = len(vectors[0])
        if cls._index is None:
            idx_path = Path(index_path)
            cls._index = (
                faiss.read_index(str(idx_path))
                if idx_path.exists()
                else faiss.IndexFlatIP(dim)  # type: ignore[attr-defined]
            )
        # type: ignore[arg-type]
        cls._index.add(np.array(vectors, dtype="float32"))
        faiss.write_index(cls._index, str(index_path))  # type: ignore[attr-defined]
