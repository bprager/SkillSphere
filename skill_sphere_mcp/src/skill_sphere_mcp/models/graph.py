"""Graph data models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Graph node model."""

    id: str
    labels: List[str]
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphRelationship(BaseModel):
    """Graph relationship model."""

    id: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    source_id: str
    target_id: str
