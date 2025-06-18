"""Application settings and configuration."""

import logging
import os

from functools import lru_cache

from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


logger = logging.getLogger(__name__)


class ClientInfo(BaseModel):
    """Client information model."""

    name: str = Field(default="SkillSphere")
    version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
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
    )
    mcp_instructions: str = Field(
        default="""You are connected to Bernd Prager's (bernd@prager.ws) skills-graph. \
This MCP server provides access to a Neo4j-powered Hypergraph-of-Thought containing enriched career records and professional experiences. \
Use `graph.search` or traverse `skills.node` to gather evidence, \
then call `skill.match_role` or `cv.generate` as appropriate. \
Prefer nodes labelled 'JOB' or 'CERTIFICATION' for hard evidence. \
If a requirement is missing, suggest relevant up-skilling. \
All context and content provided through this MCP server is specifically for Bernd Prager.""",
    )

    model_config = SettingsConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class Settings(BaseSettings):
    """Application settings."""

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = Field(default=False)

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="password")

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    otel_service_name: str = Field(default="mcp-server")
    otel_sdk_disable: bool = Field(default=False)

    # MCP Protocol Metadata
    protocol_version: str = Field(default="2025-05-16")
    service_name: str = Field(default="SkillSphere MCP")
    service_version: str = Field(default="0.2.0")

    # Client info
    client_info: ClientInfo = Field(default_factory=ClientInfo, env=None)

    # Feature flags
    enable_telemetry: bool = Field(default=True)
    enable_caching: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_prefix="SKILL_SPHERE_MCP_",
        populate_by_name=True,
        extra="ignore",
    )

    def __init__(self, **kwargs):
        logger.debug("Initializing Settings with kwargs: %s", kwargs)
        super().__init__(**kwargs)
        logger.debug("Settings initialized: %s", self)


def get_test_settings() -> Settings:
    """Get test settings."""
    client_info = ClientInfo(
        name="SkillSphere-Test",
        version="1.0.0",
        environment="test",
        features=["cv", "search", "matching"],
        mcp_instructions="Test instructions",
    )
    print("[DEBUG] get_test_settings: client_info type:", type(client_info))
    print("[DEBUG] get_test_settings: client_info:", client_info)
    settings_obj = Settings(
        host="0.0.0.0",
        port=8000,
        debug=True,
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test_password",
        otel_exporter_otlp_endpoint="http://localhost:4317",
        otel_service_name="mcp-server-test",
        otel_sdk_disable=True,
        protocol_version="2025-05-16",
        service_name="SkillSphere MCP Test",
        service_version="0.2.0",
        client_info=client_info,
        enable_telemetry=False,
        enable_caching=False,
    )
    print("[DEBUG] get_test_settings: settings_obj:", settings_obj)
    return settings_obj


@lru_cache
def get_settings() -> Settings:
    """Get application settings."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return get_test_settings()
    return Settings()


# Create a singleton instance for testing
settings = get_settings()

__all__ = ["get_settings", "get_test_settings", "settings"]
