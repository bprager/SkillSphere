"""Main application module."""

import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.mcp_routes import router as mcp_router
from .api.routes import router as api_router
from .config.settings import get_settings
from .db.neo4j import neo4j_conn
from .telemetry.otel import setup_telemetry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown events."""
    # Setup OpenTelemetry
    tracer = setup_telemetry()
    if tracer:
        logger.info("OpenTelemetry configured successfully")
        app.state.tracer = tracer

    # Verify Neo4j connection
    if await neo4j_conn.verify_connectivity():
        logger.info("Neo4j connection verified")
    else:
        logger.error("Failed to connect to Neo4j")
        sys.exit(1)

    yield

    # Cleanup
    await neo4j_conn.close()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Skill Sphere MCP",
        description="Management Control Plane for Skill Sphere",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(mcp_router, prefix="/api/mcp")

    return app


def main() -> None:
    """Application entry point."""
    settings = get_settings()
    uvicorn.run(
        "skill_sphere_mcp.main:create_app",
        host=settings.host,
        port=settings.port,
        factory=True,
        reload=True,
    )


if __name__ == "__main__":
    main()
