"""CV generation module."""

from typing import Any

from fastapi import HTTPException
from neo4j import AsyncSession
from pydantic import BaseModel
from pydantic import Field

from ..utils.validation import validate_parameters


class GenerateCVRequest(BaseModel):
    """CV generation request."""

    target_keywords: list[str] = Field(min_length=1)
    format: str = Field(pattern="^(markdown|html|pdf)$")


class GenerateCVResponse(BaseModel):
    """CV generation response."""

    content: str
    format: str


def _format_contact_info(person: dict[str, Any], is_html: bool = False) -> str:
    """Format contact information section."""
    if not any(key in person for key in ["email", "phone"]):
        return ""

    if is_html:
        content = "<div class='contact'>"
        if "email" in person:
            content += f"<p>Email: {person['email']}</p>"
        if "phone" in person:
            content += f"<p>Phone: {person['phone']}</p>"
        content += "</div>"
    else:
        content = ""
        if "email" in person:
            content += f"Email: {person['email']}\n"
        if "phone" in person:
            content += f"Phone: {person['phone']}\n"
        content += "\n"

    return content


def _format_summary(person: dict[str, Any], is_html: bool = False) -> str:
    """Format summary section."""
    if "summary" not in person:
        return ""

    if is_html:
        return f"<h2>Summary</h2><p>{person['summary']}</p>"
    return f"## Summary\n{person['summary']}\n\n"


def _format_skills(skills: list[dict[str, Any]], is_html: bool = False) -> str:
    """Format skills section."""
    if is_html:
        content = "<h2>Skills</h2>"
        if skills:
            content += "<ul>"
            for skill in skills:
                content += f"<li>{skill['name']}</li>"
            content += "</ul>"
        else:
            content += "<p>No skills listed</p>"
    else:
        content = "## Skills\n"
        if skills:
            for skill in skills:
                content += f"- {skill['name']}\n"
        else:
            content += "No skills listed\n"
        content += "\n"

    return content


def _format_company(company: dict[str, Any], is_html: bool = False) -> str:
    """Format a single company entry."""
    if is_html:
        content = f"<div class='experience'><h3>{company['name']}</h3>"
        if "position" in company:
            content += f"<p class='position'>{company['position']}</p>"
        if "start_date" in company and "end_date" in company:
            content += (
                f"<p class='dates'>{company['start_date']} - {company['end_date']}</p>"
            )
        if "description" in company:
            content += f"<p class='description'>{company['description']}</p>"
        content += "</div>"
    else:
        content = f"### {company['name']}\n"
        if "position" in company:
            content += f"{company['position']}\n"
        if "start_date" in company and "end_date" in company:
            content += f"{company['start_date']} - {company['end_date']}\n"
        if "description" in company:
            content += f"{company['description']}\n"
        content += "\n"

    return content


def _format_experience(companies: list[dict[str, Any]], is_html: bool = False) -> str:
    """Format experience section."""
    if is_html:
        content = "<h2>Experience</h2>"
        if companies:
            for company in companies:
                content += _format_company(company, is_html)
        else:
            content += "<p>No experience listed</p>"
    else:
        content = "## Experience\n"
        if companies:
            for company in companies:
                content += _format_company(company, is_html)
        else:
            content += "No experience listed\n\n"

    return content


def _format_education_entry(edu: dict[str, Any], is_html: bool = False) -> str:
    """Format a single education entry."""
    if is_html:
        content = f"<div class='education'><h3>{edu['institution']}</h3>"
        if "degree" in edu:
            content += f"<p class='degree'>{edu['degree']}</p>"
        if "field" in edu:
            content += f"<p class='field'>{edu['field']}</p>"
        if "graduation_year" in edu:
            content += f"<p class='graduation'>Graduated: {edu['graduation_year']}</p>"
        content += "</div>"
    else:
        content = f"### {edu['institution']}\n"
        if "degree" in edu:
            content += f"{edu['degree']}\n"
        if "field" in edu:
            content += f"{edu['field']}\n"
        if "graduation_year" in edu:
            content += f"Graduated: {edu['graduation_year']}\n"
        content += "\n"

    return content


def _format_education(education: list[dict[str, Any]], is_html: bool = False) -> str:
    """Format education section."""
    if is_html:
        content = "<h2>Education</h2>"
        if education:
            for edu in education:
                content += _format_education_entry(edu, is_html)
        else:
            content += "<p>No education listed</p>"
    else:
        content = "## Education\n"
        if education:
            for edu in education:
                content += _format_education_entry(edu, is_html)
        else:
            content += "No education listed\n\n"

    return content


def _generate_markdown_cv(record: dict[str, Any]) -> str:
    """Generate markdown CV content."""
    person = record["p"]
    skills = record["skills"]
    companies = record["companies"]
    education = record["education"]

    content = f"# {person['name']}\n\n"
    content += _format_contact_info(person)
    content += _format_summary(person)
    content += _format_skills(skills)
    content += _format_experience(companies)
    content += _format_education(education)

    return content


def _generate_html_cv(record: dict[str, Any]) -> str:
    """Generate HTML CV content."""
    person = record["p"]
    skills = record["skills"]
    companies = record["companies"]
    education = record["education"]

    content = f"<h1>{person['name']}</h1>"
    content += _format_contact_info(person, is_html=True)
    content += _format_summary(person, is_html=True)
    content += _format_skills(skills, is_html=True)
    content += _format_experience(companies, is_html=True)
    content += _format_education(education, is_html=True)

    return content


async def generate_cv(
    parameters: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Generate a CV based on target keywords and format.

    Args:
        parameters: Request parameters containing target_keywords and format
        session: Neo4j database session

    Returns:
        Generated CV content and format

    Raises:
        HTTPException: If parameters are invalid or profile not found
    """
    try:
        request = validate_parameters(parameters, GenerateCVRequest)
    except ValueError as e:
        # Always raise 422 for validation errors
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}") from e

    # Query to find a profile matching the target keywords
    query = """
    MATCH (p:Person)
    WHERE ANY(keyword IN $keywords WHERE p.name CONTAINS keyword)
    OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
    OPTIONAL MATCH (p)-[:WORKED_AT]->(c:Company)
    OPTIONAL MATCH (p)-[:EDUCATED_AT]->(e:Education)
    RETURN p,
           collect(DISTINCT s) as skills,
           collect(DISTINCT c) as companies,
           collect(DISTINCT e) as education
    """
    try:
        result = await session.run(query, keywords=request.target_keywords)
        record = await result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Convert Neo4j Record to dictionary
        record_dict = {
            "p": dict(record["p"]),
            "skills": [dict(s) for s in record["skills"]],
            "companies": [dict(c) for c in record["companies"]],
            "education": [dict(e) for e in record["education"]],
        }

        # Generate CV content based on the format
        if request.format == "markdown":
            content = _generate_markdown_cv(record_dict)
        elif request.format == "html":
            content = _generate_html_cv(record_dict)
        elif request.format == "pdf":
            raise HTTPException(
                status_code=501,
                detail="PDF format not implemented",
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid format: {request.format}. Must be one of: markdown, html, pdf",
            )

        return {"content": content, "format": request.format}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
