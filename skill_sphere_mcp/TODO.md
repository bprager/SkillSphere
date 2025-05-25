# Architectural Overview

Drawing on the **SkillSphere MCP** product-design document (PDD) , we’ll structure the server into **five core layers**:

1. **Entrypoint & Transport**

   * **`main.py`** boots the FastAPI app and mounts a single `/rpc` JSON-RPC router, plus health-check and any legacy REST routes.
   * A thin **RPC dispatcher** maps `method` names to handler functions.

2. **Configuration & Instrumentation**

   * **`config.py`** centralizes `pydantic-settings` declarations for all env vars (`neo4j_uri`, OTLP endpoint, protocol version, service metadata, etc.).
   * **`telemetry/`** contains OpenTelemetry setup: tracer provider, span processors, and FastAPI middleware.

3. **Domain Models & DTOs**

   * **`models/`** holds Pydantic schemas:

     * **RPC payloads** (`JSONRPCRequest`, `JSONRPCResponse`)
     * **Resource types** (`SkillNode`, `SkillRelation`, `ProfileSummary`, etc.)
     * **Tool parameter/results** (`MatchRoleParams`, `MatchRoleResult`, `CVGenerateParams`, …)

4. **Business Logic & Services**

   * **`services/neo4j_service.py`** wraps all Cypher queries (node fetch, graph search).
   * **`services/skill_service.py`** implements higher-level functions: `match_role()`, `explain_match()`.
   * **`services/cv_service.py`** generates markdown/PDF CVs.
   * Each service is injectable into RPC handlers.

5. **RPC Handlers & Tool Registry**

   * **`handlers/initialize.py`**, **`handlers/resources.py`**, **`handlers/tools.py`** define all MCP methods (`initialize`, `resources/list`, `tools/list`, `tools/call`).
   * A lightweight **plugin mechanism** allows future tools (e.g. `interview.ask`) to register themselves.

All components share the same **semantic version** and **protocolVersion** via settings, ensuring clients can introspect capabilities at startup.

---

## Proposed Directory Structure

```text
skill_sphere_mcp/
├── README.md                     # Project overview & quickstart
├── pyproject.toml                # Poetry/uv-managed project file
├── requirements.txt              # Pin fallback deps
├── .env.example                  # Sample env vars
├── Dockerfile                    # Container spec (prod/dev)
├── docker-compose.yml            # Neo4j + OTLP collector for local dev
├── docs/
│   ├── architecture.md           # Human-readable reference
│   └── diagrams/
│       └── HighLevelArchitecture.puml
│
├── skill_sphere_mcp/             # Python package root
│   ├── __init__.py
│   ├── main.py                   # Entrypoint, mounts routers
│   ├── config.py                 # Pydantic-settings definitions
│   ├── telemetry/
│   │   ├── __init__.py
│   │   ├── tracer.py             # OTLP exporter, span processor
│   │   └── middleware.py         # FastAPI instrumentation
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rpc.py                # JSONRPCRequest/Response schemas
│   │   ├── resources.py          # SkillNode, SkillRelation, ProfileSummary
│   │   └── tools.py              # Params & results for each tool
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── neo4j_service.py      # Bolt-driver abstraction
│   │   ├── skill_service.py      # match_role, explain_match
│   │   └── cv_service.py         # cv.generate implementation
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── initialize.py         # MCP handshake logic
│   │   ├── resources.py          # resources/list, resources/get
│   │   ├── tools.py              # tools/list, tools/call dispatch
│   │   └── plugins.py            # Optional dynamic tool loader
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── rest.py               # healthz, /v1/entity, /v1/search (legacy)
│   │   └── rpc.py                # single POST /rpc entrypoint
│   │
│   └── cli.py                    # Optional MCP CLI integration
│
└── tests/
    ├── conftest.py              # pytest fixtures (app, settings, Neo4j test container)
    ├── test_initialize.py
    ├── test_resources.py
    ├── test_tools.py
    └── integration/
        └── test_end_to_end.py
```

* **Modularity**: Each concern lives in its own folder (`models`, `services`, `handlers`).
* **Extensibility**: New tools or resources simply add a Pydantic schema in `models/tools.py` + a handler in `handlers/tools.py` (or via `handlers/plugins.py`).
* **Testability**: Clear separation enables unit tests for services and handlers, plus end-to-end tests against an ephemeral Neo4j instance.
* **Dev ergonomics**: `cli.py` can wire into the same RPC dispatcher for interactive use (`mcp[cli]`), while the FastAPI app handles production traffic.

This structure ensures the **SkillSphere MCP** remains maintainable, scalable, and ready for future capabilities like live subscriptions, write-back tooling, or interview simulations.
