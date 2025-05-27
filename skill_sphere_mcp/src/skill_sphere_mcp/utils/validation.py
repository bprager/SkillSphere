"""Validation utilities."""

from typing import Any, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def validate_parameters(parameters: dict[str, Any], model_class: type[T]) -> T:
    """Validate parameters against a Pydantic model.

    Args:
        parameters: Dictionary of parameters to validate
        model_class: Pydantic model class to validate against

    Returns:
        Validated model instance

    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        return model_class(**parameters)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {exc}"
        ) from exc
