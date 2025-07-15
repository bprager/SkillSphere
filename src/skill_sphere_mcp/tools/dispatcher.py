from typing import Any, Dict, List, Optional, Type
from fastapi import HTTPException
from neo4j import AsyncSession
from skill_sphere_mcp.tools.handlers import (
    explain_match, graph_search, match_role,
    MatchRoleOutputModel, ExplainMatchOutputModel, GraphSearchOutputModel
)

def generate_cv(*args, **kwargs) -> dict[str, Any]:
    # Stub for generate_cv to satisfy mypy
    return {} 