# SkillSphere — Hypergraph-Powered Professional Knowledge Base

## Hypergraph

[![Hypergraph Pylint](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml/badge.svg?job=test&matrix=project%3Ahypergraph%2Ccheck%3Apylint)](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml?query=branch%3Amain+job%3Atest+matrix%3Aproject%3Ahypergraph%2Ccheck%3Apylint)
[![Hypergraph Tests](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml/badge.svg?job=test&matrix=project%3Ahypergraph%2Ccheck%3Apytest)](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml?query=branch%3Amain+job%3Atest+matrix%3Aproject%3Ahypergraph%2Ccheck%3Apytest)
[![Hypergraph Coverage](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml/badge.svg?job=test&matrix=project%3Ahypergraph%2Ccheck%3Acoverage)](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml?query=branch%3Amain+job%3Atest+matrix%3Aproject%3Ahypergraph%2Ccheck%3Acoverage)

## SkillSphere MCP

[![MCP Pylint](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml/badge.svg?job=test&matrix=project%3Askill_sphere_mcp%2Ccheck%3Apylint)](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml?query=branch%3Amain+job%3Atest+matrix%3Aproject%3Askill_sphere_mcp%2Ccheck%3Apylint)
[![MCP Tests](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml/badge.svg?job=test&matrix=project%3Askill_sphere_mcp%2Ccheck%3Apytest)](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml?query=branch%3Amain+job%3Atest+matrix%3Aproject%3Askill_sphere_mcp%2Ccheck%3Apytest)
[![MCP Coverage](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml/badge.svg?job=test&matrix=project%3Askill_sphere_mcp%2Ccheck%3Acoverage)](https://github.com/bprager/SkillSphere/actions/workflows/tests.yml?query=branch%3Amain+job%3Atest+matrix%3Aproject%3Askill_sphere_mcp%2Ccheck%3Acoverage)

[![Python 3.10.17](https://img.shields.io/badge/python-3.10.17-blue.svg)](https://www.python.org/downloads/)

*A reproducible, open-source playground that turns plain career notes into a query-ready knowledge graph **and** can spit out job-targeted, ATS-friendly résumés on demand.*

---

## ✨ Why this repo exists

| Pain point                                                  | How SkillSphere helps                                                                                            |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Career data scattered across docs, LinkedIn and slide decks | **Single-source-of-truth**: all jobs, projects and certs live in Markdown                                        |
| Recruiters can't see proof of specific skills quickly       | **Hypergraph-of-Thought** in Neo4j lets agents answer: *"Show projects proving Kubernetes cost-optimisation."*   |
| Tailoring a résumé for every role is tedious                | **Graph-to-PDF pipeline** converts the same graph into a fully **ATS-optimised CV** aligned to a chosen job spec |
| Privacy / cost worries around SaaS LLMs                     | Runs **entirely local** on Ollama; no OpenAI key required                                                        |

If you're exploring AI-driven personal knowledge graphs *or* need a quick way to generate job-specific CVs, clone the repo, drop in your own records and you'll have a live graph **and** résumé builder inside 10 minutes.

---

## 🚀 Quick start

```bash
git clone https://github.com/bprager/SkillSphere.git
cd SkillSphere
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt       # faiss-cpu, langchain-community, neo4j-driver…
ollama pull gemma3:12b                # or your favourite local LLM
cp .env.sample .env                   # adjust Neo4j creds if needed

# 1) Build / refresh the graph
python -m hypergraph

# 2) Generate an ATS-ready résumé for a target job description
python scripts/build_resume.py --job-spec docs/job_postings/google_se_iii.md
```

* Browse the graph → [http://localhost:7474](http://localhost:7474) (Neo4j)
* Query skills via MCP API → `curl localhost:8000/query -d '{"prompt":"List cloud skills"}'`
* Résumé PDF appears in `output/` ready to send.

---

## 🗺️ Repo tour

| Path                             | Purpose                                                                          |
| -------------------------------- | -------------------------------------------------------------------------------- |
| `docs/`                          | Markdown records (`jobs`, `extras`, `certifications`) **and** job-spec examples. |
| `src/hypergraph/`                | Core ingestion pipeline with **gleaning loop** + **Node2Vec**.                   |
| `architecture.md`                | Design spec & PlantUML flow.                                                     |
| `scripts/build_resume.py`        | Graph→Markdown→Pandoc pipeline for **ATS PDFs**.                                 |
| `templates/`                     | Pandoc résumé / cover-letter templates.                                          |
| `tests/`                         | Comprehensive test suite with 100% coverage of core modules.                     |

---

## 🛠️ Core Components

### Hypergraph Module (`src/hypergraph/`)

* **LLM Integration** (`llm/`): Triple extraction and knowledge gleaning
* **Graph Database** (`db/`): Neo4j operations and registry management
* **Embeddings** (`embeddings/`): FAISS vector store for semantic search
* **Core** (`core/`): Configuration and shared utilities

### Testing (`tests/`)

* Unit tests with pytest
* Mocked Neo4j and LLM interactions
* Comprehensive coverage of core functionality

---

## 📚 Research foundation

SkillSphere's hypergraph model is inspired by:

> **Haoran Luo, Haihong E, Guanting Chen, et al.**
> *HyperGraphRAG: Retrieval-Augmented Generation with Hypergraph-Structured Knowledge Representation.*
> arXiv: 2503.21322 (2025). [https://arxiv.org/abs/2503.21322](https://arxiv.org/abs/2503.21322)

We adapt it to a **personal** graph and add:

* Incremental ingest with SHA-256 change tracking
* Local-LLM **gleaning loop** that wrings ~25% extra facts per chunk
* Neo4j GDS **Node2Vec** embeddings for structural search
* A résumé generator that queries the graph and compiles an **ATS-optimised CV** for any job description
* Comprehensive test suite ensuring reliability

---

## 🤝 Why you might care

* **Hiring for AI / knowledge-graph talent?** — this is a live sample of my architecture, Python and graph-data chops.
* **Building internal talent graphs or CV automation?** — fork it, swap Markdown for HR data, and you're halfway to a skills matrix and auto-CV tool.
* **Just curious?** — open a PR or start a discussion; I love geeky graph & GenAI conversations.

---

## 📬 Let's connect

* Web [https://www.prager.ws](https://www.prager.ws)
* Email [bernd@prager.ws](mailto:bernd@prager.ws) · LinkedIn [@berndprager](https://www.linkedin.com/in/berndprager)
* Book a chat [https://calendly.com/bernd-prager/30min](https://calendly.com/bernd-prager/30min)

---

© 2025 Bernd Prager — Apache 2.0 • Clone, adapt, and let me know what you build!
