"""MCP Server - FastAPI application setup and configuration."""

import logging
import os

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .api.mcp_routes import router as mcp_router
from .api.routes import router as metrics_router
from .config.settings import get_settings
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
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()

    # Set up OpenTelemetry if enabled
    if settings.enable_telemetry:
        try:
            # Set up the tracer provider
            resource = Resource.create({"service.name": settings.otel_service_name})
            provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(provider)

            # Set up the OTLP exporter
            otlp_exporter = OTLPSpanExporter(endpoint=settings.otel_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            provider.add_span_processor(span_processor)

            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(fastapi_app)

            logger.info("OpenTelemetry instrumentation enabled")
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry: %s", e)
            logger.warning("Continuing without telemetry")

    # Startup
    logger.info("Starting MCP server")
    yield

    # Shutdown
    logger.info("Shutting down MCP server")

    # Cleanup
    if settings.enable_telemetry:
        try:
            provider = trace.get_tracer_provider()
            provider.force_flush()
            logger.info("OpenTelemetry cleanup completed")
        except Exception as e:
            logger.error("Error during OpenTelemetry cleanup: %s", e)


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
    mcp_server_app.include_router(api_router)  # /v1 routes
    mcp_server_app.include_router(mcp_router)  # /mcp routes
    mcp_server_app.include_router(metrics_router)  # /metrics and other API routes

    # Mount static files at /static for all static assets
    mcp_server_app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Add a route for the root path to serve index.html
    @mcp_server_app.get("/")
    async def root():
        return FileResponse(os.path.join(static_dir, "index.html"))

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
