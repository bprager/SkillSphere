"""Parameter validation utilities."""

from typing import TypeVar, cast

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def validate_parameters(parameters: dict, model_class: type[T]) -> T:
    """Validate parameters against a Pydantic model.

    Args:
        parameters: Parameters to validate
        model_class: Pydantic model class to validate against

    Returns:
        Validated parameters as model instance

    Raises:
        ValueError: If validation fails
    """
    try:
        return cast(T, model_class(**parameters))
    except ValidationError as e:
        raise ValueError(str(e)) from e
