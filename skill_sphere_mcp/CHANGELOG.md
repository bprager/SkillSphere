<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to the SkillSphere MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-05-16

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

- Consolidated server setup into `app.py`
- Removed redundant `main.py` and `mcp_server.py`
- Updated documentation to reflect new server structure
- Improved type hints and error handling

### Fixed

- Type mismatch in `rpc_search` function
- Session handling in `rpc_tool` function
- Linter errors in API routes

## [0.3.0] - 2025-05-01

### Added

- Node2Vec embeddings for semantic search
- Graph search tool implementation
- Resource schema definitions
- Tool parameter validation

### Changed

- Updated API documentation
- Improved error handling
- Enhanced test coverage

## [0.2.0] - 2025-04-15

### Added

- Basic MCP protocol implementation
- Neo4j connection management
- OpenTelemetry integration
- Initial test suite

### Changed

- Refactored API structure
- Updated configuration management

## [0.1.0] - 2025-04-01

### Added

- Initial project setup
- FastAPI application structure
- Basic configuration
- Development environment setup

[0.4.0]: https://github.com/yourusername/skill-sphere-mcp/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/yourusername/skill-sphere-mcp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/yourusername/skill-sphere-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/skill-sphere-mcp/releases/tag/v0.1.0
