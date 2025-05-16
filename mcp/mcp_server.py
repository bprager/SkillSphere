#!/usr/bin/env python3
"""
MCP Server – FastAPI service exposing Skills‑Graph (Neo4j) endpoints
with OpenTelemetry instrumentation and Pydantic‑powered settings.

Author: Bernd Prager
Revision: v0.2 – 2025‑05‑16

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
    python-dotenv            # optional, dev‑only
"""
from __future__ import annotations

import sys
from functools import lru_cache
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException
from neo4j import Driver, GraphDatabase
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPSpanExporter
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --------------------------------------------------------------------------- #
# Environment / settings                                                      #
# --------------------------------------------------------------------------- #

# In local development load .env first (noop in prod containers)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python‑dotenv is optional
    pass


class Settings(BaseSettings):
    # Server
    host: str = Field("0.0.0.0", env="MCP_HOST")
    port: int = Field(8000, env="MCP_PORT")

    # Neo4j
    neo4j_uri: str = Field(..., env="MCP_NEO4J_URI")
    neo4j_user: str = Field("neo4j", env="MCP_NEO4J_USER")
    neo4j_password: str = Field(..., env="MCP_NEO4J_PASSWORD")

    # OpenTelemetry
    otel_endpoint: str = Field("http://localhost:4317", env="OTEL_EXPORTER_OTLP_ENDPOINT")
    otel_service_name: str = Field("mcp-server", env="OTEL_SERVICE_NAME")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:  # pragma: no cover
    try:
        return Settings()  # environment variables validated here
    except Exception as exc:
        # Fail fast with helpful message
        sys.stderr.write(f"[fatal] Invalid configuration: {exc}\n")
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

RequestsInstrumentor().instrument()  # outbound HTTP spans

# --------------------------------------------------------------------------- #
# FastAPI                                                                     #
# --------------------------------------------------------------------------- #
app = FastAPI(title="MCP Server", version="0.2.0")
FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)

# --------------------------------------------------------------------------- #
# Neo4j Driver                                                                #
# --------------------------------------------------------------------------- #


@lru_cache(maxsize=1)
def get_neo4j_driver() -> Driver:  # pragma: no cover
    return GraphDatabase.driver(
        cfg.neo4j_uri, auth=(cfg.neo4j_user, cfg.neo4j_password)
    )


# --------------------------------------------------------------------------- #
# Pydantic DTOs                                                               #
# --------------------------------------------------------------------------- #


class Entity(BaseModel):
    id: str
    labels: List[str]
    properties: dict[str, Any]
    relationships: Optional[List[dict[str, Any]]] = None


class SearchRequest(BaseModel):
    query: str
    k: int = 10  # top‑k results


class SearchResult(BaseModel):
    entity_id: str
    score: float


# --------------------------------------------------------------------------- #
# Routes                                                                      #
# --------------------------------------------------------------------------- #


@app.get("/healthz", summary="Health check")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/entity/{entity_id}", response_model=Entity, summary="Get entity by ID")
async def get_entity(entity_id: str):
    cypher = (
        "MATCH (n) WHERE id(n) = $id "
        "OPTIONAL MATCH (n)-[r]->(m) "
        "RETURN n, collect({relType: type(r), targetId: id(m), targetLabels: labels(m)}) AS rels"
    )
    with tracer.start_as_current_span("neo4j.get_entity"):
        with get_neo4j_driver().session() as ses:
            record = ses.run(cypher, id=int(entity_id)).single()
            if not record:
                raise HTTPException(status_code=404, detail="Entity not found")
            node = record["n"]
            rels = record["rels"]
            return Entity(
                id=str(node.id), labels=list(node.labels), properties=dict(node), relationships=rels
            )


@app.post("/v1/search", response_model=list[SearchResult], summary="Semantic / graph search")
async def search(request: SearchRequest):
    # Placeholder for future vector search
    raise HTTPException(
        status_code=501,
        detail="Free‑text semantic search not implemented yet – embed the query first.",
    )


# --------------------------------------------------------------------------- #
# Entrypoint – `python mcp_server.py`                                         #
# --------------------------------------------------------------------------- #

def main() -> None:  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "mcp_server:app",
        host=cfg.host,
        port=cfg.port,
        reload=False,
    )


if __name__ == "__main__":
    main()

