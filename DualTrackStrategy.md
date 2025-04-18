1 · Decision Lens

```plantuml
@startuml Decision_Lens
!theme spacelab
title Graph‑Store Options for PJES

frame "Property‑Graph Path" {
  :Neo4j CE;
  :KuzuDB;
}

frame "Semantic‑Web Path" {
  :Neo4j + n10s;
  :Kuzu RDFGraphs;
  :Pure RDF store (Jena / Blazegraph);
}

:Protégé IDE: --> "OWL/RDF Ontologies";
"OWL/RDF Ontologies" --> "Neo4j + n10s";
"OWL/RDF Ontologies" --> :Kuzu RDFGraphs;
"OWL/RDF Ontologies" --> :Pure RDF store;

:Neo4j CE --> :API surface (Cypher, GraphQL);
:KuzuDB --> :Embedded API (Cypher/Python);
:Pure RDF store --> :SPARQL endpoint;

:Neo4j CE --> :PJES KG;
:KuzuDB --> :PJES KG;
:Pure RDF store --> :PJES KG;

note right of :KuzuDB
+ MIT licence
+ Fast analytics
– No clustering
end note
note right of :Neo4j CE
+ Mature ecosystem
+ APOC / GDS
– Some features paywalled
end note
@enduml
```


⸻

2 · KuzuDB vs Neo4j at a Glance

Factor	Neo4j CE 5.x	KuzuDB 0.9 (Apr 2025)
Licence	GPL‑3 (Community); AGPL/commercial for Enterprise	MIT – fully permissive  ￼
Maturity / Ranking	≈ 14 years in market; #1 graph DB on DB‑Engines  ￼	First public release 2023; still “early‑adopter” tier  ￼
Query Language	Cypher + preview GQL; full-text, path‑finding, pattern comprehensions	Implements a large Cypher subset; missing some APOC style procs
Vector Search	Add‑on (GDS v2, AuraDS)	Built‑in vector & full‑text indices  ￼
Analytics / GDS	Mature Graph Data Science lib (algorithms, embeddings)	No native algorithms yet; relies on external Python libs
Server / Embedding	Runs as server; clustering only in Enterprise	Embedded / serverless library; no HA cluster
RDF/OWL Path	n10s plugin: import/export RDF, SHACL validation, basic inferencing  ￼	RDFGraphs extension: native triple ingestion, SHACL blog demo  ￼ ￼
Tooling Ecosystem	Bloom viz, Cypher‑Workbench, robust docs, large community	Python/JS bindings, CLI, active—but smaller—Discord
Footprint on your workstation	JVM + Bolt server (~512 MB baseline)	Single shared‑lib + on‑disk columnar store; hundreds of MB
Strengths	Stability, ecosystem, rich APOC procedures, GDS, GraphQL bridges	Blazing OLAP performance, permissive licence, easy embedding, vector search
Trade‑offs	Some advanced features gated behind Enterprise; heavier	Fewer integrations, limited docs, evolving syntax, single‑process only



⸻

3 · Protégé + OWL/RDF Toolchain

Why bother?

Benefit	Detail
Ontology‑first modelling 	Drag‑and‑drop class hierarchy, DL reasoners (HermiT, Pellet) to check consistency  ￼
Inter‑op	Export Turtle/OWL → load into Neo4j n10s (n10s.onto.import.fetch)  ￼ or into Kuzu RDFGraphs API
Collaboration	WebProtégé enables multi‑user reviews, comments, change‑tracking
Validation	Author SHACL shapes in Protégé, then run validation inside Neo4j n10s or Kuzu (blog demo)  ￼

Risks / Overheads
	•	Extra layer to learn; may distract from core PJES delivery.
	•	OWL reasoning can bloat KG with inferred triples; watch memory usage on 60 GB host.
	•	Mapping impedance: property‑graph queries (Cypher) vs triple patterns (SPARQL) may confuse future contributors—stick to one mental model per module.

⸻

4 · How Each Option Serves PJES Goals

Goal	Neo4j	KuzuDB	Protégé + RDF
Rapid MVP (Ph 2 & 3)	Familiar to you; GraphQL & LangChain adapters ready‑made	Needs custom Python wrapper for HTTP or embed in agent process	Slower—conversion layer required
Showcasing AI leadership	Rich APOC + GDS demos (knowledge‑graph embeddings, link‑prediction)	Cutting‑edge vector index/ WASM embedding could impress	Demonstrates semantic‑web breadth
Open A2A / MCP	JSON‑LD export via n10s; easy HTTP layer	Need to build REST/GraphQL facade yourself	Direct RDF (SHACL) validation—good for open agents
Broaden personal portfolio	You already know it well	Gives you “new tech” story for talks	Adds ontology engineering credibility
FinOps / self‑hosting	Small for single‑instance; Enterprise licence pricey if you later need cluster	Free, lightweight; but single‑node → manual fail‑over	Tooling free; reasoning CPU‑hungry



⸻

5 · Recommended Path
	1.	Stick with Neo4j CE for Phases 0‑4
Fastest path to a working coach, public profile, and chat agent.
	•	Use n10s early so your schema stays RDF‐friendly.
	•	Keep Cypher dialect vanilla to remain portable.
	2.	Create a shadow KuzuDB branch in Phase 4
	•	Run nightly ETL from Neo4j → Kuzu to benchmark vector & analytic queries.
	•	Publish a blog “Neo4j vs Kuzu: lessons from my PJES” (adds to your thought‑leadership).
	3.	Protégé workflow (optional power‑up)
	•	Draft the core ontology (Person, Skill, Project, Publication).
	•	Export .ttl snapshots; load via n10s.onto.import.fetch.
	•	Schedule quarterly ontology reviews—don’t let modelling paralysis block shipping.

⸻

6 · Risk Mitigation Checklist

Risk	Guard‑rail
Over‑engineering KG stack	Freeze core schema v1 before experimenting with new DBs.
Licensing surprises	Stay on Neo4j Community; evaluate Kuzu MIT; document any proprietary add‑ons.
Resource saturation	Enable Neo4j page‑cache = 16 GB; cap Java heap = 8 GB; run Kuzu in separate cgroup.
Product‑focus drift	Define a “Definition of Done” per Phase; Kuzu & Protégé experiments only after DoD met.



⸻

7 · Bottom Line
	•	Neo4j gets you production‑ready functionality, Bloom visual demos, and familiar tooling—ideal for first public release.
	•	KuzuDB is a compelling add‑on for high‑speed analytics and a résumé talking point, but today it lacks the ecosystem depth you’ll need for the web‑facing API.
	•	Protégé + OWL/RDF adds semantic‑web credibility and long‑term interoperability; integrate it incrementally so it enhances rather than stalls delivery.

Adopt a dual‑track: deliver value now with Neo4j, explore Kuzu/Protégé in sandbox branches, and fold in their advantages when the core PJES is stable.
