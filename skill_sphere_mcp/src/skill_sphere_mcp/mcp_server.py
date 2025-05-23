#!/usr/bin/env python3
"""
MCP Server - FastAPI service exposing Skills-Graph (Neo4j) endpoints
with OpenTelemetry instrumentation and Pydantic-powered settings.

Author: Bernd Prager
Revision: v0.2 - 2025-05-16

Configuration is provided via environment variables **or** a `.env`
file (loaded automatically in development).  See the `Settings`
class below for full list and defaults.

Dependencies (add to requirements.txt / pyproject.toml):
    fastapi
    uvicorn[standard]
    neo4j>=5
    pydantic>=2
    pydantic-settings>=2
    opentelemetry-api
    opentelemetry-sdk
    opentelemetry-exporter-otlp
    opentelemetry-instrumentation-fastapi
    opentelemetry-instrumentation-requests
    python-dotenv            # optional, dev-only
"""
from __future__ import annotations

import logging
import sys
from functools import lru_cache
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from neo4j import Driver, GraphDatabase
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

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

# --------------------------------------------------------------------------- #
# Environment / settings                                                      #
# --------------------------------------------------------------------------- #

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

# --------------------------------------------------------------------------- #
# Neo4j Driver                                                                #
# --------------------------------------------------------------------------- #


@lru_cache(maxsize=1)
def get_neo4j_driver() -> Driver:  # pragma: no cover
    """Get cached Neo4j driver instance."""
    return GraphDatabase.driver(
        cfg.neo4j_uri, auth=(cfg.neo4j_user, cfg.neo4j_password)
    )


# --------------------------------------------------------------------------- #
# Pydantic DTOs                                                               #
# --------------------------------------------------------------------------- #


class Entity(BaseModel):
    """Graph entity with ID, labels, properties and optional relationships."""

    id: str
    labels: list[str]
    properties: dict[str, Any]
    relationships: list[dict[str, Any]] | None = None


class SearchRequest(BaseModel):
    """Search request with query string and optional result limit."""

    query: str
    k: int = 10  # top-k results


class SearchResult(BaseModel):
    """Search result with entity ID and relevance score."""

    entity_id: str
    score: float


# --------------------------------------------------------------------------- #
# Routes                                                                      #
# --------------------------------------------------------------------------- #


@app.get("/healthz", summary="Health check")
async def health_check() -> dict[str, str]:
    """Return service health status."""
    logger.debug("Health check requested")
    return {"status": "ok"}


@app.get("/v1/entity/{entity_id}", response_model=Entity, summary="Get entity by ID")
async def get_entity(entity_id: int) -> Entity:
    """Get a graph entity by its ID, including its relationships."""
    logger.info("Fetching entity with ID: %d", entity_id)
    cypher = (
        "MATCH (n) WHERE id(n) = $id "
        "OPTIONAL MATCH (n)-[r]->(m) "
        "RETURN n, collect({"
        "    relType: type(r), "
        "    targetId: id(m), "
        "    targetLabels: labels(m)"
        "}) AS rels"
    )
    with tracer.start_as_current_span("neo4j.get_entity"):
        with get_neo4j_driver().session() as ses:
            record = ses.run(cypher, id=entity_id).single()
            if not record:
                logger.warning("Entity not found: %d", entity_id)
                raise HTTPException(status_code=404, detail="Entity not found")
            node = record["n"]
            rels = record["rels"]
            logger.debug("Found entity with %d relationships", len(rels))
            return Entity(
                id=str(node.id),
                labels=list(node.labels),
                properties=dict(node),
                relationships=rels,
            )


@app.post(
    "/v1/search", response_model=list[SearchResult], summary="Semantic / graph search"
)
async def search(request: SearchRequest) -> list[SearchResult]:
    """Search for entities using semantic or graph-based queries."""
    logger.info("Search request: %s (k=%d)", request.query, request.k)
    # Placeholder for future vector search
    logger.warning("Semantic search not implemented yet")
    raise HTTPException(
        status_code=501,
        detail="Free-text semantic search not implemented yet - embed the query first.",
    )


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
