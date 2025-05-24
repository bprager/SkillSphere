<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to the SkillSphere MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Codebase reorganization for better maintainability
  - Separated routes into dedicated `routes.py` module
  - Streamlined `main.py` as application entry point
  - Enhanced `mcp_server.py` for core configuration
- Semantic search implementation using Sentence Transformers
  - Integration with all-MiniLM-L6-v2 model
  - Cosine similarity search for graph nodes
  - Efficient vector operations using numpy
- OpenTelemetry tracing for search operations
  - Performance monitoring
  - Error tracking
  - Request tracing
- Error handling for missing dependencies
  - Graceful fallback for missing sentence-transformers
  - Clear error messages
  - Proper cleanup
- Enhanced test coverage
  - Comprehensive unit tests for Neo4j connection
  - Async test patterns with pytest-asyncio
  - Mock implementations for external dependencies
- Improved Neo4j connection management
  - Async session handling
  - Proper resource cleanup
  - Connection pooling support

### Changed

- Reorganized application structure
  - Moved route handlers to dedicated module
  - Simplified main application entry point
  - Enhanced core configuration management
- Updated architecture documentation
  - Added semantic search details
  - Enhanced component descriptions
  - Improved future improvements section
- Enhanced search endpoint
  - Better error handling
  - Improved type safety
  - More efficient vector operations
- Improved type annotations
  - Better mypy compliance
  - Stricter type checking
  - Enhanced code quality
- Refactored Neo4j connection handling
  - Moved to dedicated connection module
  - Improved async patterns
  - Better error handling

### Fixed

- Type checking issues in search implementation
  - Proper return type annotations
  - Fixed Any type usage
  - Added type ignores where necessary
- Error handling for missing sentence-transformers package
  - Graceful degradation
  - Clear error messages
  - Proper cleanup
- Neo4j session management
  - Proper session cleanup
  - Connection pooling
  - Error handling
- Application lifecycle management
  - Proper startup/shutdown handling
  - Improved error handling during initialization
  - Better resource cleanup
- Test suite improvements
  - Fixed async test patterns
  - Improved mock implementations
  - Better test isolation

### Security

- Enhanced PAT token validation
- Improved error message security
- Added input sanitization
- Read-only Neo4j access enforcement

### Performance

- Optimized vector operations
- Improved connection management
- Enhanced error handling
- Better async patterns

### TODO

- [ ] Add Redis-based caching for frequently used embeddings
- [ ] Implement filtering by node type and properties
- [ ] Add comprehensive tests for semantic search functionality
- [ ] Support hybrid search (semantic + keyword)
- [ ] Add relevance feedback mechanism
- [ ] Fix remaining type checking issues in main.py
- [ ] Add proper return type annotations for async functions
- [ ] Implement proper FastAPI lifespan management
- [ ] Add JSON-RPC endpoint for MCP compliance
- [ ] Implement JSON Schema validation for tool calls
- [ ] Add contract tests for schema drift
- [ ] Implement PII masking in OpenTelemetry traces
- [ ] Add rate limiting
- [ ] Create comprehensive API documentation
- [ ] Add Docker/Kubernetes deployment support

## [0.2.0] - 2025-05-16

### Added

- Initial MCP server implementation
  - FastAPI-based REST API
  - MCP protocol compliance
  - Basic routing
- Neo4j integration
  - Async connection management
  - Basic CRUD operations
  - Error handling
- OpenTelemetry instrumentation
  - Request tracing
  - Performance monitoring
  - Error tracking
- PAT authentication
  - Token generation
  - Validation
  - Expiration
- Basic health check endpoints
  - Liveness probe
  - Readiness probe
  - Status endpoint

### Changed

- Updated project structure
  - Modular organization
  - Clear separation of concerns
  - Better maintainability
- Enhanced documentation
  - API documentation
  - Architecture overview
  - Development guidelines

### Fixed

- Various type checking issues
  - Added missing type hints
  - Fixed incorrect types
  - Improved type safety
- Connection management improvements
  - Better error handling
  - Proper cleanup
  - Connection pooling

### Security

- Initial PAT implementation
- Basic input validation
- Error message sanitization

### Performance

- Initial async implementation
- Basic connection pooling
- Simple caching
