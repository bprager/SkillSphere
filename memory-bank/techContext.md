# Technical Context

## Technology Stack

### Core Technologies

- **MCP (Model Context Protocol)** implementation
- **Python 3.10+** with modern type hints
- **FastAPI** for API framework
- **Neo4j** for hypergraph storage
- **Node2Vec** for semantic embeddings
- **Ollama** for local AI processing
- **YAML** for structured metadata
- **Markdown** processing with front matter
- **PDF** generation for résumé output

### Data Processing Technologies

- **YAML Front Matter**: Structured metadata for enhanced processing
- **SHA-256 Hashing**: Change detection for incremental processing
- **FAISS**: Vector storage for hybrid search
- **Template System**: Standardized formats for consistency

### Development Tools

- **Black** for code formatting
- **MyPy** for type checking
- **Pytest** for testing
- **Coverage** for test coverage
- **Ruff** for linting

## Development Setup

### Requirements

- Python 3.10 or higher
- Neo4j database
- Ollama installation
- Virtual environment

### Dependencies

Key dependencies from pyproject.toml:

- FastAPI for API framework
- Neo4j for graph database
- Node2Vec for embeddings
- LangChain for AI processing
- Pydantic for data validation
- PyYAML for front matter processing

### Development Environment

- Virtual environment management
- Code formatting and linting
- Type checking
- Test coverage reporting

## Technical Constraints

### Performance

- Individual file processing for optimal accuracy
- Graph query optimization
- PDF generation efficiency
- Change detection through SHA-256 hashing

### Security

- Local data processing
- No external API keys
- Secure data handling

### Compatibility

- Python 3.10+ requirement
- Neo4j version compatibility
- Ollama version requirements

## Deployment

- Docker support with docker-compose
- Local deployment configuration
- Development environment setup
- Production configuration
