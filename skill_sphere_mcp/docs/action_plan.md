To design an action plan for the development of the SkillSphere MCP Server, we will leverage the provided Product Requirements Document (PRD).

**I. Project Overview**

* **Product:** SkillSphere MCP Server
* **Purpose:** To expose Bernd Prager's skills-and-experience hypergraph through the Model Context Protocol (MCP) for LLM agents to reason over.
* **Version:** 0.4
* **Launch Date Target:** August 29, 2025 (v1.0 launch)
* **Assumptions:**
    * Hypergraph already exists in Neo4j and is kept current by a separate ingestion pipeline.
    * Agents are credentialed via PAT; no anonymous access.

**II. Key Objectives & Success Metrics**

The development plan will focus on achieving the following objectives and their corresponding Key Performance Indicators (KPIs):

* **Accelerate suitability checks:** Average time for recruiter bot to answer “fit?” ≤ 3 seconds (p95).
* **Automate CV creation:** ≥ 80% CVs generated without manual edits.
* **Provide explainability:** ≥ 90% agent responses citing graph evidence.
* **Reliability:** API availability (rolling 30 days) ≥ 99.5%.
* **Observability:** 100% of requests with traces with end-to-end latency & errors.

**III. Scope of Work (In-Scope for MVP)**

The initial development will focus on:

* Read-only MCP endpoints (`/rpc`).
* Four core resources (`skills.node`, `skills.relation`, `profiles.*`).
* Four callable tools (`skill.*`, `cv.generate`, `graph.search`).
* OpenTelemetry tracing.
* Deployment on single VM / Kubernetes.

**IV. Development Action Plan - Phased Approach**

The timeline in the PRD suggests a phased approach with two-week sprints. The following outlines the plan based on the provided milestones:

**Phase 1: Foundational Setup & Core MCP Handshake (Estimated: June 2 - June 20, 2025)**

* **Milestone:** REST → MCP adapter scaffolded (Target: June 6, 2025).
    * **Tasks:**
        * Set up project repository and initial development environment.
        * Implement basic MCP server structure.
        * Design and implement the adapter layer for future REST to MCP transition.
* **Milestone:** `initialize`, resource endpoints complete (Target: June 20, 2025).
    * **Tasks:**
        * Implement `initialize` endpoint to support MCP handshake, including negotiated protocol version (FR-1).
        * Implement `resources/list` and `resources/get` for the four core resources (`skills.node`, `skills.relation`, `profiles.*`) (FR-2).
        * Set up basic read-only integration with Neo4j via Bolt (FR-4).
        * Expose `/healthz` for liveness & readiness checks (FR-6).

**Phase 2: Tool Dispatcher & Core Tooling (Estimated: June 23 - July 25, 2025)**

* **Milestone:** Tool dispatcher + `skill.*` tools functional (Target: July 11, 2025).
    * **Tasks:**
        * Implement tool dispatcher with JSON Schema validation for the four tools (FR-3).
        * Develop and integrate `skill.match_role` and `skill.explain_match` tools.
        * Implement `cv.generate` tool.
* **Milestone:** `graph.search`, Node2Vec embeddings (Target: July 25, 2025).
    * **Tasks:**
        * Implement `graph.search` to produce Node2Vec / embedding search results (FR-5).
        * Integrate necessary libraries or services for Node2Vec embeddings.

**Phase 3: Observability, Security & Acceptance (Estimated: July 28 - August 15, 2025)**

* **Milestone:** Observability & health checks (Target: August 8, 2025).
    * **Tasks:**
        * Stream OpenTelemetry traces to collector, ensuring PII masking (FR-7).
        * Implement comprehensive error logging and monitoring.
        * Verify 100% structured traces with latency & error labels (NFR - Observability).
* **Milestone:** Beta freeze & stakeholder UAT (Target: August 15, 2025).
    * **Tasks:**
        * Conduct load testing with k6 to confirm ≤ 1 second p95 latency at 50 RPS (Non-Functional Acceptance).
        * Perform chaos testing (pod kill) to ensure recovery within 30 seconds with no error leakage (Non-Functional Acceptance).
        * Verify PAT authentication and read-only permissions in Neo4j (NFR - Security).
        * Initiate User Acceptance Testing (UAT) with stakeholders and gather feedback.
        * Address any critical bugs or issues identified during UAT.

**Phase 4: Launch Preparation (Estimated: August 18 - August 29, 2025)**

* **Milestone:** v1.0 launch (Target: August 29, 2025).
    * **Tasks:**
        * Finalize documentation and release notes.
        * Prepare deployment artifacts for single VM / Kubernetes (In-Scope).
        * Conduct final smoke tests in the production environment.
        * Monitor system performance and stability post-launch.

**V. Cross-Cutting Concerns**

* **Security:** Implement PAT authentication and ensure read-only permissions are enforced in Neo4j (NFR - Security). Adhere to OWASP ASVS L1 standards.
* **Reliability:** Aim for ≥ 99.5% API uptime (NFR - Reliability).
* **Scalability:** Design for horizontal pod auto-scaling to handle 10 concurrent agent sessions and 50 RPS bursts (NFR - Scalability).
* **Compliance:** Ensure no personal data beyond public résumé is exported, adhering to GDPR Art. 6 (legitimate interest) (NFR - Compliance).
* **Risk Mitigation:**
    * **Graph schema drift:** Freeze Neo4j schema during MVP and add contract tests.
    * **LLM hallucination:** Tighten tool schemas and reinforce with examples.
    * **High latency from Neo4j queries:** Add indices and cache hot resources in Redis.

**VI. Dependencies**

* Neo4j instance with populated hypergraph (DevOps).
* OpenTelemetry Collector configured (Observability).
* JSON-RPC / MCP client libraries selected (Backend).
* PAT issuance process defined (Security).

**VII. Future Considerations (Post V1.0 Launch)**

* Replace Node2Vec with Graph-RAG embeddings for richer context (Road-map Q2-25).
* Add write-back endpoint for agents to attach interview feedback (Q4-25).
* Investigate multi-tenant mode to serve other professionals.

This action plan provides a structured approach to developing the SkillSphere MCP Server, aligning with the objectives and requirements outlined in the PRD. Regular reviews and adjustments based on team velocity and feedback will be crucial for success.

