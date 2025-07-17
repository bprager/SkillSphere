"""Embedding model management."""

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Initialize the model at module level
try:
    MODEL: SentenceTransformer | None = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    MODEL = None
    logger.warning("sentence-transformers not installed, will use random embeddings")


def get_embedding_model() -> SentenceTransformer | None:
    """Get the embedding model instance.

    Returns:
        SentenceTransformer model or None if not available
    """
    return MODEL
