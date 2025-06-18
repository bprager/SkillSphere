# SkillSphere Project Brief

## Project Overview
SkillSphere is a graph-powered talent intelligence platform that transforms scattered career information into a structured knowledge graph and generates ATS-ready résumés. The project aims to solve the problem of fragmented career data and generic CVs by providing a unified, intelligent solution.

## Core Requirements

### 1. Data Integration
- Convert career data from various sources (LinkedIn, slides, docs) into a Neo4j hypergraph
- Maintain a single source of truth for career information
- Support Markdown as the primary input format

### 2. Résumé Generation
- Generate job-specific résumé PDFs through graph queries
- Ensure ATS compatibility
- Support one-click generation

### 3. Privacy & Performance
- Run fully local on Ollama
- No external API key requirements
- Optimize for performance and privacy

### 4. Technical Requirements
- Python 3.10+ compatibility
- 100% unit-tested core modules
- Graph-powered architecture using Neo4j
- Node2Vec embeddings for semantic understanding

## Project Goals
1. Create a seamless experience for users to manage their career data
2. Provide intelligent, context-aware résumé generation
3. Maintain high performance and privacy standards
4. Demonstrate graph/AI capabilities through the codebase itself

## Success Metrics
- Successful conversion of career data to graph format
- Accurate and relevant résumé generation
- System performance and reliability
- Code quality and test coverage 