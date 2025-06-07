"""Graph data models."""

from typing import Any

from pydantic import BaseModel
from pydantic import Field


class GraphNode(BaseModel):
    """Graph node model."""

    id: str
    labels: list[str]
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphRelationship(BaseModel):
    """Graph relationship model."""

    id: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)
    source_id: str
    target_id: str
