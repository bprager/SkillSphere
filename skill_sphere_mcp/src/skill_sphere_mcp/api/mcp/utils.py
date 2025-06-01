"""Utility functions for the MCP API."""

from typing import Any

from fastapi import HTTPException

from ...config.settings import get_settings
from ...models.graph import GraphNode, GraphRelationship
from ..models import InitializeResponse


def get_initialize_response() -> InitializeResponse:
    """Get the initialization response."""
    settings = get_settings()
    client_info = dict(settings.client_info)
    return InitializeResponse(
        protocol_version="1.0",
        capabilities={
            "semantic_search": True,
            "graph_query": True,
            "tool_dispatch": True,
            "features": client_info["features"],
        },
        instructions=f"Public access enabled. Environment: {client_info['environment']}",
    )


def get_initialize_response_dict() -> dict[str, Any]:
    """Get the initialization response as a dictionary.

    Returns:
        Dictionary containing protocol version, capabilities, and instructions
    """
    response = get_initialize_response()
    return {
        "protocol_version": response.protocol_version,
        "capabilities": response.capabilities,
        "instructions": response.instructions,
    }


async def get_resource(resource: str) -> dict[str, Any]:
    """Get resource information."""
    resources = {
        "nodes": {
            "type": "collection",
            "schema": GraphNode.model_json_schema(),
        },
        "relationships": {
            "type": "collection",
            "schema": GraphRelationship.model_json_schema(),
        },
        "search": {
            "type": "action",
            "schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
        },
        "skill": {
            "type": "collection",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["id", "name"],
            },
        },
        "skills.node": {
            "type": "collection",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["id", "name"],
            },
        },
        "skills.relation": {
            "type": "collection",
            "schema": {
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "target_id": {"type": "string"},
                    "type": {"type": "string"},
                    "weight": {"type": "number"},
                },
                "required": ["source_id", "target_id", "type"],
            },
        },
        "profiles.detail": {
            "type": "collection",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "years_experience": {"type": "number"},
                            },
                        },
                    },
                },
                "required": ["id", "name"],
            },
        },
    }

    if resource not in resources:
        raise HTTPException(
            status_code=400, detail=f"Invalid resource type: {resource}"
        )
    return resources[resource]
