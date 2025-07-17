"""Extended fields models for additional metadata."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExtendedFields(BaseModel):
    """Extended fields model for storing additional metadata."""

    meta: dict[str, Any] | None = Field(
        default=None, alias="_meta", description="Additional metadata"
    )
    title: str | None = Field(default=None, description="Optional title")
    context: Any | None = Field(default=None, description="Optional context")

    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
    )
