---
title: "SkillSphere Architecture"
author: "Bernd Prager"
date: 2025-05-29            # rendered automatically
subtitle: "Revision v2.1"
abstract: |
  **SkillSphere** converts plain-text career records into a Neo4j‑powered
  *Hypergraph‑of‑Thought*, enriched by local LLM gleaning loops and served
  through an **MCP API** that LLM agents can query. This document provides a
  proud, yet practical, walkthrough of the architecture that makes it tick.
---

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 0  Executive Overview

| What it does | Why it matters |
|--------------|----------------|
| **Markdown ➜ Hypergraph** | One source of truth for jobs, projects & certifications |
| **LLM gleaning loop** | Wring ~25 % extra facts *locally* (Gemma 3 12 B on Ollama) |
| **Node2Vec embeddings** | Structural similarity search and résumé ranking |
| **MCP Server** | Standardised API that any LangChain agent can query |
| **Graph ➜ Markdown ➜ PDF** | One‑click, ATS‑optimised résumé for any job spec |
| **OpenTelemetry inside** | End‑to‑end tracing & Prom‑ready metrics out of the box |
| **100 % unit‑tested core** | CI badges say what words can’t fileciteturn2file5 |

> **TL;DR for decision‑makers** – this is a live, reproducible sample of my
> graph‑thinking, Python craftsmanship and DevOps rigour. Fork it for your org
> or hire me to tailor it.

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 1  Logical View

```{ .plantuml height=50% plantuml-filename=LogicalView.png }
@startuml
!theme plain
skinparam packageStyle rectangle

package "Data Layer" {
  A : Markdown docs
  B : doc_registry (SQLite)
  C : embeddings cache (FAISS)
}

package "Processing Layer" {
  D : Hypergraph Package (Python)
  E : Ollama LLMs\nGemma 3 12B / nomic-embed
}

package "Graph Layer" {
  F : Neo4j
  G : GDS Node2Vec (embedding)
}

package "Application Layer" {
  H : MCP Server (FastAPI)
  I : LangChain + Agents
}

A --> D
D --> B : hash check
D --> C : text embeddings
D --> E : gleaning loop
E --> D : triples JSON
D --> F : Cypher MERGE
F --> G : Node2Vec
G --> F : write property `embedding`
F --> H
H --> I
@enduml
```

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 2  Design Principles & Innovations

* **Local‑first AI.** All LLM calls run on Ollama, eliminating token costs and
  protecting sensitive career data.
* **Gleaning Loop.** Up to three iterative passes request *only new* triples,
  boosting recall without ballooning latency fileciteturn2file1.
* **Deterministic Cypher MERGE.** Idempotent writes guarantee clean graphs even
  under reruns and parallel ingestion.
* **Observability by default.** OpenTelemetry exports latency, Cypher timings
  and Node2Vec runtime straight to Grafana.
* **CI‑driven confidence.** Separate workflows for *hypergraph* and *MCP* run
  lint, type‑check, unit tests and coverage gates before any merge hits `main`.

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 3  Hypergraph Package

<details><summary>Directory snapshot (click to expand)</summary>

```text
hypergraph/
├── src/hypergraph/
│   ├── core/          # settings, utils
│   ├── db/            # Neo4j & SQLite helpers
│   ├── embeddings/    # FAISS store
│   └── llm/           # Gemma 3 triple extraction
└── tests/             # pytest, 100 % coverage
```
</details>

### 3.1  Processing Steps

1. **Change detection** – SHA‑256 hashes skip unchanged docs (SQLite registry).
2. **Chunk & embed** – 1 500‑word windows, 200‑word overlap; vectors stored in
   FAISS for hybrid search.
3. **Gleaning loop** – up to 3 Gemma passes ask *only* for missing triples.
4. **Graph update** – deterministic Cypher `MERGE` ensures alias‑safe nodes.
5. **Node2Vec refresh** – post‑ingest GDS batch writes 128‑d embeddings.

*First full build: ~3 × v1 runtime; incremental runs ≈ 45 s on 800 docs.*

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 4  MCP Server

FastAPI app exposing both human‑friendly CRUD and strict *Model Context Protocol* RPC.

```{ .plantuml height=60% plantuml-filename=MCPServer.png }
@startuml
!theme plain
skinparam componentStyle rectangle

component "FastAPI App" as FastAPI {
  [main.py\nlifespan] as main
  [api.routes\n(public)] as routes
  [api.mcp_routes\n(MCP RPC)] as mcp
}

package "Core Services" {
  [config.settings\n(Pydantic-Settings)] as settings
  [auth.pat\nPAT Auth] as pat
  [telemetry.otel\nOTel setup] as otel
}

package "Data Access" {
  [db.neo4j\nAsyncSession] as neo4j
  [graph.embeddings\nNode2Vec cache] as embed
  [graph.node2vec\nTrainer] as n2v
}

FastAPI --> pat : verify PAT
FastAPI --> neo4j : Cypher (async)
FastAPI --> embed : tool calls
embed --> neo4j : read‑only Cypher
pat --> settings
neo4j --> settings
otel --> settings
FastAPI --> otel : instrumentation

cloud "OTel\nCollector" as collector
otel --> collector : OTLP/gRPC

database "Neo4j" as db
neo4j --> db
@enduml
```

### 4.1  Runtime Flow

1. **Startup** – configuration, health‑check Neo4j, init OTEL.
2. **Authenticated request** – PAT → dependency‑injected session → Cypher/Vector
   search → JSON/Streaming response.
3. **Shutdown** – graceful driver close; spans flushed.

### 4.2  OpenTelemetry at a glance

| Signal | Exporter | Destination |
|--------|----------|-------------|
| **Traces** | OTLP/gRPC | Self‑hosted **Grafana Tempo** |
| **Metrics** | Prometheus | **Grafana Loki/Prom** dashboards |
| **Logs** | Stdout (+ tracespan IDs) | **Grafana Loki** |

```python
# telemetry/otel.py (excerpt)
from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource.create({"service.name": "skillsphere-mcp"})
trace.set_tracer_provider(trace.TracerProvider(resource=resource))
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="tempo:4317"))
trace.get_tracer_provider().add_span_processor(span_processor)
```

*20 µs overhead per request; worth every byte for end‑to‑end flame‑graphs.*

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 5  Infrastructure & Ops

| Host | Stack | Ports |
|------|-------|-------|
| **odin** | Neo4j 5.15 + GDS 2.x | 7474 / 7687 |
| **odin** | Ollama 0.6.8 | 11434 |
| **odin** | Ingestion Worker (systemd / Docker) | – |
| **odin** | MCP Server (FastAPI) | **8000** |
| **odin** | Grafana + Tempo + Loki + Prometheus | 3000 / 9090 / 3200 |

### 5.1  Docker‑Compose deployment

A single‑command setup for local dev or PoC:

```yaml
version: "3.9"
services:
  neo4j:
    image: neo4j:5.15
    volumes:
      - neo4j-data:/data
    environment:
      - NEO4J_AUTH=neo4j/test
    ports:
      - "7474:7474"
      - "7687:7687"

  ollama:
    image: ollama/ollama:0.6.8
    volumes:
      - ollama-models:/root/.ollama
    ports:
      - "11434:11434"

  mcp:
    build: ./skill_sphere_mcp
    env_file: .env
    depends_on:
      - neo4j
      - ollama
    ports:
      - "8000:8000"

  ingestion:
    build: ./hypergraph
    command: ["python", "-m", "hypergraph.cli.ingest", "--watch", "300"]
    volumes:
      - ./ingestion_docs:/app/ingestion_docs
    depends_on:
      - neo4j
      - ollama

  grafana:
    image: grafana/grafana:10.4.2
    ports:
      - "3000:3000"
    depends_on:
      - tempo
      - prometheus
      - loki

  tempo:
    image: grafana/tempo:2.4.3
    ports:
      - "3200:3200"
      - "4317:4317"

  loki:
    image: grafana/loki:2.9.7
    ports:
      - "3100:3100"

  prometheus:
    image: prom/prometheus:v2.51.2
    ports:
      - "9090:9090"

volumes:
  neo4j-data:
  ollama-models:
```

```bash
# spin up everything
$ docker compose up -d

# watch logs
$ docker compose logs -f mcp | sed -e "s/\x1b\[[0-9;]*m//g" | lnav
```

### 5.2  Periodic ingestion

| Method | When to use | How |
|--------|-------------|-----|
| **Docker watch‑mode** | Simple demos / dev | `--watch 300` flag (see compose) |
| **Systemd timer** | Single prod host | `systemctl enable hypergraph-ingest.timer` (5 min) |
| **GitHub Actions CRON** | Cloud Neo4j Aura | `schedule: '*/15 * * * *'` triggers `ingest` job |

All methods call the same entry‑point:

```bash
python -m hypergraph.cli.ingest  # defaults: one‑shot
```

### 5.3  Running the MCP server

| Context | Command |
|---------|---------|
| **Bare metal** | `uvicorn skill_sphere_mcp.main:app --host 0.0.0.0 --port 8000 --workers 4` |
| **Docker** | `docker compose up mcp` |
| **Dev hot‑reload** | `uvicorn skill_sphere_mcp.main:app --reload` |

Once up, browse Swagger UI at <http://localhost:8000/docs> – traces stream to
Tempo automatically.

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 6  Performance Snapshot (M1 Max, 32 GB)

| Stage | Docs = 800 | Docs Δ = 8 |
|-------|-----------|-----------|
| Ingest + Glean | 4 m 20 s | 18 s |
| Node2Vec 128‑d | 55 s | 55 s |
| Total wall‑clock | **5 m 15 s** | **1 m 13 s** |

*Graphs stay snappy – 50 k nodes, 220 k rels queries < 100 ms.*

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 7  Research Foundation

SkillSphere builds on **HyperGraphRAG** (2025) fileciteturn2file1, adapting its
hypergraph retrieval to personal knowledge graphs and augmenting it with:

* Incremental ingest & hash tracking
* Local LLM gleaning loop
* Node2Vec structural embeddings
* Graph‑to‑PDF résumé pipeline

Further reading lives in `docs/research.md`.

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 8  Roadmap

1. **Edge weighting + centrality pre‑compute** for richer MCP ranking.
2. **Auto‑summary blurbs** per entity (Gemma 3 distillation).
3. **Incremental Node2Vec** once graph size justifies it.
4. **Async ingest with two‑pass RAG** for high‑QPS environments.
5. **Helm chart** for Kubernetes deploys with horizontal pod autoscale.

<!-- ─────────────────────────────────────────────────────────────────────────── -->
## 9  Hire Me

Need *graph‑driven AI* in your org? Book a 30‑min strategy call
(<https://calendly.com/bernd-prager/30min>) and let’s build your competitive
edge together.

---
<sup>© 2025 Bernd Prager — Apache 2.0. Clone it, fork it, improve it, and tell me
what you build!</sup>

