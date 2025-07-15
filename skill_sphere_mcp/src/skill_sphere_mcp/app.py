"""MCP Server - FastAPI application setup and configuration."""

import logging
import os

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn

from fastapi import Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from neo4j import AsyncSession
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .api.mcp import router as elicitation_router
from .api.mcp.routes import explain_match_endpoint
from .api.mcp.routes import graph_search_endpoint
from .api.mcp.routes import match_role_direct_endpoint
from .api.mcp.routes import router as mcp_router
from .api.rest import router as rest_router
from .api.routes import router as metrics_router
from .auth.oauth import OAUTH_AVAILABLE
from .auth.oauth import validate_access_token
from .config.settings import get_settings
from .db.deps import get_db_session
from .middleware.matomo_tracking import MatomoTrackingMiddleware
from .routes import router as api_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# In local development load .env first (noop in prod containers)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional
    pass


@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    # Startup
    logger.info("Starting MCP server")
    yield
    # Shutdown
    logger.info("Shutting down MCP server")
    # Cleanup
    if settings.enable_telemetry:
        try:
            provider = trace.get_tracer_provider()
            if hasattr(provider, 'force_flush'):
                provider.force_flush()
            logger.info("OpenTelemetry cleanup completed")
        except Exception as exc:
            logger.error("Shutdown error: %s", exc)
            raise


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    mcp_server_app = FastAPI(
        title="SkillSphere MCP",
        version="0.2.0",
        lifespan=lifespan,
        description="""Model Context Protocol (MCP) server for SkillSphere.

        This server implements the MCP standard using JSON-RPC 2.0. All MCP operations
        should be performed through the `/mcp/rpc` endpoint using JSON-RPC requests.

        Example initialize request:
        ```json
        {
            "jsonrpc": "2.0",
            "method": "mcp.initialize",
            "params": {},
            "id": 1
        }
        ```

        The server also provides some REST endpoints for health checks and resource
        information, but all MCP operations should use the RPC endpoint.
        """,
    )

    # OpenTelemetry setup (moved from lifespan)
    settings = get_settings()
    if settings.enable_telemetry:
        try:
            resource = Resource.create({"service.name": settings.otel_service_name})
            provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(provider)
            otlp_exporter = OTLPSpanExporter(endpoint=settings.otel_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            provider.add_span_processor(span_processor)
            FastAPIInstrumentor.instrument_app(mcp_server_app)
            logger.info("OpenTelemetry instrumentation enabled")
        except Exception as exc:
            logger.error("Startup error: %s", exc)
            # Do not raise here to allow app creation in tests

    # Configure CORS
    mcp_server_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Get the static directory path
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

    # Include API routes first
    if OAUTH_AVAILABLE and get_settings().enable_oauth:
        mcp_server_app.include_router(api_router, dependencies=[Depends(validate_access_token)])  # /v1 routes with OAuth
    else:
        mcp_server_app.include_router(api_router)  # /v1 routes without OAuth

    mcp_server_app.include_router(rest_router, prefix="/v1", tags=["rest"])  # /v1/healthz endpoint
    mcp_server_app.include_router(mcp_router, prefix="/mcp", tags=["mcp"])
    mcp_server_app.include_router(metrics_router)  # /metrics and other API routes
    mcp_server_app.include_router(elicitation_router)  # /elicitation routes

    # Add Matomo tracking middleware
    mcp_server_app.add_middleware(MatomoTrackingMiddleware)

    # Mount static files at /static for all static assets
    mcp_server_app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Mount .well-known for OAuth discovery document
    well_known_dir = os.path.join(static_dir, ".well-known")
    mcp_server_app.mount("/.well-known", StaticFiles(directory=well_known_dir), name="well-known")

    # Add a route for the root path to serve index.html
    @mcp_server_app.get("/")
    async def root() -> FileResponse:
        """Serve the root page."""
        return FileResponse(os.path.join(static_dir, "index.html"))

    # Add direct tool endpoints for testing
    @mcp_server_app.post("/match_role", tags=["tools"])
    async def match_role_root(
        request: dict,
        session: AsyncSession = Depends(get_db_session)
    ) -> dict[str, Any]:
        """Match role endpoint at root level."""
        return await match_role_direct_endpoint(request, session)

    @mcp_server_app.post("/explain_match", tags=["tools"])
    async def explain_match_root(
        request: dict,
        session: AsyncSession = Depends(get_db_session)
    ) -> dict[str, Any]:
        """Explain match endpoint at root level."""
        return await explain_match_endpoint(request, session)

    @mcp_server_app.post("/graph_search", tags=["tools"])
    async def graph_search_root(
        request: dict,
        session: AsyncSession = Depends(get_db_session)
    ) -> dict[str, Any]:
        """Graph search endpoint at root level."""
        return await graph_search_endpoint(request, session)

    return mcp_server_app


app = create_app()


def main() -> None:  # pragma: no cover
    """Run the FastAPI server with uvicorn."""
    cfg = get_settings()
    logger.info("Starting MCP server on %s:%d", cfg.host, cfg.port)
    uvicorn.run(
        "skill_sphere_mcp.app:create_app",
        host=cfg.host,
        port=cfg.port,
        reload=False,
        factory=True,
    )


if __name__ == "__main__":
    main()
