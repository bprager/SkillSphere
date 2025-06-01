# SkillSphere ⚡️

**_Graph-powered talent intelligence in < 10 min_**

> _Turn scattered career notes into a live knowledge graph — and one-click, ATS-ready résumés._

![Hypergraph • Test + Lint](https://github.com/bprager/SkillSphere-Agent/actions/workflows/hypergraph.yml/badge.svg)
![Hypergraph • Coverage](hypergraph/coverage.svg)
![SkillSphere MCP • Test + Lint](https://github.com/bprager/SkillSphere-Agent/actions/workflows/skill_sphere_mcp.yml/badge.svg)
![SkillSphere MCP • Coverage](skill_sphere_mcp/coverage.svg)

![Python 3.10](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/github/license/bprager/SkillSphere-Agent.svg)

---

## 🌟 Why you'll care

| Problem | SkillSphere's answer |
|--------|------------------------|
| **Career data everywhere** — LinkedIn, slides, docs | Markdown → **Neo4j hypergraph** (one source of truth) |
| **Generic CVs don't win roles** | Graph-query → **Job-specific résumé PDF** |
| **LLM privacy & cost nerves** | Runs **fully local** on Ollama, no API keys |
| **Need proof of my graph/AI chops** | This repo **is** the demo — explore the live graph or read the code |

---

## 🚀 30‑second taste

```bash
git clone https://github.com/bprager/SkillSphere.git
cd SkillSphere && ./scripts/quick_start.sh   # builds graph + sample résumé
open output/resume_google.pdf
```

> Full install & config instructions live in **`docs/installation.md`**.

---

## 🔍 See it in action

![SkillSphere demo GIF](docs/media/coming_soon.gif)

---

## 🧩 Inside the box

* **Hypergraph‑of‑Thought** model → Neo4j + Node2Vec embeddings
* **Gleaning loop** wrings 25 % extra facts from each chunk
* **Graph→Markdown→PDF** pipeline for recruiter‑ready résumés
* 100 % unit‑tested core modules

Deep‑dive architecture and research notes are in **`docs/architecture.md`**.

---

## 🤝 Work with me

I design & build **graph‑driven AI solutions** that make talent, knowledge and content searchable & actionable.
If that sparks ideas for your team:

* **[Book a 30‑min chat](https://calendly.com/bernd-prager/30min)**
* **[Connect on LinkedIn](https://www.linkedin.com/in/bprager)**
* **Say hi via email:** `bernd@prager.ws`

Let's turn your data into an unfair advantage.

---

© 2025 **Bernd Prager** — _Apache 2.0_
Clone it, fork it, improve it — and tell me what you build!
