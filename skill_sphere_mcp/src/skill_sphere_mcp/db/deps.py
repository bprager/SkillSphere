"""Database dependency injection."""

from typing import AsyncGenerator

from neo4j import AsyncSession

from ..config.settings import get_settings
from .connection import DatabaseConnection


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    settings = get_settings()
    connection = DatabaseConnection(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    await connection.connect()

    session = connection.get_session()
    if session is None:
        await connection.close()
        raise RuntimeError("Failed to create database session")

    try:
        yield session
    finally:
        if session is not None:
            try:
                # Close session if it exists
                if hasattr(session, 'close') and callable(session.close):
                    session.close()  # type: ignore[unused-coroutine]
            except Exception:
                # Ignore close errors
                pass
        await connection.close()
