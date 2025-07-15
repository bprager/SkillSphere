"""Extended fields models for additional metadata."""

from typing import Any
from typing import Dict
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ExtendedFields(BaseModel):
    """Extended fields model for storing additional metadata."""

    meta: Optional[Dict[str, Any]] = Field(
        default=None, alias="_meta", description="Additional metadata"
    )
    title: Optional[str] = Field(default=None, description="Optional title")
    context: Optional[Any] = Field(default=None, description="Optional context")

    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
    )
