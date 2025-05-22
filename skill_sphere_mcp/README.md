# Skill Sphere MCP

Management Control Plane (MCP) for Skill Sphere, a FastAPI-based service that manages skills and experiences in a Neo4j graph database.

## Features

- FastAPI-based REST API
- Neo4j graph database integration
- OpenTelemetry instrumentation
- Environment-based configuration
- Health check endpoint
- Skills management endpoints

## Prerequisites

- Python 3.9 or higher
- Neo4j database
- OpenTelemetry collector (optional)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/skill-sphere-mcp.git
cd skill-sphere-mcp
```

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. Install dependencies:

```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_NEO4J_URI=bolt://localhost:7687
MCP_NEO4J_USER=neo4j
MCP_NEO4J_PASSWORD=your_password
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=mcp-server
```

## Running the Application

Start the server:

```bash
python -m skill_sphere_mcp.main
```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `GET /api/v1/health` - Health check endpoint
- `GET /api/v1/skills` - List all skills
- `POST /api/v1/skills` - Create a new skill

## Development

1. Install development dependencies:

```bash
pip install -e ".[dev]"
```

1. Run tests:

```bash
pytest
```

1. Run linting:

```bash
ruff check .
```

## License

MIT License
