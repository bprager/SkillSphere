"""Tool handlers for the MCP server."""

from typing import Any

from fastapi import HTTPException
from neo4j import AsyncSession


async def explain_match(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Explain why a skill matches a role requirement.

    Args:
        parameters: Tool parameters
        session: Neo4j database session

    Returns:
        Match explanation
    """
    skill_id = parameters.get("skill_id")
    role_requirement = parameters.get("role_requirement")

    if not skill_id or not role_requirement:
        raise HTTPException(
            status_code=400,
            detail="Missing required parameters: skill_id and role_requirement",
        )

    # Query the database to find evidence for the match
    query = """
    MATCH (s:Skill {id: $skill_id})
    OPTIONAL MATCH (s)-[:USED_IN]->(p:Project)
    OPTIONAL MATCH (s)-[:CERTIFIED_IN]->(c:Certification)
    RETURN s, collect(p) as projects, collect(c) as certifications
    """
    result = await session.run(query, skill_id=skill_id)
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")

    skill = record["s"]
    projects = record["projects"]
    certifications = record["certifications"]

    # Build evidence list
    evidence = []
    for project in projects:
        evidence.append(
            {"type": "project", "description": f"Used in project: {project['name']}"}
        )
    for cert in certifications:
        evidence.append(
            {"type": "certification", "description": f"Certified in: {cert['name']}"}
        )

    # Generate explanation
    explanation = (
        f"Skill {skill['name']} matches requirement '{role_requirement}' "
        f"based on {len(projects)} projects and {len(certifications)} certifications."
    )

    return {
        "explanation": explanation,
        "evidence": evidence,
    }


async def graph_search(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Graph search tool handler."""
    query = parameters.get("query")
    top_k = parameters.get("top_k", 5)
    if not query:
        raise HTTPException(status_code=400, detail="Missing query parameter")
    if top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be greater than 0")

    # Query the database to find nodes matching the query
    cypher_query = """
    MATCH (n)
    WHERE n.name CONTAINS $search_query OR n.description CONTAINS $search_query
    RETURN n
    LIMIT $top_k
    """
    result = await session.run(cypher_query, search_query=query, top_k=top_k)
    records = await result.fetch_all()  # type: ignore[attr-defined]
    results = [{"node": record["n"]} for record in records]

    return {"results": results, "query": query, "top_k": top_k}


async def match_role(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Match role tool handler (returns match_score, skill_gaps, matching_skills)."""
    required_skills = parameters.get("required_skills")
    years_experience = parameters.get("years_experience", {})
    if not required_skills:
        raise HTTPException(status_code=400, detail="Missing required_skills parameter")
    if not isinstance(years_experience, dict):
        raise HTTPException(
            status_code=400, detail="years_experience must be a dictionary"
        )

    # Validate that all years_experience values are integers
    for skill, years in years_experience.items():
        if not isinstance(years, int):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid years_experience for skill '{skill}': {years} (must be int)",
            )

    # Query the database to find matching profiles
    query = """
    MATCH (p:Person)
    WHERE ALL(skill IN $required_skills WHERE (p)-[:HAS_SKILL]->(:Skill {name: skill}))
    RETURN p
    """
    result = await session.run(query, required_skills=required_skills)
    records = await result.fetch_all()

    matching_skills = []
    skill_gaps = []
    for skill in required_skills:
        found = False
        for record in records:
            if skill in record["p"].get("skills", []):
                matching_skills.append({"name": skill})
                found = True
                break
        if not found:
            skill_gaps.append(skill)

    match_score = (
        len(matching_skills) / len(required_skills) if required_skills else 0.0
    )

    return {
        "match_score": match_score,
        "skill_gaps": skill_gaps,
        "matching_skills": matching_skills,
    }
