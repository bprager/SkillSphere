# Hypergraph

A hypergraph-based knowledge ingestion pipeline that processes markdown documents into a Neo4j graph database with vector embeddings.

## Features

- Document chunking and vector embeddings using Ollama
- Triple extraction using LLMs
- Neo4j graph storage with Node2Vec embeddings
- FAISS vector similarity search
- Incremental updates with document registry

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/hypergraph.git
cd hypergraph
```

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

1. Create a `.env` file with your configuration:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASS=your_password
OLLAMA_BASE_URL=http://localhost:11434
```

## Usage

1. Start Neo4j and Ollama services
2. Place your markdown documents in the configured `doc_root` directory
3. Run the ingestion pipeline:

```bash
python -m hypergraph
```

## Development

- Run tests:

```bash
pytest
```

- Format code:

```bash
black src tests
ruff check src tests
```

## License

MIT
