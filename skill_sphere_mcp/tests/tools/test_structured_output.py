from unittest.mock import AsyncMock

import pytest

from skill_sphere_mcp.tools.dispatcher import dispatch_tool


@pytest.mark.asyncio
async def test_dispatch_tool_structured_output_match_role() -> None:
    parameters = {
        "required_skills": ["Python", "FastAPI"],
        "years_experience": {"Python": 3, "FastAPI": 2},
    }
    session = AsyncMock()
    result = await dispatch_tool(
        "skill.match_role", parameters, session, structured_output=True
    )
    assert "structured_result" in result
    structured = result["structured_result"]
    assert isinstance(structured["match_score"], float)
    assert isinstance(structured["skill_gaps"], list)
    assert isinstance(structured["matching_skills"], list)


@pytest.mark.asyncio
async def test_dispatch_tool_structured_output_explain_match() -> None:
    parameters = {
        "skill_id": "skill123",
        "role_requirement": "Senior Developer",
    }
    session = AsyncMock()
    # Mock session.run to return a record with expected data
    mock_record = AsyncMock()
    mock_record.single.return_value = {
        "s": {"name": "Python"},
        "projects": [{"name": "Project A"}],
        "certifications": [{"name": "Cert A"}],
    }
    session.run.return_value = mock_record
    result = await dispatch_tool(
        "skill.explain_match", parameters, session, structured_output=True
    )
    assert "structured_result" in result
    structured = result["structured_result"]
    assert "explanation" in structured
    assert isinstance(structured["evidence"], list)


@pytest.mark.asyncio
async def test_dispatch_tool_structured_output_graph_search() -> None:
    parameters = {
        "query": "Python",
        "top_k": 5,
    }
    session = AsyncMock()
    # Mock session.run to return records
    mock_record = AsyncMock()
    mock_record.all.return_value = [{"n": {"name": "Python Node"}}]
    session.run.return_value = mock_record
    result = await dispatch_tool(
        "graph.search", parameters, session, structured_output=True
    )
    assert "structured_result" in result
    structured = result["structured_result"]
    assert isinstance(structured["results"], list)
    assert structured["query"] == "Python"
    expected_top_k = 5
    assert structured["top_k"] == expected_top_k
