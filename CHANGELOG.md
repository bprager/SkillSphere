# Changelog

## [2.3.0] - 2025-06-20

### Added
- Implemented OAuth 2 Resource Server authentication with introspection endpoint.
- Added Protocol Version Middleware enforcing MCP-Protocol-Version header.
- Introduced structured tool output with Pydantic OutputModel schemas.
- Added Public Schema Extensions with _meta, title, and context fields in all public models.
- Created new elicitation RPC endpoint for dynamic prompt and schema retrieval.
- Extended graph search tool output with deep-links to nodes.
- Removed JSON-RPC batching support; hardened lifecycle tests for initialize, initialized, and shutdown.
- Added feature flag ENABLE_OAUTH to toggle OAuth authentication.
- Added comprehensive unit and integration tests covering new features and upgrade steps.

### Changed
- Updated API models to include extended fields for better schema compliance.
- Updated dispatch tool to return structured results with validation.
- Updated FastAPI app to include new elicitation routes.

### Fixed
- Resolved import errors and test configuration issues during upgrade.
- Fixed test warnings related to async test handling.

### Deprecated
- Personal Access Token (PAT) authentication replaced by OAuth 2 Resource Server.

---

*For full details, see the MCP upgrade documentation and project README.*
