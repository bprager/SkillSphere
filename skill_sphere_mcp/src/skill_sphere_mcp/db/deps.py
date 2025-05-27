"""Database dependencies."""

from fastapi import Depends

from ..db.connection import neo4j_conn

get_db_session = Depends(neo4j_conn.get_session)
