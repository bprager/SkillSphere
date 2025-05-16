# ────────────────────────────────────────────────────────────
# Hypergraph-of-Thought skill/experience schema v1
# ────────────────────────────────────────────────────────────
meta:
  name: bernd_skill_graph
  version: "1.0"
  description: >
    Schema & extraction hints for building a Neo4j Hypergraph-of-Thought
    representing Bernd Prager’s skills, experience and credentials.

entities:
  - label: Person
    pk: [name]
    examples: ["Bernd Prager"]
  - label: Role
    pk: [title, start_date, organization]
    examples: ["Director Delivery Management", "Founding Spokesperson"]
  - label: Organization
    pk: [name]
    examples: ["EPAM Systems, Inc.", "Wirtschaftsjunioren Rostock"]
  - label: Project
    pk: [name, organization]
    examples: ["Insurance KG-RAG POC"]
  - label: Certification
    pk: [name, issuer]
    examples: ["Machine Learning", "TOGAF® 9"]
  - label: Activity          # extra-professional involvement
    pk: [name, organization]
    examples: ["State President", "Plenary Assembly Member"]
  - label: Event
    pk: [name, date]
    examples: ["LLM Architecture Patterns (Learning Week 2023)"]
  - label: Skill
    pk: [name]
    examples: ["Neo4j", "FinOps", "Mentorship"]
  - label: Tool
    pk: [name]
    examples: ["LangChain", "LlamaIndex", "Vue 3"]
  - label: Topic             # broad conceptual buckets
    pk: [name]
    examples: ["GenAI", "RAG"]
  - label: Hyperedge         # anchor node that CONNECTS many others
    pk: [hash]               # SHA-1 of sorted connected-node IDs

relationships:
  - type: HAS_ROLE
    from: Person
    to: Role
  - type: WORKED_AT          # Role → Organization
    from: Role
    to: Organization
  - type: CONTRIBUTED_TO     # Person/Role → Project
    from: Role
    to: Project
  - type: USED_IN            # Tool → Project
    from: Tool
    to: Project
  - type: SHOWCASED_IN       # Skill → Project/Event/Activity
    from: Skill
    to: "*"
  - type: COVERS_TOPIC       # Project/Cert/Event → Topic
    from: "*"
    to: Topic
  - type: OWNS_CERT          # Person → Certification
    from: Person
    to: Certification
  - type: SUPPORTS_SKILL     # Certification → Skill
    from: Certification
    to: Skill
  - type: CONNECTS           # Hyperedge → any connected node
    from: Hyperedge
    to: "*"

hyperedge_templates:
  # Anchor a bundle around a project and its key artefacts
  - name: project_bundle
    anchor: Project
    connects: [Skill, Tool, Organization, Topic]
    hash_fields: [anchor_id, connected_ids]

  # Bundle a certification with the skills & tools it validates
  - name: certification_bundle
    anchor: Certification
    connects: [Skill, Tool, Topic]

  # Bundle leadership or community activities with leadership skills
  - name: activity_leadership
    anchor: Activity
    connects: [Skill, Topic]

prompt_steering:
  # Provide these lists to the LLM as “known labels” to favour re-use
  known_skills:
    - Neo4j
    - FinOps
    - RAG
    - Mentorship
    - Public Speaking
  known_tools:
    - LangChain
    - LlamaIndex
    - Vue 3
    - Terraform
  alias_map:           # simple synonym guidance to cut duplicates
    Fin Ops: FinOps
    Gen-AI: GenAI
    GPT-4o: GPT-4o
    ML: Machine Learning

dedup_rules:
  string_similarity_threshold: 0.83
  embedding_similarity_threshold: 0.88
  prefer_existing_node_if:
    - exact_casefold_match
    - string_similarity_above_threshold
    - embedding_similarity_above_threshold

maintenance_jobs:
  - name: nightly_dedupe
    schedule: "0 3 * * *"          # 03:00 daily
    tasks:
      - apoc.refactor.mergeNodes   # merge duplicates
      - recalc_embeddings
      - recalc_centrality

# End of file

