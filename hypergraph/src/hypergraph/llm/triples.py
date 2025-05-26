"""LLM-based triple extraction from text."""

import json
from typing import List

import yaml
from langchain_ollama import ChatOllama

MARKDOWN_FENCE_COUNT = 2
MIN_PARTS_COUNT = 2


# pylint: disable=R0903
class TripleExtractorConfig:
    """Configuration for TripleExtractor."""

    def __init__(self, rel_hints, known_skills, known_tools, alias_map):
        self.rel_hints = rel_hints
        self.known_skills = known_skills
        self.known_tools = known_tools
        self.alias_map = alias_map


def clean_json(raw: str) -> str:
    """Remove markdown fences & leading prose; return substring starting at first '[' or '{'."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```", MARKDOWN_FENCE_COUNT)
        if len(parts) >= MIN_PARTS_COUNT:
            raw = parts[1]
    for i, ch in enumerate(raw):
        if ch in "[{":
            return raw[i:]
    return raw


def parse_triples(text: str) -> List[dict]:
    """Try JSON then YAML parsing of triples. Always return a list."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            result = yaml.safe_load(text)
            return result if isinstance(result, list) else []
        except yaml.YAMLError:
            return []


# pylint: disable=R0903
class TripleExtractor:
    """Extracts subject-relation-object triples from text using LLM."""

    def __init__(
        self,
        model: str,
        base_url: str,
        config: TripleExtractorConfig,
    ):
        """Initialize with LLM and extraction hints."""
        self.llm = ChatOllama(model=model, base_url=base_url)
        self.rel_hints = config.rel_hints
        self.known_skills = config.known_skills
        self.known_tools = config.known_tools
        self.alias_map = config.alias_map

    def extract(self, text: str, max_rounds: int = 3) -> List[dict]:
        """Multi-turn gleaning loop until no new triples or max rounds reached."""
        collected: List[dict] = []
        prompt_template = (
            "You are an information‑extraction assistant. Output **ONLY** valid JSON — "
            "a list of triples with keys 'subject', 'relation', 'object'.\n"
            "Use relation names from: {rels}. "
            "Prefer skill names from: {skills}. "
            "Prefer tool names from: {tools}.\n"
            "Alias map (apply before output): {aliases}.\n"
            "Already extracted triples (avoid duplicates):\n{known}\n"
            "Text to analyse:```\n{chunk}```"
        )

        for _ in range(1, max_rounds + 1):
            prompt = prompt_template.format(
                rels=", ".join(self.rel_hints),
                skills=", ".join(self.known_skills),
                tools=", ".join(self.known_tools),
                aliases=json.dumps(self.alias_map),
                known=json.dumps(collected),
                chunk=text,
            )
            resp = self.llm.invoke(prompt)
            content = str(resp.content)
            triples = parse_triples(clean_json(content))
            # Filter out ones we already have
            new = [t for t in triples if t not in collected]
            if not new:
                break
            collected.extend(new)
        return collected
