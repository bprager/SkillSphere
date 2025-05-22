# Product Requirements Document (PRD)

**Product:** SkillSphere MCP Server
**Author:** Bernd Prager  **Reviewer(s):** TBD
**Version:** 0.4 (derived from PDD v0.3.0)  **Date:** 20 May 2025

---

## 1 · Purpose & Background

Recruiters, hiring bots and "smart-CV" tools repeatedly ask:

* "Does Bernd have the skills for *this* role?"
* "Generate a résumé tailored to *that* job description."

SkillSphere exposes Bernd Prager's skills-and-experience **hypergraph** through the **Model Context Protocol (MCP)**, so any LLM agent can reason over a single, always-up-to-date source instead of scraping LinkedIn or PDFs. The PRD turns the existing PDD into an actionable roadmap for engineering, product and go-to-market teams.&#x20;

---

## 2 · Objectives & Success Metrics

| Objective                     | KPI / Success Metric                         | Target            |
| ----------------------------- | -------------------------------------------- | ----------------- |
| Accelerate suitability checks | Avg. time for recruiter bot to answer "fit?" | ≤ 3 s (p95)       |
| Automate CV creation          | % CVs generated without manual edits         | ≥ 80 %            |
| Provide explainability        | % agent responses citing graph evidence      | ≥ 90 %            |
| Reliability                   | API availability (rolling 30 d)              | ≥ 99.5 %          |
| Observability                 | Traces with end-to-end latency & errors      | 100 % of requests |

---

## 3 · Scope

| In-Scope                                                             | Out-of-Scope                               |
| -------------------------------------------------------------------- | ------------------------------------------ |
| Read-only MCP endpoints (`/rpc`)                                     | Direct write access to the hypergraph      |
| Four core resources (`skills.node`, `skills.relation`, `profiles.*`) | Editing LinkedIn or external profiles      |
| Four callable tools (`skill.*`, `cv.generate`, `graph.search`)       | Interview scheduling, calendar integration |
| OpenTelemetry tracing                                                | Detailed business analytics dashboard      |
| Deployment on single VM / Kubernetes                                 | Multi-tenant SaaS offering                 |

### Assumptions

* Hypergraph already exists in Neo4j and is kept current by a separate ingestion pipeline.
* Agents are credentialed via PAT; no anonymous access.

---

## 4 · User Personas & Top Use-Cases

| Persona                               | Goal                                   | Representative Questions                           |
| ------------------------------------- | -------------------------------------- | -------------------------------------------------- |
| **Suitability Agent** (recruiter bot) | Decide if Bernd fits a role            | "List critical skill gaps."                        |
| **CV Generator Agent**                | Produce tailored résumé / cover letter | "Give me a one-pager emphasising Go & Kubernetes." |

(See PDD §2 for extended table)&#x20;

---

## 5 · User Stories

1. **As a recruiter bot**, I want to call `skill.match_role` with a list of required skills so that I receive a similarity score and gap analysis.
2. **As a recruiter bot**, I want to call `skill.explain_match` for each supporting node so that I can justify my recommendation.
3. **As a CV generator agent**, I want to call `cv.generate` with target keywords and format = "markdown" so that I receive an instantly usable résumé.
4. **As any agent**, I want to list resources and tools on `initialize` so that I can self-discover capabilities.

---

## 6 · Functional Requirements

| #    | Requirement                                                                               | Priority |
| ---- | ----------------------------------------------------------------------------------------- | -------- |
| FR-1 | Support MCP handshake (`initialize`) incl. negotiated protocol version                    | Must     |
| FR-2 | Implement `resources/list`, `resources/get` for the four resources                        | Must     |
| FR-3 | Implement tool dispatcher with JSON Schema validation for four tools                      | Must     |
| FR-4 | Integrate with Neo4j via Bolt (read-only)                                                 | Must     |
| FR-5 | Produce Node2Vec / embedding search results via `graph.search`                            | Should   |
| FR-6 | Expose `/healthz` for liveness & readiness                                                | Must     |
| FR-7 | Stream OpenTelemetry traces to collector; mask PII                                        | Should   |
| FR-8 | Provide REST "legacy" endpoints (`/v1/entity/{id}`, `/v1/search`) until full MCP adoption | Could    |

*Note:* tool parameter / return schemas are specified in PDD §5.&#x20;

---

## 7 · Non-Functional Requirements

| Area              | Requirement                                         | Metric / Standard                 |
| ----------------- | --------------------------------------------------- | --------------------------------- |
| **Performance**   | End-to-end latency for tool call (p95)              | ≤ 1 s                             |
| **Scalability**   | Handle 10 concurrent agent sessions, 50 RPS bursts  | Horizontal pod auto-scale         |
| **Reliability**   | API uptime                                          | ≥ 99.5 %                          |
| **Security**      | PAT auth; read-only permissions enforced in Neo4j   | OWASP ASVS L1                     |
| **Observability** | 100 % structured traces with latency & error labels | OTLP                              |
| **Compliance**    | No personal data beyond public résumé exported      | GDPR Art. 6 (legitimate interest) |

---

## 8 · Acceptance Criteria & Test Plan

### Functional Acceptance

* **Initialize** returns declared capabilities & instructions.
* **Resources**: `resources/get skills.node 123` returns expected labels/props.
* **Tools**: Calling `cv.generate` with mocked requirements returns markdown with ≥ 3 new role-specific bullet points.
* **Error handling**: Invalid tool params return JSON-RPC error -32602.

### Non-Functional Acceptance

* Load-test with k6 confirms < 1 s p95 latency at 50 RPS.
* Chaos test (pod kill) shows recovery within 30 s with no error leakage.
* Trace sample verifies PII is excluded.

---

## 9 · Dependencies

| Dependency                               | Status                 | Owner         |
| ---------------------------------------- | ---------------------- | ------------- |
| Neo4j instance with populated hypergraph | Running                | DevOps        |
| OpenTelemetry Collector                  | Configured             | Observability |
| JSON-RPC / MCP client libraries          | Selected (open-source) | Backend       |
| PAT issuance process                     | Defined                | Security      |

---

## 10 · Timeline & Milestones*

| Date (Q2-25) | Milestone                                    |
| ------------ | -------------------------------------------- |
| **6 Jun**    | REST → MCP adapter scaffolded                |
| **20 Jun**   | `initialize`, resource endpoints complete    |
| **11 Jul**   | Tool dispatcher + `skill.*` tools functional |
| **25 Jul**   | `graph.search`, Node2Vec embeddings          |
| **08 Aug**   | Observability & health checks                |
| **15 Aug**   | Beta freeze & stakeholder UAT                |
| **29 Aug**   | v1.0 launch                                  |

* Dates assume two-week sprints; adjust per team velocity.

---

## 11 · Risks & Mitigations

| Risk                                                             | Impact | Likelihood | Mitigation                                                   |
| ---------------------------------------------------------------- | ------ | ---------- | ------------------------------------------------------------ |
| Graph schema drift causes tool failures                          | High   | Medium     | Freeze Neo4j schema during MVP; add contract tests           |
| LLM hallucination despite instructions                           | Medium | Medium     | Tighten tool schemas; reinforce with examples                |
| Recruiter bots rely on legacy REST endpoints longer than planned | Medium | High       | Maintain REST for one extra quarter; publish migration guide |
| High latency from Neo4j queries                                  | High   | Low        | Add indices; cache hot resources in Redis                    |

---

## 12 · Future Considerations

* Replace Node2Vec with Graph-RAG embeddings for richer context (Road-map Q2-25).
* Add write-back endpoint so agents can attach interview feedback (Q4-25).
* Investigate multi-tenant mode to serve other professionals.

---

## 13 · Glossary

| Term           | Definition                                                                      |
| -------------- | ------------------------------------------------------------------------------- |
| **MCP**        | Model Context Protocol – JSON-RPC-based standard for agent ↔ server interaction |
| **Hypergraph** | Neo4j graph of Bernd's skills, certifications, projects & relationships         |
| **Resource**   | Read-only data entity exposed via MCP (`skills.node`, `profiles.summary`, …)    |
| **Tool**       | Model-invocable function with strict JSON Schema parameters & returns           |

---

### ✅ PRD Approval Checklist

* [ ] Stakeholders reviewed objectives & KPIs
* [ ] Engineering validated requirements & timeline
* [ ] Security signed off on privacy controls
* [ ] Product leadership approved scope

---

**Next step:** Kick-off Sprint 1 on 2 June 2025 with finalized epics and Jira tickets.
