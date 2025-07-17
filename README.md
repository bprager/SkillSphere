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

## 📋 Skill Extraction & Documentation Guide

### For LLM-Assisted Repository Analysis

This repository is structured to systematically capture and organize technical skills from GitHub repositories. Use these instructions to analyze repositories and extract valuable skill information.

#### 🎯 Analysis Objectives

When analyzing a GitHub repository, your goal is to:

1. **Identify Technical Skills**: Extract concrete technical competencies demonstrated in the codebase
2. **Categorize by Domain**: Organize skills into appropriate categories (software, hardware, creative, research)
3. **Document Systematically**: Create consistent, comprehensive skill records
4. **Maintain Quality**: Ensure all records follow the established template structure

#### 📂 Repository Structure

```
SkillSphere/
├── ingestion_docs/
│   ├── skills/                    # All skill documentation
│   │   ├── software/             # Programming & technical skills
│   │   ├── hardware/             # Physical systems & electronics
│   │   ├── creative/             # Design & multimedia skills
│   │   └── research/             # Self-directed learning & experiments
│   ├── jobs/                     # Professional experience records
│   ├── certs/                    # Certification documentation
│   └── extras/                   # Additional context files
├── templates/
│   ├── complementary_skills_template.md     # Main skill documentation template
│   └── complementary_skills_quick_reference.md  # YAML metadata reference
└── docs/                         # Architecture & system documentation
```

#### 🔍 Skill Extraction Process

##### Step 1: Repository Analysis

* Analyze README.md, architecture documentation, and pyproject.toml/package.json
* Identify programming languages, frameworks, databases, and deployment technologies
* Look for unique or advanced technical implementations
* Note any custom solutions or sophisticated integrations

##### Step 2: Skill Categorization

Use this decision matrix:

| Category | Criteria | Examples |
|----------|----------|----------|
| **software/** | Programming, APIs, databases, cloud, DevOps | Python, FastAPI, Neo4j, Docker, Kubernetes |
| **hardware/** | Physical systems, electronics, embedded | PCB design, 3D printing, IoT, embedded systems |
| **creative/** | Design, multimedia, content creation | Video editing, graphic design, documentation |
| **research/** | Experiments, prototypes, learning projects | ML research, proof-of-concepts, explorations |

##### Step 3: Prioritization Framework

* **High Priority**: Core technologies central to the project's functionality
* **Medium Priority**: Supporting technologies that enable the main features
* **Low Priority**: Configuration tools and standard development utilities

##### Step 4: Documentation Creation

For each identified skill, create a comprehensive record using the template structure.

#### 📝 Template Usage

**Primary Template**: `templates/complementary_skills_template.md`

* Use this for full skill documentation
* Include all sections: Overview, Learning Journey, Projects, Competencies
* Focus on transferable skills and professional relevance

**Quick Reference**: `templates/complementary_skills_quick_reference.md`

* Contains YAML metadata structure for each skill
* Use for consistent categorization and tagging
* Update when adding new skills

#### 📋 File Naming Convention

Use descriptive filenames that include the main technology:

**Software Skills:**

* `neo4j-hypergraphs.md` (database + specific application)
* `fastapi-web-services.md` (framework + application type)
* `docker-orchestration.md` (tool + specific use case)

**Hardware Skills:**

* `pcb-design-kicad.md` (skill + primary tool)
* `3d-printing-bambulab.md` (process + specific equipment)

**Creative Skills:**

* `video-editing-davinci.md` (skill + software)
* `technical-writing-documentation.md` (skill + application)

#### 🔧 Quality Standards

**Required Information:**

* Technical depth and complexity level
* Specific tools and technologies used
* Practical projects or implementations
* Professional relevance and transferability
* Learning progression and current proficiency

**Metadata Requirements:**

```yaml
title: "Clear, Descriptive Skill Name"
type: "software_skill|hardware_skill|creative_skill|research_skill"
category: "specific_domain"
entity_id: "skill_unique_identifier"
primary_tools: ["Tool1", "Tool2", "Tool3"]
technologies: ["Tech1", "Tech2", "Tech3"]
competencies: ["skill1", "skill2", "skill3"]
```

#### 🎯 LLM Analysis Prompt Template

Use this prompt structure for repository analysis:

```markdown
Analyze this GitHub repository and extract technical skills for documentation:

1. **Repository Assessment**: Examine the codebase, documentation, and dependencies
2. **Skill Identification**: Identify 3-5 high-priority technical skills demonstrated
3. **Categorization**: Determine the appropriate category (software/hardware/creative/research)
4. **Documentation**: Create comprehensive skill records using the provided template
5. **Integration**: Update the quick reference with new skill metadata

Focus on:
- Advanced or specialized technical implementations
- Technologies central to the project's core functionality
- Skills that demonstrate professional-level competency
- Unique combinations of technologies or innovative approaches

Create detailed documentation that showcases technical depth and practical application.
```

#### 📊 Integration with SkillSphere System

Documented skills are processed by the hypergraph system to:

* Create semantic connections between related competencies
* Generate job-specific résumé content
* Identify skill gaps and learning opportunities
* Demonstrate continuous learning and technical growth

The hypergraph processes markdown files to extract entities, relationships, and competency mappings for intelligent career intelligence.

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
