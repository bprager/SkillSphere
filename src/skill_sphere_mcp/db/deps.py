from typing import AsyncGenerator

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    from skill_sphere_mcp.db.connection import DatabaseConnection
    from skill_sphere_mcp.config.settings import get_settings
    settings = get_settings()
    conn = DatabaseConnection(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    await conn.connect()
    session = conn.get_session()
    try:
        yield session
    finally:
        if session:
            await session.close()
    await conn.close() 