from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter

router = APIRouter()

class ElicitationRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool for elicitation")

from pydantic import BaseModel, Field
from pydantic import ConfigDict

class ElicitationResponse(BaseModel):
    prompt: str = Field(..., description="Prompt for the user")
    elicitation_schema: Dict[str, Any] = Field(..., description="JSON schema for the elicitation")
    defaults: Optional[Dict[str, Any]] = Field(None, description="Optional default values")

    model_config = ConfigDict(
        validate_by_name=True
    )

@router.post("/elicitation/request", response_model=ElicitationResponse)
async def elicitation_request(request: ElicitationRequest) -> ElicitationResponse:
    # For demonstration, return a static prompt and schema
    prompt = f"Please provide input for tool: {request.tool_name}"
    elicitation_schema = {
        "type": "object",
        "properties": {
            "example_param": {"type": "string", "description": "An example parameter"}
        },
        "required": ["example_param"]
    }
    defaults = {"example_param": "default value"}

    return ElicitationResponse(prompt=prompt, elicitation_schema=elicitation_schema, defaults=defaults)
