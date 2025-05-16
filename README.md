# SkillSphere — Hypergraph-Powered Professional Knowledge Base

*A reproducible, open-source playground that turns plain career notes into a query-ready knowledge graph **and** can spit out job-targeted, ATS-friendly résumés on demand.*

---

## ✨ Why this repo exists

| Pain point                                                  | How SkillSphere helps                                                                                            |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Career data scattered across docs, LinkedIn and slide decks | **Single-source-of-truth**: all jobs, projects and certs live in Markdown                                        |
| Recruiters can’t see proof of specific skills quickly       | **Hypergraph-of-Thought** in Neo4j lets agents answer: *“Show projects proving Kubernetes cost-optimisation.”*   |
| Tailoring a résumé for every role is tedious                | **Graph-to-PDF pipeline** converts the same graph into a fully **ATS-optimised CV** aligned to a chosen job spec |
| Privacy / cost worries around SaaS LLMs                     | Runs **entirely local** on Ollama; no OpenAI key required                                                        |

If you’re exploring AI-driven personal knowledge graphs *or* need a quick way to generate job-specific CVs, clone the repo, drop in your own records and you’ll have a live graph **and** résumé builder inside 10 minutes.

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
poetry run python hypergraph/ingestion_worker.py

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
| `hypergraph/ingestion_worker.py` | Ingestion pipeline with **gleaning loop** + **Node2Vec**.                        |
| `architecture.md`                | Design spec & PlantUML flow.                                                     |
| `scripts/build_resume.py`        | Graph→Markdown→Pandoc pipeline for **ATS PDFs**.                                 |
| `templates/`                     | Pandoc résumé / cover-letter templates.                                          |

---

## 📚 Research foundation

SkillSphere’s hypergraph model is inspired by:

> **Haoran Luo, Haihong E, Guanting Chen, et al.**
> *HyperGraphRAG: Retrieval-Augmented Generation with Hypergraph-Structured Knowledge Representation.*
> arXiv: 2503.21322 (2025). [https://arxiv.org/abs/2503.21322](https://arxiv.org/abs/2503.21322)

We adapt it to a **personal** graph and add:

* Incremental ingest with SHA-256 change tracking.
* Local-LLM **gleaning loop** that wrings \~25 % extra facts per chunk.
* Neo4j GDS **Node2Vec** embeddings for structural search.
* A résumé generator that queries the graph and compiles an **ATS-optimised CV** for any job description.

---

## 🤝 Why you might care

* **Hiring for AI / knowledge-graph talent?** — this is a live sample of my architecture, Python and graph-data chops.
* **Building internal talent graphs or CV automation?** — fork it, swap Markdown for HR data, and you’re halfway to a skills matrix and auto-CV tool.
* **Just curious?** — open a PR or start a discussion; I love geeky graph & GenAI conversations.

---

## 📬 Let’s connect

* Web [https://www.prager.ws](https://www.prager.ws)
* Email [bernd@prager.ws](mailto:bernd@prager.ws) · LinkedIn [@berndprager](https://www.linkedin.com/in/berndprager)
* Book a chat [https://calendly.com/bernd-prager/30min](https://calendly.com/bernd-prager/30min)

---

© 2025 Bernd Prager — Apache 2.0 • Clone, adapt, and let me know what you build!

