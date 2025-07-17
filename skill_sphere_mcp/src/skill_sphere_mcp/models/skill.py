"""Skill model definition."""

from pydantic import BaseModel, Field


class Skill(BaseModel):
    """Skill model."""

    name: str = Field(..., description="Name of the skill")
    description: str | None = Field(None, description="Description of the skill")
    category: str | None = Field(None, description="Category of the skill")
    level: int | None = Field(None, description="Skill level (1-5)", ge=1, le=5)
