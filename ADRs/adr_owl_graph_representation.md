# ADR: Using OWL/RDFS to Represent the Hypergraph Schema

**Status**: Proposed
**Date**: 2025-05-15
**Context**:
The project involves constructing a hypergraph-based system to model and explore professional skills, certifications, and experiences, using an MCP server. The data is intended to be stored and visualized using a graph backend (Neo4j), with the intent to document and publish the journey on GitHub.

This ADR evaluates the benefit of also representing the hypergraph in OWL (Web Ontology Language) or RDFS (RDF Schema) format, in addition to using Neo4j.

---

## Decision

We will support a dual-representation approach:
- **Primary graph modeling** will remain in **Neo4j** for performance, flexibility, and ease of local development.
- **Ontology-based representation** will be created in **OWL/RDFS** to support interoperability, reasoning, and publishing in alignment with semantic web standards.

---

## Rationale

### ✅ Value of OWL/RDFS Representation

1. **Standards & Interoperability**
   OWL and RDFS are W3C standards widely used in knowledge graphs and semantic web contexts. Publishing the graph in this format allows compatibility with:
   - SPARQL query engines
   - Ontology editors (e.g., Protégé)
   - Linked data platforms and reasoning systems

2. **Schema Reuse and Enrichment**
   The ability to reuse well-known vocabularies (e.g., FOAF, Schema.org, SKOS) allows for better integration and documentation of concepts like `Person`, `Organization`, `Role`, or `Skill`.

3. **Reasoning Capabilities**
   OWL supports logical inference. For example:
   - If `Bernd Prager` holds a job titled "Mentor" → infer experience with coaching.
   - If a skill is used in multiple projects → derive expertise level.

4. **FAIR Data Principles**
   Representing the graph in OWL aligns with the FAIR principles:
   - **F**indable
   - **A**ccessible
   - **I**nteroperable
   - **R**eusable

   Publishing RDF/OWL formats on GitHub enhances transparency and utility for broader communities.

5. **Future Proofing**
   This structure facilitates integration with LLM-based agents, semantic search, and web-linked knowledge bases.

---

## Implementation Plan

1. Develop the schema and data model in Neo4j using `neo4j_impl.py`.
2. When stable, export the graph to RDF/OWL using:
   - `neosemantics` (n10s plugin for Neo4j)
   - Python tools like `RDFLib` or `Owlready2`
3. Host the OWL ontology and RDF data on GitHub.
4. Optionally, document the ontology in human-readable format for broader accessibility.

---

## Consequences

- Adds semantic rigor and documentation to the knowledge graph.
- Slightly increases complexity but pays off in broader utility and reuse.
- Enables downstream use in reasoning engines and semantic tooling.
- Provides a high-quality publishable format for professional branding and community sharing.

---

## Alternatives Considered

- Using Neo4j only — simpler but limits interoperability and reasoning.
- Using only OWL — more complex for development and performance tuning.

By combining both, we maintain agility while supporting long-term semantic value.

