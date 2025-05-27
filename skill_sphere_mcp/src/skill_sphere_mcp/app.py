"""MCP Server - FastAPI application setup and configuration."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from .api.mcp_routes import router as mcp_router
from .config.settings import get_settings
from .routes import router as api_router
from .telemetry.otel import setup_telemetry

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
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Setup OpenTelemetry
    tracer = setup_telemetry()
    if tracer:
        logger.info("OpenTelemetry tracing enabled")
    else:
        logger.warning("OpenTelemetry tracing disabled")

    # Startup
    logger.info("Starting MCP server")
    yield

    # Shutdown
    logger.info("Shutting down MCP server")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    mcp_server_app = FastAPI(
        title="SkillSphere MCP",
        version="0.2.0",
        lifespan=lifespan,
    )

    # Include API routes
    mcp_server_app.include_router(api_router)
    mcp_server_app.include_router(mcp_router)

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
