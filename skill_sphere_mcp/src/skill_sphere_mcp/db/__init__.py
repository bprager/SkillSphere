"""Database package initialization."""

from .connection import neo4j_conn

__all__ = ["neo4j_conn"]
