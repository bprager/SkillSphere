# ADR: Choosing Backend and Schema for Local MCP-based Skill Hypergraph

**Status**: Proposed  
**Date**: 2025-05-15  
**Context**: Based on [arXiv:2503.21322](https://arxiv.org/abs/2503.21322) and the implementation files (`chroma_impl.py`, `milvus_impl.py`, etc.), we are constructing a local **hypergraph** to model personal **skills**, **job experiences**, **certifications**, and **extracurricular activities** using an MCP server running on **Ubuntu**.

---

## Decision

We will use the following configuration:

### ✅ Backend: `neo4j_impl.py`

**Reasoning**:
- Graph databases (Neo4j) are **natively designed** for hypergraph and relationship modeling.
- Easy **local installation** via Docker or Neo4j Desktop.
- Excellent **querying and visualization** capabilities.
- Mature Cypher query language and integration with Python (`py2neo`, `neo4j`).

---

## Schema Design

### 🔹 Entity Types

| Label             | Description                                              |
|------------------|----------------------------------------------------------|
| `Person`          | Central identity node (e.g., Bernd Prager)             |
| `Job`             | Professional roles held                                 |
| `Organization`    | Employers, certification bodies                         |
| `Project`         | Named efforts or subunits within jobs                   |
| `Skill`           | Abstract competencies (e.g., Mentoring, Strategy)       |
| `Technology`      | Tools, frameworks, languages used                       |
| `Certification`   | Formal certifications earned                            |
| `ExperienceType`  | Classification: e.g., "Professional", "Volunteer"       |
| `Location`        | City/Country nodes for geo-tagging                      |
| `TimeRange`       | Start/end temporal brackets                             |

### 🔹 Relationships

| Relationship           | Source → Target                                     |
|------------------------|-----------------------------------------------------|
| `:HAS_EXPERIENCE`      | `Person` → `Job`                                    |
| `:WORKED_FOR`          | `Job` → `Organization`                              |
| `:HELD_ROLE`           | `Person` → `Project`                                |
| `:USED`                | `Job`/`Project` → `Skill` / `Technology`            |
| `:LOCATED_IN`          | `Job`/`Organization` → `Location`                   |
| `:DURING`              | `Job`/`Certification` → `TimeRange`                 |
| `:ACHIEVED_CERTIFICATION` | `Person` → `Certification`                    |
| `:ISSUED_BY`           | `Certification` → `Organization`                    |
| `:RELATED_TO`          | Generic linkage for flexible modeling               |
| `:EXPERIENCE_TYPE`     | `Job` → `ExperienceType`                            |

---

## Example Snippets (Cypher)

### Job Experience
```cypher
(:Person {name: "Bernd Prager"})-[:HAS_EXPERIENCE]->(:Job {title: "AI Architect", start: 2020, end: 2024})
(:Job)-[:WORKED_FOR]->(:Organization {name: "EPAM Systems"})
(:Job)-[:USED]->(:Skill {name: "RAG"})
(:Job)-[:USED]->(:Technology {name: "LangChain"})
(:Job)-[:LOCATED_IN]->(:Location {city: "Los Angeles", country: "USA"})
(:Job)-[:DURING]->(:TimeRange {start: "2020-10", end: "2024-03"})
```

### Certification
```cypher
(:Person)-[:ACHIEVED_CERTIFICATION]->(:Certification {name: "AWS Certified Solutions Architect", date: "2021-05"})
(:Certification)-[:ISSUED_BY]->(:Organization {name: "Amazon Web Services"})
(:Certification)-[:USED]->(:Skill {name: "Cloud Architecture"})
```

### Extracurricular Experience
```cypher
(:Person)-[:HAS_EXPERIENCE]->(:Job {title: "Mentor", type: "Volunteer"})
(:Job)-[:EXPERIENCE_TYPE]->(:ExperienceType {name: "Extracurricular"})
(:Job)-[:USED]->(:Skill {name: "Coaching"})
```

---

## Consequences

- A local Neo4j instance will be used to host the hypergraph.
- Cypher queries can be used for analysis and visualization.
- Potential future integrations with `chroma_impl.py` or `milvus_impl.py` for embedding search are still open.

