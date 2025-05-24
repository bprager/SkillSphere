"""Application settings and configuration."""

import logging
import sys
from functools import lru_cache

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # Server
    host: str = Field(default="0.0.0.0", validation_alias="MCP_HOST")
    port: int = Field(default=8000, validation_alias="MCP_PORT", ge=1, le=65535)

    # Neo4j
    neo4j_uri: str = Field(
        default="bolt://localhost:7687", validation_alias="MCP_NEO4J_URI"
    )
    neo4j_user: str = Field(default="neo4j", validation_alias="MCP_NEO4J_USER")
    neo4j_password: str = Field(default="neo4j", validation_alias="MCP_NEO4J_PASSWORD")

    # OpenTelemetry
    otel_endpoint: str = Field(
        default="http://localhost:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    otel_service_name: str = Field(
        default="mcp-server", validation_alias="OTEL_SERVICE_NAME"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:  # pragma: no cover
    """Get cached application settings from environment variables."""
    try:
        return Settings()  # environment variables validated here  # type: ignore
    except ValidationError as exc:
        # Fail fast with helpful message
        logger.error("Invalid configuration: %s", exc)
        sys.exit(1)
