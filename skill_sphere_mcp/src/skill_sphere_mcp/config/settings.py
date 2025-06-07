"""Application settings and configuration."""

import logging

from functools import lru_cache

from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


logger = logging.getLogger(__name__)


class ClientInfo(BaseModel):
    """Client information model."""

    name: str = Field(default="SkillSphere", validation_alias="MCP_CLIENT_NAME")
    version: str = Field(default="1.0.0", validation_alias="MCP_CLIENT_VERSION")
    environment: str = Field(
        default="development", validation_alias="MCP_CLIENT_ENVIRONMENT"
    )
    features: list[str] = Field(
        default_factory=lambda: [
            "cv",  # CV generation
            "search",  # Semantic search
            "matching",  # Skill matching
            "profiles",  # Profile management
            "skills",  # Skill management
            "analytics",  # Analytics and insights
            "recommendations",  # Skill recommendations
            "export",  # Data export
            "import",  # Data import
        ],
        validation_alias="MCP_CLIENT_FEATURES",
    )

    model_config = SettingsConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class Settings(BaseSettings):
    """Application settings."""

    # Server
    host: str = Field(default="0.0.0.0", validation_alias="MCP_HOST")
    port: int = Field(default=8000, validation_alias="MCP_PORT", ge=1, le=65535)
    debug: bool = Field(default=False)

    # Neo4j
    neo4j_uri: str = Field(
        default="bolt://localhost:7687", validation_alias="MCP_NEO4J_URI"
    )
    neo4j_user: str = Field(default="neo4j", validation_alias="MCP_NEO4J_USER")
    neo4j_password: str = Field(
        default="password", validation_alias="MCP_NEO4J_PASSWORD"
    )

    # OpenTelemetry
    otel_endpoint: str = Field(
        default="http://localhost:4317", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    otel_service_name: str = Field(
        default="mcp-server", validation_alias="OTEL_SERVICE_NAME"
    )

    # Client info
    client_info: ClientInfo = Field(default_factory=ClientInfo)

    # Feature flags
    enable_telemetry: bool = Field(default=True)
    enable_caching: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_prefix="SKILL_SPHERE_",
        populate_by_name=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


# Export settings instance
settings = get_settings()

__all__ = ["settings"]
