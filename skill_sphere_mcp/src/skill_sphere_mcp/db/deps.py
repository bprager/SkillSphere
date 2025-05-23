"""Database dependencies."""

from fastapi import Depends

from skill_sphere_mcp.db.neo4j import neo4j_conn

get_db_session = Depends(neo4j_conn.get_session)
