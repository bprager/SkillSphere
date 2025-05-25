"""MCP (Model Context Protocol) route definitions and handlers."""

import logging
from typing import Annotated, Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession
from pydantic import BaseModel, Field
from sklearn.metrics.pairwise import cosine_similarity

from skill_sphere_mcp.api.jsonrpc import JSONRPCHandler, JSONRPCRequest, JSONRPCResponse
from skill_sphere_mcp.db import neo4j_conn
from skill_sphere_mcp.graph.embeddings import embeddings
from skill_sphere_mcp.models.embedding import get_embedding_model
from skill_sphere_mcp.models.graph import GraphNode, GraphRelationship
from skill_sphere_mcp.tools.dispatcher import dispatch_tool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mcp")
rpc_handler = JSONRPCHandler()

# Get the model instance
MODEL = get_embedding_model()

get_db_session = Depends(neo4j_conn.get_session)

# Resource type constants
RESOURCE_SKILLS_NODE = "skills.node"
RESOURCE_SKILLS_RELATION = "skills.relation"
RESOURCE_PROFILES_SUMMARY = "profiles.summary"
RESOURCE_PROFILES_DETAIL = "profiles.detail"

# Constants
SKILL_MATCH_THRESHOLD = 0.7


class InitializeRequest(BaseModel):
    """Initialize request model."""

    protocol_version: str
    client_info: dict[str, Any]


class InitializeResponse(BaseModel):
    """Initialize response model."""

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

    required_skills: Annotated[list[str], Field(min_length=1)]
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

    target_keywords: Annotated[list[str], Field(min_length=1)]
    format: str = Field(pattern="^(markdown|html|pdf)$")


class GenerateCVResponse(BaseModel):
    """CV generation response."""

    content: str
    format: str


class GraphSearchRequest(BaseModel):
    """Graph search request."""

    query: str
    top_k: int = Field(default=10, ge=1, le=100)


@router.post("/initialize")
async def initialize(request: InitializeRequest) -> InitializeResponse:
    """Initialize the MCP server."""
    return InitializeResponse(
        protocol_version="1.0",
        capabilities={
            "semantic_search": True,
            "graph_query": True,
            "tool_dispatch": True,
        },
        instructions="Public access enabled. All endpoints are read-only.",
    )


@router.get("/resources/list")
async def list_resources() -> list[str]:
    """List available resources."""
    return ["nodes", "relationships", "search"]


async def get_resource(resource: str) -> dict[str, Any]:
    """Get resource information."""
    if resource == "nodes":
        return {
            "type": "collection",
            "schema": GraphNode.schema(),
        }
    elif resource == "relationships":
        return {
            "type": "collection",
            "schema": GraphRelationship.schema(),
        }
    elif resource == "search":
        return {
            "type": "action",
            "schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
        }
    elif resource == RESOURCE_SKILLS_NODE:
        return {
            "type": "collection",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["id", "name"],
            },
        }
    elif resource == RESOURCE_SKILLS_RELATION:
        return {
            "type": "collection",
            "schema": {
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "target_id": {"type": "string"},
                    "type": {"type": "string"},
                    "weight": {"type": "number"},
                },
                "required": ["source_id", "target_id", "type"],
            },
        }
    elif resource == RESOURCE_PROFILES_DETAIL:
        return {
            "type": "collection",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "years_experience": {"type": "number"},
                            },
                        },
                    },
                },
                "required": ["id", "name"],
            },
        }
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid resource type: {resource}"
        )


@router.get("/resources/get/{resource}")
async def get_resource_mcp(
    request: ResourceRequest,
) -> dict[str, Any]:
    """Get resource information."""
    return await get_resource(request.resource_type)


@router.post("/rpc")
async def rpc_endpoint(
    request: JSONRPCRequest,
) -> JSONRPCResponse:
    """Handle JSON-RPC requests."""
    return await rpc_handler.handle_request(request)


@rpc_handler.register("initialize")
async def rpc_initialize(params: dict[str, Any]) -> dict[str, Any]:
    """Handle initialize RPC method."""
    request = InitializeRequest(**params)
    response = await initialize(request)
    return response.model_dump()


@rpc_handler.register("resources/list")
async def rpc_list_resources(_: dict[str, Any]) -> list[str]:
    """Handle resources/list RPC method."""
    return await list_resources()


@rpc_handler.register("resources/get")
async def rpc_get_resource(
    params: dict[str, Any], session: AsyncSession = get_db_session
) -> dict[str, Any]:
    """Handle resources/get RPC method."""
    resource = params.get("resource")
    if not resource:
        raise HTTPException(status_code=400, detail="Missing resource parameter")
    return await get_resource(resource)


@rpc_handler.register("search")
async def rpc_search(
    params: dict[str, Any], session: AsyncSession = get_db_session
) -> list[dict[str, Any]]:
    """Handle search RPC method."""
    query = params.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Missing query parameter")
    limit = params.get("limit", 10)
    response = await graph_search({"query": query, "top_k": limit}, session)
    return list(response["results"])


@rpc_handler.register("tool")
async def rpc_tool(
    params: dict[str, Any], session: AsyncSession = get_db_session
) -> Any:
    """Handle tool dispatch requests."""
    return await dispatch_tool(params["name"], params["parameters"], session)


@rpc_handler.register("skill.match_role")
async def rpc_match_role_handler(
    params: dict[str, Any], session: AsyncSession = get_db_session
) -> dict[str, Any]:
    """Handle skill matching requests."""
    return await match_role(params, session)


@router.post("/rpc/initialize", response_model=InitializeResponse)
async def initialize_mcp(
    request: InitializeRequest,
) -> InitializeResponse:
    """Initialize MCP server."""
    return await initialize(request)


@router.post("/rpc/resources/list")
async def list_resources_mcp() -> list[str]:
    """List available resources."""
    return await list_resources()


@router.post("/rpc/tools/dispatch")
async def dispatch_tool_mcp(
    request: ToolRequest,
    session: AsyncSession = get_db_session,
) -> dict[str, Any]:
    """Dispatch a tool call."""
    result = await dispatch_tool(request.tool_name, request.parameters, session)
    return dict(result)


async def _validate_match_request(parameters: dict[str, Any]) -> MatchRoleRequest:
    """Validate and parse match request parameters."""
    try:
        return MatchRoleRequest(**parameters)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {exc}"
        ) from exc


async def _get_skills_with_relationships(session: AsyncSession) -> list[dict[str, Any]]:
    """Get all skills with their relationships from the database."""
    query = """
    MATCH (s:Skill)
    OPTIONAL MATCH (s)-[r]->(t)
    WITH s, collect({rel: r, target: t}) as relationships
    OPTIONAL MATCH (p:Person)-[e:HAS_SKILL]->(s)
    WITH s, relationships, collect(e.years) as experience_years
    RETURN s, relationships, experience_years
    """
    result = await session.run(query)
    return [dict(record) async for record in result]


def _collect_evidence(relationships: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect evidence from relationships."""
    return [
        {
            "type": rel["rel"].type,
            "target": dict(rel["target"]) if rel["target"] else None,
            "properties": dict(rel["rel"]),
        }
        for rel in relationships
    ]


async def _calculate_semantic_score(skill1: str, skill2: str) -> float:
    """Calculate semantic similarity between two skills."""
    try:
        vec1 = await MODEL.get_embedding(skill1)
        vec2 = await MODEL.get_embedding(skill2)
        return float(cosine_similarity([vec1], [vec2])[0][0])
    except Exception:
        return 0.0


def _calculate_experience_score(actual_years: list[int], required_years: int) -> float:
    """Calculate experience score based on years."""
    if not actual_years or not required_years:
        return 1.0
    max_actual = max(actual_years)
    return min(max_actual / required_years, 1.0)


async def _process_skill_match(
    required_skill: str,
    required_years: int,
    skills: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, float]:
    """Process a single skill match and return best match with score."""
    best_match = None
    best_score = 0.0

    for skill in skills:
        # Calculate scores
        semantic_score = await _calculate_semantic_score(
            required_skill, skill["s"]["name"]
        )
        exact_score = (
            1.0 if skill["s"]["name"].lower() == required_skill.lower() else 0.0
        )
        experience_score = _calculate_experience_score(
            skill["experience_years"], required_years
        )

        # Combined score (weighted)
        combined_score = (
            0.6 * max(exact_score, semantic_score)  # Skill match
            + 0.4 * experience_score  # Experience match
        )

        if combined_score > best_score:
            best_score = combined_score
            best_match = skill

    return best_match, best_score


async def match_role(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Match skills against role requirements."""
    request = await _validate_match_request(parameters)

    # Validate years_experience values
    for skill, years in request.years_experience.items():
        if not (isinstance(years, int) and type(years) is int):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid years_experience for skill '{skill}': {years} (must be int)",
            )

    skills = await _get_skills_with_relationships(session)

    # Initialize results
    matching_skills = []
    skill_gaps = []
    supporting_nodes = []

    # Process each required skill
    for required_skill in request.required_skills:
        required_years = request.years_experience.get(required_skill, 0)
        best_match, best_score = await _process_skill_match(
            required_skill, required_years, skills
        )

        # Process the best match
        if best_match and best_score >= SKILL_MATCH_THRESHOLD:
            evidence = _collect_evidence(best_match["relationships"])
            matching_skills.append(
                {
                    "name": best_match["s"]["name"],
                    "properties": dict(best_match["s"]),
                    "relationships": evidence,
                    "match_score": best_score,
                    "experience_years": (
                        max(best_match["experience_years"])
                        if best_match["experience_years"]
                        else 0
                    ),
                }
            )
            supporting_nodes.extend(
                [
                    rel["target"].id
                    for rel in best_match["relationships"]
                    if rel["target"]
                ]
            )
        else:
            skill_gaps.append(required_skill)

    # Calculate overall match score
    match_score = len(matching_skills) / len(request.required_skills)

    return MatchRoleResponse(
        match_score=match_score,
        skill_gaps=skill_gaps,
        matching_skills=matching_skills,
    ).model_dump()


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

    response = GenerateCVResponse(content=content, format=request.format)
    return response.model_dump()


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
