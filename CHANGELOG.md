# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-06-17

### Changed

- **Code Quality Improvements**: Enhanced overall code quality and maintainability
  - Resolved all R0801 (duplicate code) pylint issues
  - Eliminated code duplication in Pydantic models and API routes
  - Consolidated shared functionality into reusable utility functions
  - Improved import organization and code structure
  - Fixed test failures introduced by previous pylint improvements

### Fixed

- **Duplicate Code Issues**: Eliminated code duplication across the codebase
  - Consolidated duplicate `HealthResponse`, `InitializeRequest`, and `InitializeResponse` models
  - Created shared `create_skill_in_db()` utility function to eliminate duplicate skill creation logic
  - Fixed import order issues in utility modules
  - Resolved test failures caused by handler return format changes
- **Test Suite Stability**: Fixed all test failures and improved test reliability
  - Updated mock data structures to match expected formats
  - Fixed Node2Vec model preprocessing for test scenarios
  - Corrected error handling expectations in test cases
  - Removed invalid module patches in test files
- **Pylint Compliance**: Achieved excellent code quality standards
  - Resolved all R0801 duplicate code violations
  - Maintained 9.84/10 overall pylint score
  - Fixed import order and code style issues
  - Improved error handling consistency

### Technical Details

- **Models Consolidation**: Moved shared Pydantic models to `api/mcp/models.py` and updated imports
- **Utility Functions**: Created `create_skill_in_db()` in `api/mcp/utils.py` for shared skill creation logic
- **Test Improvements**: Enhanced mock fixtures and test data structures for better reliability
- **Code Organization**: Improved separation of concerns and reduced code duplication

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

- [ ] Add Kubernetes deployment manifests
- [ ] Add rate limiting middleware
- [ ] Implement connection pooling for Neo4j
- [ ] Add query optimization strategies

### Developer Experience

- [ ] Create comprehensive API documentation
- [ ] Develop example client implementations
- [ ] Add development tools and utilities
- [ ] Create testing utilities and fixtures
- [ ] Add contract tests for schema changes

### Documentation

- [ ] Create installation guide
- [ ] Add deployment documentation
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

## [0.2.1] - 2024-03-19

### Added
- Static HTML landing page for the MCP server with key features and API documentation link
- OpenTelemetry integration with Grafana Tempo for distributed tracing
- Docker Compose configuration for local development with Tempo and OpenTelemetry collector
- New user-friendly landing page with responsive design and modern typography
- Integration with Grafana Tempo for distributed tracing visualization
- OpenTelemetry collector configuration for metrics and traces
- Configurable MCP instructions for LLM clients with owner identification and usage guidelines
- Environment variable-based configuration for MCP server behavior

### Changed
- Removed internal Neo4j service from docker-compose.yml in favor of external Neo4j instance
- Updated MCP server to serve static files from the root path
- Improved container networking configuration to avoid port conflicts
- Enhanced observability with end-to-end tracing capabilities
- Updated architecture documentation to reflect new UI and observability features
- Moved MCP instructions to environment configuration for better maintainability
- Updated MCP initialization response to include owner context and usage guidelines

### Fixed
- Resolved permission issues with Tempo data directory
- Fixed port conflict between OpenTelemetry collector and Tempo services
- Improved container startup reliability
- Addressed networking issues between services
- Fixed static file serving configuration in FastAPI application

### Infrastructure
- Added Grafana Tempo for distributed tracing
- Configured OpenTelemetry collector for metrics and traces
- Implemented proper container networking between services
- Set up persistent storage for Tempo data
- Improved Docker Compose configuration for local development

## [0.2.0] - Fri Jun 8 18:48:47 PDT 2025

### Added

- CV generation module with support for multiple formats
  - Markdown and HTML output formats
  - Structured CV sections (contact, summary, skills, experience, education)
  - Template-based formatting
  - Graph-based data retrieval
- Enhanced test coverage for MCP server
  - Added comprehensive test suite for API endpoints
  - Improved mock data and fixtures
  - Added async test support
  - Enhanced error handling tests

### Changed

- Improved package structure and installation
  - Moved to src-based layout
  - Enhanced development mode installation
  - Fixed Python path issues
  - Improved dependency management
- Updated GitHub Actions workflow
  - Switched to standard pip for package management
  - Added proper Python path configuration
  - Enhanced test execution with asyncio support
  - Improved coverage reporting
- Enhanced error handling and validation
  - Added parameter validation for CV generation
  - Improved error messages and status codes
  - Enhanced type checking and validation

### Fixed

- Module import issues in tests
  - Fixed Python path configuration
  - Corrected package installation
  - Resolved import errors
- GitHub Actions workflow issues
  - Fixed package installation
  - Corrected test execution
  - Resolved coverage reporting
  - Fixed badge generation

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