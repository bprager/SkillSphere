# Changelog

## [2.3.1] - 2025-01-15

### Added

- **Matomo Analytics Integration**: Added comprehensive web analytics with GeoIP2 tracking
  - Docker-based Matomo setup with dedicated MySQL database
  - Nginx reverse proxy with geo-location headers
  - Privacy-focused analytics with custom event tracking
  - Persistent storage for analytics data
  - Separate Docker network for isolation

- **Certification Template System**: Created comprehensive template system for professional certifications
  - `certification_template.md` with standardized YAML front matter structure
  - `CERTIFICATION_TEMPLATE_GUIDE.md` with detailed usage instructions
  - `certification_quick_reference.md` with common patterns and examples
  - `CERTIFICATION_TEMPLATE_BENEFITS.md` documenting processing advantages
  - Migration and verification scripts for template adoption

### Changed

- **OAuth Configuration**: Updated redirect URI configuration for production deployment
  - Fixed redirect URI in oauth.py to match production environment
  - Improved error handling for OAuth callback flow
  - Enhanced security for production OAuth flow

- **Certification Data Structure**: Migrated from single monolithic file to individual certification files
  - Split `certifications.md` into 8 individual files (6 professional + 2 in-progress)
  - Enhanced YAML front matter with entity IDs, status tracking, and competency arrays
  - Individual file processing dramatically improves hypergraph accuracy
  - Structured metadata enables better LLM gleaning and search capabilities

### Fixed

- **Geo-location Tracking**: Fixed GeoIP2 integration with proper database mounting
  - Corrected MaxMind database path in Docker volume mounts
  - Fixed Nginx geo-location header configuration
  - Improved geo-location data accuracy in Matomo dashboard

### Infrastructure

- Added Matomo Docker Compose configuration with MySQL database.
- Added environment configuration for analytics tracking.
- Improved development scripts and tooling for better developer experience.

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
