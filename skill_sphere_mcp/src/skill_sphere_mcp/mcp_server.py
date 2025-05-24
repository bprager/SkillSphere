"""MCP Server - FastAPI service exposing Skills-Graph (Neo4j) endpoints."""

import logging
import sys
from functools import lru_cache

import uvicorn
from fastapi import FastAPI
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from skill_sphere_mcp.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Optional OpenTelemetry instrumentation
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    HAS_OTEL_INSTRUMENTATION = True
except ImportError:
    HAS_OTEL_INSTRUMENTATION = False
    logger.warning("OpenTelemetry instrumentation packages not installed")

# In local development load .env first (noop in prod containers)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional
    pass


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # Server
    host: str = Field(default="0.0.0.0", validation_alias="MCP_HOST")
    port: int = Field(default=8000, validation_alias="MCP_PORT")

    # Neo4j
    neo4j_uri: str = Field(default=..., validation_alias="MCP_NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", validation_alias="MCP_NEO4J_USER")
    neo4j_password: str = Field(default=..., validation_alias="MCP_NEO4J_PASSWORD")

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
        return Settings()  # environment variables validated here
    except ValidationError as exc:
        # Fail fast with helpful message
        logger.error("Invalid configuration: %s", exc)
        sys.exit(1)


cfg = get_settings()

# --------------------------------------------------------------------------- #
# OpenTelemetry                                                               #
# --------------------------------------------------------------------------- #
resource = Resource.create({"service.name": cfg.otel_service_name})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint=cfg.otel_endpoint, insecure=True)
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

if HAS_OTEL_INSTRUMENTATION:
    RequestsInstrumentor().instrument()  # outbound HTTP spans

# --------------------------------------------------------------------------- #
# FastAPI                                                                     #
# --------------------------------------------------------------------------- #
app = FastAPI(title="MCP Server", version="0.2.0")
if HAS_OTEL_INSTRUMENTATION:
    FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)

# Include API routes
app.include_router(api_router)


# --------------------------------------------------------------------------- #
# Entrypoint - `python mcp_server.py`                                         #
# --------------------------------------------------------------------------- #
def main() -> None:  # pragma: no cover
    """Run the FastAPI server with uvicorn."""
    logger.info("Starting MCP server on %s:%d", cfg.host, cfg.port)
    uvicorn.run(
        "mcp_server:app",
        host=cfg.host,
        port=cfg.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
