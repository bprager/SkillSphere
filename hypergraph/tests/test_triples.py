"""Tests for hypergraph.llm.triples module."""

# pylint: disable=import-error, wrong-import-position
import sys

from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from unittest.mock import patch

from hypergraph.llm.triples import TripleExtractor
from hypergraph.llm.triples import TripleExtractorConfig
from hypergraph.llm.triples import clean_json
from hypergraph.llm.triples import parse_triples


def test_clean_json_removes_markdown_and_prose() -> None:
    """Test that clean_json removes markdown fences and leading prose."""
    # Markdown fenced JSON
    raw = """```json\n[{'subject': 'A', 'relation': 'B', 'object': 'C'}]\n```"""
    cleaned = clean_json(raw)
    assert cleaned.startswith("[")
    # Leading prose
    raw2 = 'Some intro... [{"subject": "A", "relation": "B", "object": "C"}]'
    cleaned2 = clean_json(raw2)
    assert cleaned2.startswith("[")
    # No JSON found
    raw3 = "No JSON here!"
    cleaned3 = clean_json(raw3)
    assert cleaned3 == "No JSON here!"


def test_parse_triples_json_and_yaml() -> None:
    """Test that parse_triples correctly parses JSON and YAML inputs."""
    # Valid JSON
    json_text = '[{"subject": "A", "relation": "B", "object": "C"}]'
    triples_list = parse_triples(json_text)
    assert isinstance(triples_list, list)
    assert triples_list[0]["subject"] == "A"
    # Valid YAML
    yaml_text = "- subject: A\n  relation: B\n  object: C"
    triples_list2 = parse_triples(yaml_text)
    assert isinstance(triples_list2, list)
    assert triples_list2[0]["object"] == "C"
    # Invalid input
    bad = parse_triples("not valid")
    assert bad == []


def test_triple_extractor_extract() -> None:
    """Test that TripleExtractor.extract correctly extracts triples from text using a mocked LLM."""
    # Patch ChatOllama to return a mock response
    with patch("hypergraph.llm.triples.ChatOllama") as mock_llm_class:
        mock_llm = mock_llm_class.return_value
        # Simulate LLM returning a valid triple in JSON
        mock_llm.invoke.return_value.content = '[{"subject": "A", "relation": "B", "object": "C"}]'
        config = TripleExtractorConfig(
            rel_hints=["B"], known_skills=[], known_tools=[], alias_map={}
        )
        extractor = TripleExtractor(
            model="test-model",
            base_url="http://localhost:1234",
            config=config,
        )
        result = extractor.extract("Test text", max_rounds=2)
        assert isinstance(result, list)
        assert result[0]["subject"] == "A"
        # Simulate LLM returning no new triples after first round
        mock_llm.invoke.return_value.content = "[]"
        result2 = extractor.extract("Test text", max_rounds=2)
        assert not result2
