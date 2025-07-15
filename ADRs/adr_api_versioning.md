# ADR: API Design and Versioning Strategy

## Status
Proposed

## Context
The SkillSphere MCP Server exposes a JSON-RPC 2.0 compliant API alongside RESTful endpoints. As the system evolves, maintaining backward compatibility and enabling smooth API evolution is critical.

## Decision
- Use JSON-RPC 2.0 as the primary protocol for MCP operations, ensuring strict adherence to the specification.
- Expose RESTful endpoints for health checks, metrics, and auxiliary operations.
- Implement API versioning via URL path prefixes (e.g., `/v1/`) for REST endpoints.
- Maintain backward compatibility by supporting multiple API versions concurrently when needed.
- Use semantic versioning for the API and document changes clearly in the changelog and API docs.
- Deprecate legacy features (e.g., JSON-RPC batching) with clear error responses and documentation.
- Provide comprehensive OpenAPI documentation for REST endpoints, including versioning information.

## Consequences
- Clear separation of concerns between JSON-RPC and REST APIs.
- Easier client migration and version management.
- Improved developer experience with up-to-date documentation.
- Controlled deprecation of legacy features.

## Next Steps
- Implement versioned REST routes.
- Maintain changelog and API documentation.
- Communicate deprecations clearly to clients.
