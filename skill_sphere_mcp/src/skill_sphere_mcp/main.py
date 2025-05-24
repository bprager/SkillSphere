"""Application entry point for the MCP server."""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from skill_sphere_mcp.mcp_server import app, cfg, get_neo4j_driver, setup_telemetry
from skill_sphere_mcp.routes import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting up MCP server...")

    # Initialize OpenTelemetry
    tracer = setup_telemetry()
    if tracer:
        app.state.tracer = tracer

    # Verify Neo4j connectivity
    if not await get_neo4j_driver().verify_connectivity():
        logger.error("Failed to connect to Neo4j")
        raise RuntimeError("Neo4j connection failed")

    # Include routes
    app.include_router(router)

    yield

    # Shutdown
    logger.info("Shutting down MCP server...")
    await get_neo4j_driver().close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app.lifespan = lifespan
    return app


def main() -> None:
    """Run the FastAPI server with uvicorn."""
    logger.info("Starting MCP server on %s:%d", cfg.host, cfg.port)
    uvicorn.run(
        "skill_sphere_mcp.main:create_app",
        host=cfg.host,
        port=cfg.port,
        factory=True,
        reload=True,
    )


if __name__ == "__main__":
    main()
