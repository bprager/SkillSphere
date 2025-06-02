"""MCP API handlers."""

import logging
from typing import Annotated, Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore[import-untyped]

from ...db.deps import get_db_session
from ...graph.embeddings import embeddings
from ...models.embedding import get_embedding_model
from ...models.mcp import (
    InitializeRequest,
    InitializeResponse,
    QueryRequest,
    QueryResponse,
    ResourceRequest,
    ResourceResponse,
    SearchRequest,
    SearchResponse,
)
from .models import (
    ExplainMatchRequest,
    ExplainMatchResponse,
    GraphSearchRequest,
    MatchRoleRequest,
    MatchRoleResponse,
)
from .utils import get_initialize_response_dict, get_resource

logger = logging.getLogger(__name__)

# Get the model instance
MODEL = get_embedding_model()

# Constants
SKILL_MATCH_THRESHOLD = 0.5

router = APIRouter()


@router.post("/initialize", response_model=InitializeResponse)
async def initialize(_request: InitializeRequest) -> dict[str, Any]:
    """Initialize the MCP connection."""
    return get_initialize_response_dict()


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """Execute a Cypher query."""
    try:
        result = await session.run(request.query, request.parameters or {})
        records = await result.fetch_all()
        return {
            "results": [dict(record) for record in records],
            "metadata": {
                "nodes_created": result.consume().counters.nodes_created,
                "relationships_created": result.consume().counters.relationships_created,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """Search for nodes by text similarity."""
    print("DEBUG: Starting search handler")  # Debug print
    try:
        logger.info("Starting search with query: %s", request.query)
        print(f"DEBUG: Query: {request.query}")  # Debug print

        # Get all nodes with their labels and properties
        print("DEBUG: Running Neo4j query")  # Debug print
        result = await session.run("MATCH (n) RETURN n, labels(n) as labels")
        nodes = await result.fetch_all()
        print(f"DEBUG: Fetched {len(nodes)} nodes")  # Debug print
        logger.info("Fetched %d nodes from database", len(nodes))

        try:
            nodes = [
                {
                    "node_id": (
                        str(record["n"].id)
                        if hasattr(record["n"], "id")
                        else record["n"]["id"]
                    ),
                    "labels": record["labels"],
                    "properties": (
                        dict(record["n"])
                        if hasattr(record["n"], "__dict__")
                        else record["n"]
                    ),
                }
                for record in nodes
            ]
            print(f"DEBUG: Processed nodes: {nodes}")  # Debug print
            logger.info("Processed nodes: %s", nodes)
        except Exception as e:
            print(f"DEBUG: Error processing nodes: {e!s}")  # Debug print
            logger.error("Error processing nodes: %s", str(e))
            raise

        # Get query embedding
        print("DEBUG: Getting query embedding")  # Debug print
        try:
            query_embedding = MODEL.get_embedding(request.query)
            print(f"DEBUG: Query embedding: {query_embedding}")  # Debug print
            logger.info("Got query embedding: %s", query_embedding)
        except Exception as e:
            print(f"DEBUG: Error getting query embedding: {e!s}")  # Debug print
            logger.error("Error getting query embedding: %s", str(e))
            raise

        # Calculate similarity scores
        results = []
        for node in nodes:
            try:
                node_id = node["node_id"]
                print(f"DEBUG: Processing node {node_id}")  # Debug print

                # Handle both direct properties and nested properties
                properties = node["properties"]
                if isinstance(properties, dict) and "properties" in properties:
                    properties = properties["properties"]
                name = properties.get("name", "")
                print(f"DEBUG: Node name: {name}")  # Debug print

                node_embedding = MODEL.get_embedding(name)
                print(f"DEBUG: Node embedding: {node_embedding}")  # Debug print
                logger.info("Got node embedding for %s: %s", name, node_embedding)

                score = 0.0
                if query_embedding is not None and node_embedding is not None:
                    try:
                        # Both are numpy arrays
                        score = float(
                            np.dot(query_embedding, node_embedding)
                            / (
                                np.linalg.norm(query_embedding)
                                * np.linalg.norm(node_embedding)
                                + 1e-8
                            )
                        )
                        print(f"DEBUG: Calculated score: {score}")  # Debug print
                    except Exception as e:
                        print(
                            f"DEBUG: Error calculating score: {e!s}"
                        )  # Debug print
                        logger.error("Error calculating score: %s", str(e))
                        score = 0.0

                logger.info("Calculated score for node %s: %f", node_id, score)

                results.append(
                    {
                        "node_id": node_id,
                        "score": score,
                        "labels": node["labels"],
                        "properties": properties,
                    }
                )
            except Exception as e:
                print(f"DEBUG: Error processing node: {e!s}")  # Debug print
                logger.error("Error processing node: %s", str(e))
                continue

        # Sort by similarity score
        results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True,
        )[: request.limit]
        print(f"DEBUG: Final results: {results}")  # Debug print
        logger.info("Final results: %s", results)

        return {"results": results}
    except Exception as e:
        print(f"DEBUG: Handler error: {e!s}")  # Debug print
        logger.warning("Failed to encode query: %s", str(e))
        return {"results": []}


@router.post("/resource", response_model=ResourceResponse)
async def get_resource_info(request: ResourceRequest) -> dict[str, Any]:
    """Get resource information."""
    resource_info = await get_resource(request.resource)
    return {"type": resource_info["type"], "resource_schema": resource_info["schema"]}


async def _validate_match_request(parameters: dict[str, Any]) -> MatchRoleRequest:
    """Validate and parse match request parameters."""
    try:
        return MatchRoleRequest(**parameters)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {exc}"
        ) from exc


async def _get_skills_with_relationships(session: AsyncSession) -> list[dict[str, Any]]:
    """Get all skills with their relationships from the database."""
    cypher_query = """
    MATCH (s:Skill)
    OPTIONAL MATCH (s)-[r]->(t)
    WITH s, collect({rel: r, target: t}) as relationships
    OPTIONAL MATCH (p:Person)-[e:HAS_SKILL]->(s)
    WITH s, relationships, collect(e.years) as experience_years
    RETURN s, relationships, experience_years
    """
    result = await session.run(cypher_query)
    return [dict(record) async for record in result]


def _collect_evidence(relationships: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect evidence from relationships."""
    return [
        {
            "type": rel["rel"]["type"],
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
    except (ValueError, TypeError, AttributeError, IndexError, RuntimeError):
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

    # Validate required_skills is not empty
    if not request.required_skills:
        raise HTTPException(
            status_code=400,
            detail="required_skills cannot be empty",
        )

    # Validate years_experience values
    for skill, years in request.years_experience.items():
        if not isinstance(years, int):
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
                    rel["target"]["id"]
                    for rel in best_match["relationships"]
                    if rel["target"]
                ]
            )
        else:
            skill_gaps.append(required_skill)

    # Calculate overall match score
    match_score = (
        len(matching_skills) / len(request.required_skills)
        if request.required_skills
        else 0.0
    )

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
    cypher_query = """
    MATCH (s:Skill) WHERE id(s) = $skill_id
    OPTIONAL MATCH (s)-[r]->(t)
    RETURN s, collect({rel: r, target: t}) as evidence
    """

    try:
        result = await session.run(cypher_query, skill_id=int(request.skill_id))
        record = await result.single()
        if not record:
            raise HTTPException(
                status_code=404, detail=f"Skill not found: {request.skill_id}"
            )

        # Generate explanation based on evidence
        evidence = [
            {"type": rel["rel"]["type"], "target": dict(rel["target"])}
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

    # Validate top_k
    if request.top_k <= 0:
        raise HTTPException(
            status_code=400,
            detail="top_k must be greater than 0",
        )

    try:
        if MODEL is None:
            raise ImportError("sentence-transformers not available")
        tensor = MODEL.encode(request.query)
        query_embedding: np.ndarray = tensor.numpy()  # Convert Tensor to numpy array
    except (ImportError, AttributeError, RuntimeError) as exc:
        logger.warning("Failed to encode query: %s", exc)
        query_embedding = np.random.default_rng().standard_normal(128)

    results = await embeddings.search(
        session=session, query_embedding=query_embedding, top_k=request.top_k
    )

    return {"results": results}


async def handle_search(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Handle search request.

    Args:
        parameters: Search parameters
        session: Neo4j database session

    Returns:
        Search results
    """
    result = await graph_search(parameters, session)
    return dict(result)  # Ensure we return a dict


async def handle_tool(
    tool_name: str, parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Handle tool request.

    Args:
        tool_name: Name of the tool to execute
        parameters: Tool parameters
        session: Neo4j database session

    Returns:
        Tool execution results

    Raises:
        HTTPException: If tool name is invalid
    """
    if tool_name == "match_role":
        result = await match_role(parameters, session)
        return dict(result)
    if tool_name == "explain_match":
        result = await explain_match(parameters, session)
        return dict(result)
    if tool_name == "graph_search":
        result = await graph_search(parameters, session)
        return dict(result)
    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}") from None
