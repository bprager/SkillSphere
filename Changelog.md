<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## TODO

### Core Components

- [ ] Implement Redis-based caching for search results
- [ ] Add hybrid search support (semantic + keyword)
- [ ] Implement result pagination for search endpoints
- [ ] Add relationship traversal and path finding capabilities
- [ ] Implement graph analytics features
- [ ] Add schema validation for graph data
- [ ] Optimize embedding generation and persistence
- [ ] Implement parallel walk generation for Node2Vec
- [ ] Add custom sampling strategies for graph embeddings

### Infrastructure

- [ ] Create Docker-based deployment configuration
- [ ] Add Kubernetes deployment manifests
- [ ] Implement health check endpoints
- [ ] Set up monitoring and alerting
- [ ] Add rate limiting middleware
- [ ] Implement connection pooling for Neo4j
- [ ] Add query optimization strategies

### Developer Experience

- [ ] Create comprehensive API documentation
- [ ] Develop example client implementations
- [ ] Add development tools and utilities
- [ ] Create testing utilities and fixtures
- [ ] Add contract tests for schema changes
- [ ] Implement CI/CD pipeline improvements

### Documentation

- [ ] Create installation guide
- [ ] Add deployment documentation
- [ ] Write contribution guidelines
- [ ] Create troubleshooting guide
- [ ] Add performance tuning guide
- [ ] Document security best practices

### Testing & Quality

- [ ] Increase test coverage to 90%
- [ ] Add integration tests
- [ ] Implement performance benchmarks
- [ ] Add load testing suite
- [ ] Create security testing framework

### Features

- [ ] Design and implement use case strategy
- [ ] Design and develop agent components
- [ ] Develop MCP and A2A components
- [ ] Create improvement strategy with KPIs
- [ ] Add CV generation pipeline
- [ ] Implement graph-based résumé generation
- [ ] Add support for multiple output formats (PDF, HTML, Markdown)

## [0.1.9] - Thu May 23 16:45:00 PDT 2025

### Added

- GitHub Actions workflows for both projects
  - Separate workflows for hypergraph and skill_sphere_mcp
  - Automated test runs and linting
  - Coverage badge generation and updates
  - Proper caching configuration for dependencies

### Changed

- Split Node2Vec implementation into separate modules
  - Moved to dedicated package structure
  - Improved code organization
  - Enhanced maintainability
- Updated README.md with
  - Project badges and status
  - Quick start instructions
  - Project overview and features
  - Contact information
- Fixed GitHub Actions configuration
  - Corrected cache keys and paths
  - Improved badge generation workflow
  - Added proper error handling for git operations
  - Fixed path issues in coverage badge generation

### Fixed

- GitHub Actions workflow issues
  - Fixed cache cleanup errors
  - Corrected badge generation paths
  - Resolved git commit/push errors
  - Fixed working directory configurations
- Path handling in coverage badge generation
  - Corrected output paths for badges
  - Fixed directory structure issues
  - Resolved path duplication problems

## [0.1.8] - Thu May 23 15:30:00 PDT 2025

### Changed

- Refactored Node2Vec implementation into modular package structure
  - Split into config, state, sampling, walks, training, and model modules
  - Improved code organization and maintainability
  - Updated architecture documentation
  - Fixed dependency issues with scipy and gensim

## [0.1.7] - Wed May 22 14:30:00 PDT 2025

### Changed

- Restructured ingestion pipeline into proper Python package
  - Moved code to `src/hypergraph/` with modular organization
  - Added proper test structure with pytest
  - Added dependency management with pyproject.toml
  - Added comprehensive README
  - Updated architecture documentation

## [0.1.6] - Fri May 16 10:25:37 PDT 2025

### Added

- Initial release of SkillSphere MCP Server
  - JSON-RPC 2.0 compliant API implementation
  - Model Context Protocol (MCP) support
  - Neo4j graph database integration
  - Semantic search with Node2Vec embeddings
  - OpenTelemetry instrumentation
  - Tool dispatching system
  - Health check endpoint
  - Environment-based configuration

### Changed

- Improved Knowledge-HyperGraph by
  - implementing "gleaning loop"
  - Node2Vec graph embeddings
- Consolidated server setup into `app.py`
- Removed redundant `main.py` and `mcp_server.py`
- Updated documentation to reflect new server structure
- Improved type hints and error handling

### Fixed

- Type mismatch in `rpc_search` function
- Session handling in `rpc_tool` function
- Linter errors in API routes

## [0.1.5] - Thu May 15 20:46:34 PDT 2025

### Added

- Initial ingestion pipe
- Node2Vec embeddings for semantic search
- Graph search tool implementation
- Resource schema definitions
- Tool parameter validation

### Changed

- Updated API documentation
- Improved error handling
- Enhanced test coverage

## [0.1.4] - Thu May 15 09:28:39 PDT 2025

### Added

- Missing experience records
- Basic MCP protocol implementation
- Neo4j connection management
- OpenTelemetry integration
- Initial test suite

### Changed

- Updated documentation
- Refactored API structure
- Updated configuration management

## [0.1.3] - Thu May  8 10:19:03 PDT 2025

### Added

- Certificates record
- Initial project setup
- FastAPI application structure
- Basic configuration
- Development environment setup

### Changed

- Added AI focus on experience record

## [0.1.2] - Tue Apr 22 18:44:11 PDT 2025

### Added

- Branding files
- Initial website

## [0.1.1] - Fri Apr 18 13:53:33 PDT 2025

### Added

- First experience files
- Prompt to improve experience data

## [0.1.0] - Sat Feb  8 10:19:16 PST 2025

### Added

- Initial version
- Changelog
