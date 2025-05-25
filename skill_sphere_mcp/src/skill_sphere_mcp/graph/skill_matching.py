"""Skill matching service implementation."""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
from neo4j import AsyncSession
from sklearn.metrics.pairwise import cosine_similarity

from .embeddings import embeddings
from .node2vec import Node2Vec

logger = logging.getLogger(__name__)


@dataclass
class SkillMatch:
    """Represents a matched skill with evidence."""

    skill_name: str
    match_score: float
    evidence: list[dict[str, Any]]
    experience_years: float


@dataclass
class MatchResult:
    """Represents the result of a skill matching operation."""

    overall_score: float
    matching_skills: list[SkillMatch]
    skill_gaps: list[str]
    supporting_nodes: list[dict[str, Any]]


class SkillMatchingService:
    """Service for matching skills against role requirements."""

    def __init__(self, similarity_threshold: float = 0.7):
        """Initialize the skill matching service.

        Args:
            similarity_threshold: Minimum similarity score to consider a match
        """
        self.similarity_threshold = similarity_threshold
        self._node2vec = Node2Vec()

    async def match_role(
        self,
        session: AsyncSession,
        required_skills: list[dict[str, Any]],
        candidate_skills: list[dict[str, Any]],
    ) -> MatchResult:
        """Match candidate skills against role requirements.

        Args:
            session: Neo4j session
            required_skills: List of required skills with experience requirements
            candidate_skills: List of candidate's skills with experience

        Returns:
            MatchResult containing match scores, gaps, and evidence
        """
        # Handle empty required skills immediately
        if not required_skills:
            return MatchResult(
                overall_score=0.0,
                matching_skills=[],
                skill_gaps=[],
                supporting_nodes=[],
            )
        # Load embeddings if not already loaded
        if not embeddings.model:
            await embeddings.load_embeddings(session)

        # Initialize result components
        matching_skills: list[SkillMatch] = []
        skill_gaps: list[str] = []
        supporting_nodes: list[dict[str, Any]] = []

        # Track overall score components
        skill_scores: list[float] = []
        experience_scores: list[float] = []

        # Match each required skill
        for req_skill in required_skills:
            req_name = req_skill["name"]
            req_years = req_skill.get("years", 0)

            # Find best matching candidate skill
            best_match = await self._find_best_match(
                session, req_name, candidate_skills, req_years
            )

            if best_match:
                matching_skills.append(best_match)
                skill_scores.append(best_match.match_score)
                experience_scores.append(
                    min(best_match.experience_years / req_years, 1.0)
                    if req_years > 0
                    else 1.0
                )
                supporting_nodes.extend(best_match.evidence)
            else:
                skill_gaps.append(req_name)
                skill_scores.append(0.0)
                experience_scores.append(0.0)

        # Calculate overall score (60% skill match, 40% experience)
        overall_score = 0.6 * (sum(skill_scores) / len(skill_scores)) + 0.4 * (
            sum(experience_scores) / len(experience_scores)
        )

        return MatchResult(
            overall_score=overall_score,
            matching_skills=matching_skills,
            skill_gaps=skill_gaps,
            supporting_nodes=supporting_nodes,
        )

    async def _find_best_match(
        self,
        session: AsyncSession,
        req_skill: str,
        candidate_skills: list[dict[str, Any]],
        req_years: float | None = None,
    ) -> SkillMatch | None:
        """Find the best matching skill from candidate's skills.

        Args:
            session: Neo4j session
            req_skill: Required skill name
            candidate_skills: List of candidate's skills
            req_years: Optional required years of experience

        Returns:
            Best matching skill with evidence, or None if no match found
        """
        best_score = 0.0
        best_match: SkillMatch | None = None

        # Get required skill embedding
        req_embedding = await self._get_skill_embedding(session, req_skill)
        if req_embedding is None:
            return None

        # Compare with each candidate skill
        for candidate in candidate_skills:
            candidate_embedding = await self._get_skill_embedding(
                session, candidate["name"]
            )
            if candidate_embedding is None:
                continue

            # Calculate semantic similarity
            similarity = cosine_similarity(
                req_embedding.reshape(1, -1), candidate_embedding.reshape(1, -1)
            )[0][0]

            if similarity >= self.similarity_threshold:
                # Gather evidence for the match
                evidence = await self._gather_evidence(
                    session, req_skill, candidate["name"]
                )

                # Adjust score based on experience if required
                candidate_years = candidate.get("years", 0)
                if req_years is not None and req_years > 0:
                    experience_ratio = min(candidate_years / req_years, 1.0)
                    similarity = similarity * 0.7 + experience_ratio * 0.3

                match = SkillMatch(
                    skill_name=candidate["name"],
                    match_score=similarity,
                    evidence=evidence,
                    experience_years=candidate_years,
                )

                if similarity > best_score:
                    best_score = similarity
                    best_match = match

        return best_match

    async def _get_skill_embedding(
        self, session: AsyncSession, skill_name: str
    ) -> np.ndarray | None:
        """Get embedding for a skill node.

        Args:
            session: Neo4j session
            skill_name: Name of the skill

        Returns:
            Skill embedding vector or None if not found
        """
        # Query to find skill node
        query = """
        MATCH (s:Skill {name: $name})
        RETURN id(s) as node_id
        """
        result = await session.run(query, name=skill_name)
        record = await result.single()

        if not record:
            return None

        node_id = str(record["node_id"])
        return embeddings.get_embedding(node_id)

    async def _gather_evidence(
        self, session: AsyncSession, req_skill: str, candidate_skill: str
    ) -> list[dict[str, Any]]:
        """Gather evidence supporting the skill match.

        Args:
            session: Neo4j session
            req_skill: Required skill name
            candidate_skill: Candidate skill name

        Returns:
            List of evidence nodes and relationships
        """
        query = """
        MATCH (s1:Skill {name: $req_skill})
        MATCH (s2:Skill {name: $candidate_skill})
        MATCH path = shortestPath((s1)-[*..3]-(s2))
        RETURN path
        """
        result = await session.run(
            query, req_skill=req_skill, candidate_skill=candidate_skill
        )
        record = await result.single()

        if not record:
            return []

        # Extract nodes and relationships from the path
        evidence = []
        for node in record["path"].nodes:
            evidence.append(
                {
                    "type": "node",
                    "labels": list(node.labels),
                    "properties": dict(node),
                }
            )
        for rel in record["path"].relationships:
            evidence.append(
                {
                    "type": "relationship",
                    "rel_type": rel.type,
                    "properties": dict(rel),
                }
            )

        return evidence


# Global service instance
skill_matching = SkillMatchingService()
