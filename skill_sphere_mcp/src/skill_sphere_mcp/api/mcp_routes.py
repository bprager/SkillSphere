"""MCP (Model Context Protocol) route definitions and handlers."""

import logging
from typing import Annotated, Any, Optional

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

from skill_sphere_mcp.auth.pat import get_current_token
from skill_sphere_mcp.db import neo4j_conn
from skill_sphere_mcp.graph.embeddings import embeddings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the model at module level
try:
    MODEL: Optional[SentenceTransformer] = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    MODEL = None
    logger.warning("sentence-transformers not installed, will use random embeddings")

get_db_session = Depends(neo4j_conn.get_session)

# Resource type constants
RESOURCE_SKILLS_NODE = "skills.node"
RESOURCE_SKILLS_RELATION = "skills.relation"
RESOURCE_PROFILES_SUMMARY = "profiles.summary"
RESOURCE_PROFILES_DETAIL = "profiles.detail"


class InitializeRequest(BaseModel):
    """MCP initialization request."""

    protocol_version: str = "1.0"


class InitializeResponse(BaseModel):
    """MCP initialization response."""

    protocol_version: str
    capabilities: dict[str, Any]
    instructions: str


class ResourceRequest(BaseModel):
    """Resource request model."""

    resource_type: str
    resource_id: str


class ToolRequest(BaseModel):
    """Tool request model."""

    tool_name: str
    parameters: dict[str, Any]


class MatchRoleRequest(BaseModel):
    """Skill matching request."""

    required_skills: Annotated[list[str], Field(min_items=1)]
    years_experience: dict[str, int] = Field(default_factory=dict)


class MatchRoleResponse(BaseModel):
    """Skill matching response."""

    match_score: float
    skill_gaps: list[str]
    matching_skills: list[dict[str, Any]]


class ExplainMatchRequest(BaseModel):
    """Match explanation request."""

    skill_id: str
    role_requirement: str


class ExplainMatchResponse(BaseModel):
    """Match explanation response."""

    explanation: str
    evidence: list[dict[str, Any]]


class GenerateCVRequest(BaseModel):
    """CV generation request."""

    target_keywords: Annotated[list[str], Field(min_items=1)]
    format: str = Field(pattern="^(markdown|html|pdf)$")


class GenerateCVResponse(BaseModel):
    """CV generation response."""

    content: str
    format: str


class GraphSearchRequest(BaseModel):
    """Graph search request."""

    query: str
    top_k: int = Field(default=10, ge=1, le=100)


@router.post("/rpc/initialize", response_model=InitializeResponse)
async def initialize(
    request: InitializeRequest, _token: str = Depends(get_current_token)
) -> InitializeResponse:
    """MCP handshake endpoint."""
    logger.info(
        "MCP initialization requested with version %s", request.protocol_version
    )
    return InitializeResponse(
        protocol_version="1.0",
        capabilities={
            "resources": [
                RESOURCE_SKILLS_NODE,
                RESOURCE_SKILLS_RELATION,
                RESOURCE_PROFILES_SUMMARY,
                RESOURCE_PROFILES_DETAIL,
            ],
            "tools": [
                "skill.match_role",
                "skill.explain_match",
                "cv.generate",
                "graph.search",
            ],
        },
        instructions="Use PAT for authentication. All endpoints are read-only.",
    )


@router.post("/rpc/resources/list")
async def list_resources(_token: str = Depends(get_current_token)) -> list[str]:
    """List available MCP resources."""
    return [
        RESOURCE_SKILLS_NODE,
        RESOURCE_SKILLS_RELATION,
        RESOURCE_PROFILES_SUMMARY,
        RESOURCE_PROFILES_DETAIL,
    ]


@router.post("/rpc/resources/get")
async def get_resource(
    request: ResourceRequest,
    session: AsyncSession = get_db_session,
    _token: str = Depends(get_current_token),
) -> dict[str, Any]:
    """Get a specific resource by type and ID."""
    logger.info("Resource request: %s/%s", request.resource_type, request.resource_id)

    # Map resource types to Cypher queries
    queries = {
        "skills.node": """
            MATCH (n:Skill) WHERE id(n) = $id
            RETURN n, labels(n) as labels, properties(n) as props
        """,
        "skills.relation": """
            MATCH (s:Skill)-[r]->(t) WHERE id(r) = $id
            RETURN r, type(r) as type, properties(r) as props,
                   id(s) as source_id, id(t) as target_id
        """,
        "profiles.summary": """
            MATCH (p:Profile) WHERE id(p) = $id
            RETURN p, labels(p) as labels, properties(p) as props
        """,
        "profiles.detail": """
            MATCH (p:Profile) WHERE id(p) = $id
            OPTIONAL MATCH (p)-[r]->(n)
            RETURN p, labels(p) as labels, properties(p) as props,
                   collect({rel: r, node: n}) as relationships
        """,
    }

    if request.resource_type not in queries:
        raise HTTPException(
            status_code=400, detail=f"Unknown resource type: {request.resource_type}"
        )

    try:
        result = await session.run(
            queries[request.resource_type], id=int(request.resource_id)
        )
        record = await result.single()
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Resource not found: {request.resource_type}/{request.resource_id}",
            )
        return dict(record)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid resource ID format"
        ) from None
    except Exception as exc:
        logger.error("Failed to get resource: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to retrieve resource"
        ) from exc


@router.post("/rpc/tools/dispatch")
async def dispatch_tool(
    request: ToolRequest,
    session: AsyncSession = get_db_session,
    _token: str = Depends(get_current_token),
) -> dict[str, Any]:
    """Dispatch a tool call to the appropriate handler."""
    logger.info("Tool request: %s", request.tool_name)

    tool_handlers = {
        "skill.match_role": match_role,
        "skill.explain_match": explain_match,
        "cv.generate": generate_cv,
        "graph.search": graph_search,
    }

    if request.tool_name not in tool_handlers:
        raise HTTPException(
            status_code=400, detail=f"Unknown tool: {request.tool_name}"
        )

    return await tool_handlers[request.tool_name](request.parameters, session)


async def match_role(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Match skills against role requirements."""
    try:
        request = MatchRoleRequest(**parameters)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {exc}"
        ) from exc

    # Query to get all skills and their relationships
    query = """
    MATCH (s:Skill)
    OPTIONAL MATCH (s)-[r]->(t)
    RETURN s, collect({rel: r, target: t}) as relationships
    """
    result = await session.run(query)
    skills = [record async for record in result]

    # Simple matching logic (to be enhanced)
    matching_skills = []
    skill_gaps = []

    for required_skill in request.required_skills:
        found = False
        for skill in skills:
            if skill["s"]["name"].lower() == required_skill.lower():
                matching_skills.append(
                    {
                        "name": skill["s"]["name"],
                        "properties": dict(skill["s"]),
                        "relationships": [
                            {"type": rel["rel"].type, "target": dict(rel["target"])}
                            for rel in skill["relationships"]
                        ],
                    }
                )
                found = True
                break
        if not found:
            skill_gaps.append(required_skill)

    match_score = len(matching_skills) / len(request.required_skills)

    return MatchRoleResponse(
        match_score=match_score, skill_gaps=skill_gaps, matching_skills=matching_skills
    ).dict()


async def explain_match(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Explain why a skill matches a role requirement."""
    try:
        request = ExplainMatchRequest(**parameters)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {exc}"
        ) from exc

    # Query to get skill details and related evidence
    query = """
    MATCH (s:Skill) WHERE id(s) = $skill_id
    OPTIONAL MATCH (s)-[r]->(t)
    RETURN s, collect({rel: r, target: t}) as evidence
    """

    try:
        result = await session.run(query, skill_id=int(request.skill_id))
        record = await result.single()
        if not record:
            raise HTTPException(
                status_code=404, detail=f"Skill not found: {request.skill_id}"
            )

        # Generate explanation based on evidence
        evidence = [
            {"type": rel["rel"].type, "target": dict(rel["target"])}
            for rel in record["evidence"]
        ]

        explanation = (
            f"Skill {record['s']['name']} matches requirement "
            f"'{request.role_requirement}' based on {len(evidence)} pieces of evidence."
        )

        return ExplainMatchResponse(
            explanation=explanation, evidence=evidence
        ).model_dump()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format") from None


async def generate_cv(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Generate a CV based on target keywords and format."""
    try:
        request = GenerateCVRequest(**parameters)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {exc}"
        ) from exc

    # Query to get profile and related skills
    query = """
    MATCH (p:Profile)
    OPTIONAL MATCH (p)-[r]->(s:Skill)
    RETURN p, collect({rel: r, skill: s}) as skills
    """

    result = await session.run(query)
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Generate CV content based on format
    if request.format == "markdown":
        content = f"# {record['p']['name']}\n\n"
        content += "## Skills\n\n"
        for skill in record["skills"]:
            content += f"- {skill['skill']['name']}\n"
    else:
        raise HTTPException(
            status_code=501, detail=f"Format not implemented: {request.format}"
        )

    return GenerateCVResponse(content=content, format=request.format).dict()


async def graph_search(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Perform semantic/graph search using Node2Vec embeddings."""
    try:
        request = GraphSearchRequest(**parameters)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {exc}"
        ) from exc

    try:
        if MODEL is None:
            raise ImportError("sentence-transformers not available")
        tensor = MODEL.encode(request.query)
        query_embedding: np.ndarray = tensor.numpy()  # Convert Tensor to numpy array
    except (ImportError, AttributeError, RuntimeError) as exc:
        logger.warning("Failed to encode query: %s", exc)
        query_embedding = np.random.default_rng(42).standard_normal(128)

    results = await embeddings.search(
        session=session, query_embedding=query_embedding, top_k=request.top_k
    )

    return {"results": results}
