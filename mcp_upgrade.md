# SkillSphere MCP Server — Detailed Upgrade Path

*Compliance with MCP Specification 2025‑06‑18*

## 1  Scope & Goals

Upgrade the existing SkillSphere MCP server (FastAPI‑based) from compliance with MCP v 2025‑03‑26 to full compliance with MCP v 2025‑06‑18. The upgrade introduces mandatory OAuth 2 Resource‑Server semantics, protocol‑version negotiation, and structured tool output while deprecating JSON‑RPC batching.

## 2  Prerequisites

* **Branch strategy** – create `feature/mcp-2025‑06` off `main`.
* **Python 3.12** and **Poetry 1.8** or `uv` for dependency management.
* **Docker / docker‑compose** for local integration tests.
* Access to identity provider that supports OAuth 2 introspection (e.g. Keycloak or Auth0).

## 3  High‑Level Timeline

| Day | Work Package                                          |
| --: | ----------------------------------------------------- |
| 1‑2 | WP‑1 OAuth 2 Resource Server                          |
|   3 | WP‑2 Protocol Version Middleware                      |
| 4‑6 | WP‑3 Structured Tool Output                           |
|   7 | WP‑4 Public Schema Extensions                         |
| 8‑9 | WP‑5 Elicitation & Resource Links (optional/“tier‑2”) |
|  10 | WP‑6 Remove Batching & Harden Tests                   |
|  11 | WP‑7 Documentation & Ops                              |

## 4  Detailed Work Packages

### 4.1  WP‑1 OAuth 2 Resource Server *(Days 1‑2)*

**Objective:** Replace Personal‑Access‑Token (PAT) auth with OAuth 2 Bearer‑JWT validation.

| Task | Description                                                                                                           |
| ---- | --------------------------------------------------------------------------------------------------------------------- |
| 1    | Install `fastapi-oauth2-resource-server` and add to `pyproject.toml`.                                                 |
| 2    | Create `auth/oauth.py` with `OAuth2ResourceProtector` using Introspection endpoint from `${OAUTH_INTROSPECTION_URL}`. |
| 3    | Introduce new **required** env vars: `OAUTH_INTROSPECTION_URL`, `OAUTH_CLIENT_ID`, `MCP_RESOURCE_ID`.                 |
| 4    | Update dependency injection in `routers/*.py`: `current_user = Depends(validate_access_token)`.                       |
| 5    | Generate discovery doc at `/.well-known/mcp-oauth.json` (FastAPI `StaticFiles`).                                      |
| 6    | Add e2e Postman collection covering valid/invalid token, scope check, and replay detection.                           |

**Deliverables:**

* Working JWT‑protected endpoints.
* CI pipeline step `pytest tests/auth/`.

### 4.2  WP‑2 Protocol Version Middleware *(Day 3)*

**Objective:** Enforce `MCP-Protocol-Version` header on every request; inject correct version on responses.

| Task | Description                                                                                            |
| ---- | ------------------------------------------------------------------------------------------------------ |
| 1    | Add `middleware/protocol_version.py` that verifies header equals `2025‑06‑18` after session handshake. |
| 2    | On mismatch, raise `HTTP_426_UPGRADE_REQUIRED` with JSON body `{ "required_version": "2025-06-18" }`.  |
| 3    | Add unit tests in `tests/middleware/test_protocol_version.py`.                                         |
| 4    | Update `docker-compose.override.yml` to set `MCP_PROTOCOL_VERSION` env var.                            |

### 4.3  WP‑3 Structured Tool Output *(Days 4‑6)*

**Objective:** Emit tool‑specific structured results and JSON Schemas.

| Task | Description                                                                                                                                    |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | For each tool class in `tools/*.py`, create an inner `class OutputModel(BaseModel)` describing the response.                                   |
| 2    | Update tool descriptor (`ToolDescriptor.outputSchema`) to `OutputModel.model_json_schema()`.                                                   |
| 3    | Wrap executor (`execute_tool`) so it returns `{ "structured_result": output.dict() }` if `OutputModel` exists; otherwise fallback to `result`. |
| 4    | Add Pydantic validation error handling → return MCP error `-32800 StructuredValidationError`.                                                  |
| 5    | Extend integration tests in `tests/tools/` to assert presence & shape of `structured_result`.                                                  |

### 4.4  WP‑4 Public Schema Extensions *(Day 7)*

**Objective:** Include `_meta`, `title`, and `context` in all public models and RPC payloads.

| Task | Description                                                                                  |
| ---- | -------------------------------------------------------------------------------------------- |
| 1    | Add Mixin `ExtendedFields` with optional fields and inherit in all request/response models.  |
| 2    | Set default `_meta = { "generated_by": "SkillSphere 2.3" }` in `BaseConfig.model_construct`. |
| 3    | Regenerate OpenAPI (`/docs`) and ensure no warnings in Swagger‑UI or VS Code MCP client.     |

### 4.5  WP‑5 Elicitation & Resource Links *(Days 8‑9)*

**Objective:** Implement optional spec goodies to improve UX.

| Task | Description                                                                                          |
| ---- | ---------------------------------------------------------------------------------------------------- |
| 1    | Add new RPC `elicitation.request` that returns `prompt`, `schema`, and optional `defaults`.          |
| 2    | For graph‑based tools, append `.links` array with `bolt://` or `https://` deep‑links to nodes/edges. |
| 3    | Extend frontend demo notebook to consume elicitation flow.                                           |

### 4.6  WP‑6 Remove Batching & Harden Lifecycle Tests *(Day 10)*

**Objective:** Delete legacy JSON‑RPC batching and mark lifecycle ops mandatory.

| Task | Description                                                                                 |
| ---- | ------------------------------------------------------------------------------------------- |
| 1    | Remove `List[RpcRequest]` branch in `rpc_router.py`.                                        |
| 2    | If batch detected → return error `-32600` (`batch_not_supported`).                          |
| 3    | Update test harness so `initialize`, `initialized`, and `shutdown` are **required** checks. |

### 4.7  WP‑7 Documentation & Ops *(Day 11)*

**Objective:** Final documentation, version bump, and operational dashboards.

| Task | Description                                                                    |
| ---- | ------------------------------------------------------------------------------ |
| 1    | Bump Docker image tag to `skillsphere-mcp:2.3` and push to container registry. |
| 2    | Update `docs/architecture.md`: Security, Runtime Flow, Config sections.        |
| 3    | Create Grafana dashboard panel tracking `401`, `403`, `426` response counts.   |
| 4    | Announce release in CHANGELOG and internal Slack `#skillsphere‑dev`.           |

## 5  Acceptance Criteria

* All tests green (`pytest`, `mypy`, `ruff`).
* Postman “MCP 2025‑06‑18 Compliance” collection passes in CI.
* Swagger‑UI shows `MCP-Protocol-Version` header pre‑filled.
* OAuth token with wrong `resource_indicator` is rejected (403).
* Host clients (VS Code ≥ 1.91, Windows AI Foundry Preview 3) can call a structured tool and parse `structured_result` without warnings.

## 6  Rollback & Contingency

* Tag `v2.2.1` on current production commit before merge.
* Keep PAT auth behind feature flag `ENABLE_OAUTH` for 1 week.
* Blue/green deploy on Kubernetes: `mcp‑blue` (v2.2.1) ↔ `mcp‑green` (v2.3).

## 7  Appendix — Reference Links

* MCP Spec 2025‑06‑18: [https://modelcontext.org/spec/2025-06-18](https://modelcontext.org/spec/2025-06-18)
* RFC 8707 (Resource Indicators): [https://datatracker.ietf.org/doc/html/rfc8707](https://datatracker.ietf.org/doc/html/rfc8707)
* fastapi‑oauth2‑resource‑server: [https://github.com/indominusbyte/fastapi-oauth2-resource-server](https://github.com/indominusbyte/fastapi-oauth2-resource-server)

