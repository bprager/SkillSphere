# Skill Sphere MCP

Management Control Plane (MCP) for Skill Sphere, a FastAPI-based service that implements the Model Context Protocol (MCP) to expose skills and experiences from a Neo4j graph database to LLM agents.

## Features

- Model Context Protocol (MCP) implementation
- JSON-RPC 2.0 compliant API
- Neo4j graph database integration
- Semantic search with Node2Vec embeddings
- OpenTelemetry instrumentation
- Environment-based configuration
- Health check endpoint
- Tool dispatching system

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

Start the server using one of these methods:

```bash
# Method 1: Using Python module
python -m skill_sphere_mcp.app

# Method 2: Using the entrypoint script
mcp-server
```

The API will be available at `http://localhost:8000`.

## API Usage

### MCP Protocol

The server implements the Model Context Protocol (MCP) over JSON-RPC 2.0. All requests should be sent to the `/mcp/rpc` endpoint.

Example initialize request:

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocol_version": "1.0",
    "client_info": {
      "name": "example-agent"
    }
  },
  "id": 1
}
```

### Available Methods

- `initialize` - Protocol handshake
- `resources/list` - List available resources
- `resources/get` - Get resource schema
- `search` - Semantic search
- `tool` - Dispatch tool calls

### Tool Examples

Search for skills:

```json
{
  "jsonrpc": "2.0",
  "method": "tool",
  "params": {
    "tool_name": "graph.search",
    "parameters": {
      "query": "Python developer",
      "top_k": 5
    }
  },
  "id": 1
}
```

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

## Project Structure

```text
skill_sphere_mcp/
├── api/              # API routes and handlers
├── config/           # Configuration management
├── db/              # Database connection and models
├── graph/           # Graph operations and embeddings
├── models/          # Data models and schemas
├── telemetry/       # OpenTelemetry setup
├── tools/           # Tool implementations
├── app.py           # FastAPI application setup
└── routes.py        # Legacy API routes
```

## License

MIT License
