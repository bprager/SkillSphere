# SkillSphere AI Agent Instructions

## Project Overview

SkillSphere is a **Hypergraph-of-Thought** system that converts markdown career documents into a Neo4j knowledge graph, enriched by local LLM processing and served via MCP (Model Context Protocol). The system has two main components:

1. **Hypergraph Ingestion Pipeline** (`hypergraph/`) - Processes markdown → Neo4j + embeddings
2. **MCP Server** (`skill_sphere_mcp/`) - FastAPI server exposing graph data via MCP protocol

## Architecture Pattern: Two-Stage Processing

```
Markdown → [Hypergraph Pipeline] → Neo4j → [MCP Server] → AI Agents
```

- **Stage 1**: Batch ingestion with LLM gleaning loops (Gemma 3 12B via Ollama)
- **Stage 2**: Real-time API serving with Node2Vec embeddings for similarity search

## Critical Development Workflows

### Running the Full Stack
```bash
# Start all services (Neo4j, MCP server, monitoring)
docker-compose up -d

# Run hypergraph ingestion pipeline
cd hypergraph && source .venv/bin/activate
python -m hypergraph  # Processes ../ingestion_docs/*.md
```

### Testing Pattern
```bash
# Root level - runs both component test suites
./scripts/run_tests.sh

# Individual components
cd hypergraph && pytest
cd skill_sphere_mcp && pytest
```

### Environment Setup
- Each component has its own `.venv` and `pyproject.toml`
- Environment variables in `.env` files (see `.env.example` templates)
- Critical: `DOC_ROOT=../ingestion_docs` in hypergraph config

## Data Processing Conventions

### Document Structure (`ingestion_docs/`)
- **Content files**: `jobs/`, `certs/`, `skills/`, `extras/` → processed into graph
- **README files**: Automatically excluded from ingestion (see `hypergraph/__main__.py:111`)
- **Templates**: YAML frontmatter with `entity_id`, `competencies`, structured metadata

### Hypergraph Processing Pattern
1. **SHA-256 change detection** via SQLite registry (`doc_registry.sqlite3`)
2. **Chunking**: 1500-word windows, 200-word overlap
3. **Gleaning loop**: Up to 3 LLM passes extracting triples (`glean_max_rounds`)
4. **Graph merge**: Deterministic Cypher `MERGE` operations
5. **Node2Vec**: 128-dimensional embeddings for similarity search

## Component Integration Points

### Hypergraph → Neo4j
- Connection: `bolt://localhost:7687` (configurable via `NEO4J_URI`)
- Schema: `graph_schema.yaml` defines relationship types and prompt steering
- Output: RDF-like triples stored as labeled property graph

### MCP Server → Neo4j
- FastAPI app with MCP JSON-RPC endpoints at `/mcp`
- REST API at `/v1/` for monitoring/debugging
- OpenTelemetry tracing with Grafana/Tempo integration
- OAuth authentication for production (configurable)

### LLM Integration
- **Ollama**: Local inference server at `http://localhost:11434`
- **Embedding model**: `nomic-embed-text` for FAISS vector store
- **Chat model**: `gemma3:12b` for triple extraction

## Project-Specific Conventions

### Error Handling
- Use structured logging with OpenTelemetry traces
- MCP responses follow JSON-RPC 2.0 error format
- Database connection errors handled gracefully with retries

### Testing Strategy
- **Mock external services** (Neo4j, Ollama) in unit tests
- **Fixtures pattern**: See `hypergraph/tests/conftest.py` for database mocking
- **Coverage requirement**: 100% for core modules (enforced in CI)

### Code Organization
- **Dataclass patterns**: See `hypergraph/__main__.py` for configuration objects
- **Dependency injection**: FastAPI dependencies in `skill_sphere_mcp/src/*/deps.py`
- **Middleware stack**: Authentication, CORS, Matomo tracking, OpenTelemetry

## Key Files to Understand

- `docs/architecture.md` - Complete system design and data flows
- `hypergraph/src/hypergraph/__main__.py` - Core ingestion pipeline logic
- `skill_sphere_mcp/src/skill_sphere_mcp/app.py` - FastAPI application setup
- `ingestion_docs/skills/` - Template examples for structured data input
- `.cursorrules` - Existing code style and pattern preferences

## Debugging Common Issues

- **Ingestion not updating**: Check SHA-256 hashes in `doc_registry.sqlite3`
- **MCP connection errors**: Verify Neo4j is running and `NEO4J_URI` is correct
- **Empty search results**: Ensure Node2Vec embeddings are computed post-ingestion
- **Test failures**: Activate correct virtual environment per component
