"""Shared schema definitions for MCP resources."""

from typing import Any
from typing import Dict


# Resource schema definitions
RESOURCE_SCHEMAS = {
    "nodes": {
        "type": "object",
        "description": "Collection of nodes",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "type": {"type": "string"},
        },
    },
    "relationships": {
        "type": "object",
        "description": "Collection of relationships",
        "properties": {
            "type": {"type": "string"},
            "start": {"type": "string"},
            "end": {"type": "string"},
        },
    },
    "search": {
        "type": "object",
        "description": "Search functionality",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer"},
        },
    },
}


def get_resource_schema(resource_type: str) -> Dict[str, Any]:
    """Get a resource schema by type."""
    if resource_type not in RESOURCE_SCHEMAS:
        raise ValueError(f"Invalid resource type: {resource_type}")
    return RESOURCE_SCHEMAS[resource_type]


def get_resource_schema_with_type(resource_type: str) -> Dict[str, Any]:
    """Get a resource schema with type field included."""
    schema = get_resource_schema(resource_type)
    return {
        "type": resource_type,
        "description": schema["description"],
        "properties": schema["properties"]
    }
