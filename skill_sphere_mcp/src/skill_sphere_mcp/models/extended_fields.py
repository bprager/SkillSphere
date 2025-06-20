from typing import Any, Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ExtendedFields(BaseModel):
    meta: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {"generated_by": "SkillSphere 2.3"},
        description="Metadata about the model",
        alias="_meta",
    )
    title: Optional[str] = Field(default=None, description="Optional title")
    context: Optional[Any] = Field(default=None, description="Optional context")

    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
    )
