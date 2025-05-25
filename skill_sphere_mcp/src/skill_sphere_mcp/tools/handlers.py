"""Tool handler implementations."""

import logging
from typing import Any

import numpy as np
from fastapi import HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.graph.embeddings import embeddings
from skill_sphere_mcp.graph.skill_matching import SkillMatchingService
from skill_sphere_mcp.routes import MODEL

logger = logging.getLogger(__name__)

# Initialize skill matching service
skill_matcher = SkillMatchingService()

# Initialize random number generator
rng = np.random.default_rng(42)  # Using 42 as a fixed seed for reproducibility


async def match_role(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Match skills to a role.

    Args:
        parameters: Tool parameters
        session: Database session

    Returns:
        Match result
    """
    required_skills = parameters.get("required_skills", [])
    years_experience = parameters.get("years_experience", {})

    # Type check for years_experience values
    for skill, years in years_experience.items():
        if not (isinstance(years, int) and type(years) is int):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid years_experience for skill '{skill}': {years} (must be int)",
            )

    if not required_skills:
        raise HTTPException(status_code=400, detail="No skills provided")

    # Get candidate skills from the database
    result = await session.run(
        """
        MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
        RETURN s.name as name, s.years as years
        """
    )
    candidate_skills = [
        {"name": record["name"], "years": record["years"] or 0}
        async for record in result
    ]

    # Convert required skills to the format expected by the matcher
    required_skills_list = [
        {"name": skill, "years": years_experience.get(skill, 0)}
        for skill in required_skills
    ]

    # Perform matching
    match_result = await skill_matcher.match_role(
        session=session,
        required_skills=required_skills_list,
        candidate_skills=candidate_skills,
    )

    return {
        "match_score": match_result.overall_score,
        "skill_gaps": match_result.skill_gaps,
        "matching_skills": [
            {
                "name": skill.skill_name,
                "score": skill.match_score,
                "evidence": skill.evidence,
                "years": skill.experience_years,
            }
            for skill in match_result.matching_skills
        ],
    }


async def explain_match(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Explain why a skill matches a role requirement.

    Args:
        parameters: Tool parameters
        session: Database session

    Returns:
        Explanation result
    """
    skill_id = parameters.get("skill_id")
    role_requirement = parameters.get("role_requirement")

    if not skill_id or not role_requirement:
        raise HTTPException(
            status_code=400,
            detail="Both skill_id and role_requirement are required",
        )

    # Query the graph for evidence
    query = """
    MATCH (s:Skill {id: $skill_id})
    OPTIONAL MATCH (s)-[r]-(related)
    RETURN s, collect({
        type: type(r),
        target: related,
        properties: properties(r)
    }) as evidence
    """
    result = await session.run(query, skill_id=skill_id)
    record = await result.single()

    if not record:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill = record["s"]
    evidence = record["evidence"]

    # Generate explanation
    explanation = f"Skill '{skill['name']}' matches '{role_requirement}' based on:\n"
    for item in evidence:
        if item["type"] == "HAS_EXPERIENCE":
            explanation += f"- {item['target']['name']} experience: {item['properties'].get('years', 0)} years\n"
        elif item["type"] == "RELATED_TO":
            explanation += f"- Related to: {item['target']['name']}\n"

    return {"explanation": explanation, "evidence": evidence}


async def generate_cv(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Generate a CV based on target keywords.

    Args:
        parameters: Tool parameters
        session: Database session

    Returns:
        Generated CV
    """
    target_keywords = parameters.get("target_keywords", [])
    format_type = parameters.get("format", "markdown")

    if not target_keywords:
        raise HTTPException(status_code=400, detail="No target keywords provided")

    if format_type not in ["markdown", "html", "pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Must be one of: markdown, html, pdf",
        )

    # TODO: Implement actual CV generation logic
    return {
        "content": "# Professional CV",
        "format": format_type,
    }


async def graph_search(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Search the graph for nodes matching a query.

    Args:
        parameters: Tool parameters
        session: Database session

    Returns:
        Search results
    """
    query = parameters.get("query")
    top_k = parameters.get("top_k", 10)

    if not query:
        raise HTTPException(status_code=400, detail="No query provided")

    if top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be greater than 0")

    # Get query embedding
    query_embedding = MODEL.encode(query) if MODEL else rng.random(128)

    # Search using embeddings
    results = await embeddings.search(session, query_embedding, top_k=top_k)

    return {
        "results": [
            {
                "node_id": result["node_id"],
                "score": result["score"],
                "labels": result["labels"],
                "properties": result["properties"],
            }
            for result in results
        ]
    }
