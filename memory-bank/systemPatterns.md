# System Patterns

## Architecture Overview

### Core Components

1. **Hypergraph Model**
   - Neo4j database for graph storage
   - Node2Vec embeddings for semantic understanding
   - Graph-of-Thought processing

2. **Data Processing Pipeline**
   - Individual file processing for optimal accuracy
   - Markdown → Graph conversion with YAML front matter
   - Gleaning loop for fact extraction
   - Graph → Markdown → PDF pipeline

3. **Local AI Processing**
   - Ollama integration
   - Local LLM operations
   - No external API dependencies

## Design Patterns

### Data Structure Optimization

- **Individual File Processing**: Each document processed independently
- **YAML Front Matter**: Structured metadata for enhanced processing
- **Template System**: Standardized formats for consistency
- **Entity ID Management**: Unique identifiers for graph relationships

### Data Flow

```mermaid
graph LR
    A[Markdown Input] --> B[YAML Processing]
    B --> C[Graph Conversion]
    C --> D[Neo4j Storage]
    D --> E[Graph Processing]
    E --> F[PDF Generation]
```

### Component Relationships

- FastAPI for API endpoints
- Neo4j for graph storage
- Node2Vec for embeddings
- Ollama for local AI processing
- Template system for data consistency

## Technical Decisions

### Data Structure

- Individual files over monolithic documents
- YAML front matter for structured metadata
- Template system for consistency
- Entity ID standardization

### Database

- Neo4j chosen for graph capabilities
- Hypergraph model for complex relationships
- Efficient querying for résumé generation

### AI Processing

- Local Ollama deployment
- Graph-of-Thought model
- Node2Vec for semantic understanding

### API Design

- RESTful endpoints
- Async processing
- Type-safe interfaces

## Testing Strategy

- 100% unit test coverage
- Integration tests for core flows
- Performance benchmarks
- Privacy compliance checks
