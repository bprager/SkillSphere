# Product Description Document (SkillSphere MCP Server)

*A hypergraph-backed talent API for AI agents*

---

## 1 · Why this server exists

Recruiters, hiring bots and “smart-CV” tools keep asking the same questions:

* *“Does Bernd have the skills for **this** role?”*
* *“Generate a résumé tailored to **that** job description.”*

The SkillSphere server exposes Bernd Prager’s **skills-and-experience hypergraph** through the **Model Context Protocol (MCP)** so any LLM agent can reason over a single, always-up-to-date knowledge source rather than scraping LinkedIn or PDFs.

MCP provides a negotiated, machine-readable interface built on JSON-RPC 2.0 and supports both **read-only resources** and **callable tools** ([Philschmid][1]).  During the **`initialize` handshake** client and server agree on protocol revision and capabilities ([Model Context Protocol][2], [Medium][3]).

---

## 2 · Primary use-cases

| # | Actor                                                      | Goal                                       | Typical questions                                                                                      |
| - | ---------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| 1 | **Suitability agent** (recruiter bot, opportunity-matcher) | Decide if Bernd fits a role / project      | *“List critical skill gaps.”*<br>*“Explain his most relevant experience for a fintech data-platform.”* |
| 2 | **CV generator agent**                                     | Produce a role-targeted CV or cover letter | *“Give me a one-page résumé emphasising Go & Kubernetes.”*                                             |

---

## 3 · High-level architecture

```{ .plantuml height=50% plantuml-filename=HighLevelArchitecture.png }
@startuml
title SkillSphere MCP High-Level Architecture

actor "LLM Agent" as LLM

node "SkillSphere MCP\n(FastAPI App)" as MCP {
}

database "Skills Hypergraph\n(Neo4j)" as Neo4j

cloud "OpenTelemetry\nCollector" as OTEL

LLM <--> MCP : JSON-RPC 2.0 over HTTP
MCP --> Neo4j : Bolt Protocol
MCP --> OTEL : OTLP Traces

@enduml
```

*FastAPI* provides HTTP transport ([Model Context Protocol][4]); an adapter routes `/rpc` to the JSON-RPC dispatcher.
*Neo4j* stores the hypergraph (nodes: *organization, document, person, geo, event, advisory, address, coverage, damage, finances, product, profession, property, risk*).
*OpenTelemetry* ships traces to the team’s collector.

---

## 4 · Resources exposed

| Resource ID             | Purpose                                    | JSON Schema snippet                                             |
| ----------------------- | ------------------------------------------ | --------------------------------------------------------------- |
| **`skills.node`**       | Any node in the hypergraph                 | `{ id: integer, labels: string[], props: object }`              |
| **`skills.relation`**   | A typed edge                               | `{ sourceId: int, targetId: int, type: string, props: object }` |
| **`profiles.summary`**  | Pre-rendered career summary paragraph      | `{ markdown: string }`                                          |
| **`profiles.timeline`** | Chronological list of positions & projects | `{ items: [ {title, org, start, end, highlight[]} ] }`          |

Agents fetch resources with the standard `resources/get` and enumerate with `resources/list`.

---

## 5 · Tools available

> Tools are **model-controlled** functions; parameters & returns are fully
> typed with JSON Schema so an LLM can invoke them safely.

| Tool name                 | Description                                                                                                | Params                                        | Return                                                  |                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------- | ---------------------------------------- |
| **`skill.match_role`**    | Compute similarity between a job’s required skills and Bernd’s graph. Optionally suggest mitigation steps. | `requirements: string[]` `top_k: int=10`      | `{score: 0-1, gaps: string[], supporting_nodes: int[]}` |                                          |
| **`skill.explain_match`** | Explain *why* a particular node (experience, project, certification) supports the match.                   | `node_id: int` `requirement: string`          | `{markdown: string}`                                    |                                          |
| **`cv.generate`**         | Produce a résumé or cover letter emphasising provided requirements and tone.                               | `requirements: string[]` \`format: "markdown" | "pdf"\`                                                 | `{markdown?: string, pdf_file?: string}` |
| **`graph.search`**        | Vector / semantic search over Node2Vec embeddings stored on nodes.                                         | `query: string` `k: int=15`                   | `{hits: [{node_id, score}]}`                            |                                          |

---

## 6 · `initialize` response design

```jsonc
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-05-16",
    "capabilities": {
      "resources": { "subscribe": false, "listChanged": true },
      "tools":     { "listChanged": true },
      "prompts":   {},
      "logging":   { "structured": true }
    },
    "serverInfo": { "name": "SkillSphere MCP", "version": "0.3.0" },
    "instructions": "You are connected to Bernd Prager’s skills-graph. \
Use `graph.search` or traverse `skills.node` to gather evidence, \
then call `skill.match_role` or `cv.generate` as appropriate. \
Prefer nodes labelled 'JOB' or 'CERTIFICATION' for hard evidence. \
If a requirement is missing, suggest relevant up-skilling."
  }
}
```

*Rationale*

* `resources.listChanged=true` lets future versions push live updates (e.g., a new paper Bernd publishes).
* No writable side effects are exposed (read-only hypergraph), so `subscribe=false`.
* Instructions guide the model toward high-value nodes and available tools.

---

## 7 · Endpoint catalogue

| HTTP Path              | Transport       | JSON-RPC method(s)                                                            | Purpose                                     |
| ---------------------- | --------------- | ----------------------------------------------------------------------------- | ------------------------------------------- |
| `POST /rpc`            | Streamable HTTP | All standard MCP methods (`initialize`, `resources/*`, `tools/*`, tool calls) | Primary MCP endpoint                        |
| `GET  /healthz`        | plain REST      | —                                                                             | Liveness probe for infra                    |
| `GET  /v1/entity/{id}` | REST (legacy)   | —                                                                             | Direct node fetch (non-MCP clients)         |
| `POST /v1/search`      | REST (legacy)   | —                                                                             | Temporary search prior to full MCP adoption |

---

## 8 · Example agent flows

### 8.1 · Suitability agent

1. `initialize` → learns about `skill.match_role`.
2. `tools/call` → `skill.match_role` with JD keywords.
   *Gets `{score: 0.82, gaps:["Kafka"], supporting_nodes:[123,456]}`.*
3. For each supporting node call `skill.explain_match` → bullet-proof narrative.
4. Respond to recruiter with evidence & gap mitigation plan.

### 8.2 · CV generator agent

1. `initialize` → discovers `cv.generate`.
2. Optionally `graph.search` to pull extra context (e.g., specific fintech project).
3. `tools/call` → `cv.generate` with requirements + `format:"markdown"`.
4. Render markdown or convert PDF for delivery.

---

## 9 · Security & privacy

* 🔒 Server is **read-only**; no private data beyond Bernd’s public résumé content.
* OAuth2 (PAT) optional for write-capable future endpoints.
* OpenTelemetry traces exclude PII.

---

## 10 · Road-map

| Quarter | Feature                                                                                    |
| ------- | ------------------------------------------------------------------------------------------ |
| Q2-25   | Replace Node2Vec with Graph-RAG embeddings for richer `graph.search`.                      |
| Q3-25   | Add **interview simulation** tool (`interview.ask`) exposing behavioural-question prompts. |
| Q4-25   | Write-back capability so agents can attach recruiter feedback directly to the graph.       |

---

## 11 · Getting started ⚡️

```bash
# Install with Astral uv for deterministic builds
uv pip install "mcp-server[cli]" neo4j fastapi uvicorn opentelemetry-sdk
# Run locally (requires Neo4j & .env with creds)
python mcp_server.py
# Test initialize
curl -s -X POST http://localhost:8000/rpc -d \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | jq
```

---

> **SkillSphere MCP** turns Bernd’s 25 years of architecture, AI and leadership experience into a first-class, LLM-navigable knowledge graph—ready for any hiring or résumé agent to consume.

[1]: https://www.philschmid.de/mcp-introduction?utm_source=chatgpt.com "Model Context Protocol (MCP) an overview - Philschmid"
[2]: https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle?utm_source=chatgpt.com "Lifecycle - Model Context Protocol"
[3]: https://medium.com/%40nimritakoul01/the-model-context-protocol-mcp-a-complete-tutorial-a3abe8a7f4ef?utm_source=chatgpt.com "The Model Context Protocol (MCP) — A Complete Tutorial - Medium"
[4]: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports?utm_source=chatgpt.com "Transports - Model Context Protocol"

