# LLM Skill Extraction Instructions

## Purpose

This document provides specific instructions for LLM assistants to analyze GitHub repositories and extract technical skills for documentation in the SkillSphere system.

## Repository Analysis Workflow

### Phase 1: Discovery & Assessment

1. **Initial Repository Survey**
   * Read README.md, architecture documentation, and primary configuration files
   * Identify project type, main technologies, and architectural patterns
   * Assess complexity level and technical sophistication

2. **Dependency Analysis**
   * Examine `pyproject.toml`, `package.json`, `requirements.txt`, or equivalent
   * Identify frameworks, libraries, and development tools
   * Note version constraints and specialized dependencies

3. **Code Structure Review**
   * Analyze directory structure and file organization
   * Identify design patterns and architectural decisions
   * Look for custom implementations and innovative solutions

### Phase 2: Skill Identification

#### Technology Mapping

Use this framework to identify skill-worthy technologies:

| Priority | Criteria | Action |
|----------|----------|---------|
| **High** | Core project functionality, advanced implementations, unique solutions | Document immediately |
| **Medium** | Supporting technologies, standard but well-implemented features | Consider for documentation |
| **Low** | Configuration tools, standard development utilities | Usually skip |

#### Skill Categories

**Software Skills** (`ingestion_docs/skills/software/`)

* Programming languages with advanced usage
* Frameworks and libraries with sophisticated implementations
* Database technologies and query optimization
* Cloud platforms and deployment strategies
* DevOps tools and CI/CD pipelines
* API design and microservices architecture

**Hardware Skills** (`ingestion_docs/skills/hardware/`)

* Embedded systems and IoT implementations
* Electronics design and PCB development
* 3D printing and manufacturing processes
* System architecture and hardware optimization

**Creative Skills** (`ingestion_docs/skills/creative/`)

* Technical documentation and writing
* User interface and experience design
* Video editing and multimedia production
* Graphic design and visualization

**Research Skills** (`ingestion_docs/skills/research/`)

* Experimental implementations and prototypes
* Self-directed learning projects
* Technology evaluation and comparison
* Innovation and proof-of-concept development

### Phase 3: Documentation Creation

#### File Naming Standards

Follow these patterns for consistency:

```
software/
├── {technology}-{application}.md
├── neo4j-hypergraphs.md
├── fastapi-microservices.md
├── docker-orchestration.md
└── kubernetes-deployment.md

hardware/
├── {process}-{tool}.md
├── pcb-design-kicad.md
├── 3d-printing-prusa.md
└── arduino-prototyping.md
```

#### Required Documentation Elements

**YAML Frontmatter** (from template)

```yaml
title: "Technology Name & Application"
type: "software_skill|hardware_skill|creative_skill|research_skill"
category: "specific_domain"
entity_id: "skill_unique_identifier"
status: "active"
start_date: "YYYY-MM-DD"
proficiency_level: "beginner|intermediate|advanced|expert"
primary_tools: ["Tool1", "Tool2", "Tool3"]
technologies: ["Tech1", "Tech2", "Tech3"]
competencies: ["skill1", "skill2", "skill3"]
```

**Content Structure**

1. **Skill Overview**: Clear description of the technology and its application
2. **Learning Journey**: How the skill was acquired and developed
3. **Tools & Technologies**: Specific tools and their usage levels
4. **Projects & Applications**: Concrete examples from the repository
5. **Competencies Developed**: Technical and transferable skills gained
6. **Professional Relevance**: How the skill applies to career contexts

#### Quality Checklist

* [ ] Technical depth demonstrates advanced usage
* [ ] Specific project examples from the repository
* [ ] Clear connection to professional applications
* [ ] Proper categorization and metadata
* [ ] Comprehensive tool and technology coverage
* [ ] Evidence of learning progression and growth

### Phase 4: Integration & Maintenance

#### Quick Reference Updates

After creating new skill files, update `templates/complementary_skills_quick_reference.md`:

```yaml
#### Technology Name & Application
```yaml
title: "Technology Name & Application"
type: "software_skill"
category: "specific_domain"
entity_id: "skill_unique_identifier"
primary_tools: ["Tool1", "Tool2", "Tool3"]
technologies: ["Tech1", "Tech2", "Tech3"]
competencies: ["skill1", "skill2", "skill3"]
```

#### Validation Steps

1. **Completeness Check**: Ensure all template sections are filled
2. **Technical Accuracy**: Verify technology descriptions and usage
3. **Professional Relevance**: Confirm career application potential
4. **Metadata Consistency**: Check YAML formatting and categorization
5. **File Organization**: Ensure proper directory placement and naming

## Common Skill Patterns

### Advanced Database Implementation

Example: Neo4j with Graph Data Science

* **Technical Depth**: Complex graph modeling, performance optimization
* **Projects**: Knowledge graph construction, recommendation systems
* **Competencies**: Graph theory, query optimization, data relationships

### Container Orchestration

Example: Docker Compose multi-service architecture

* **Technical Depth**: Service mesh configuration, networking, scaling
* **Projects**: Microservices deployment, development environments
* **Competencies**: DevOps practices, system architecture, automation

### API Development

Example: FastAPI with async programming

* **Technical Depth**: Async patterns, performance optimization, API design
* **Projects**: RESTful services, real-time applications, microservices
* **Competencies**: Backend development, system integration, performance tuning

## LLM Assistant Prompt Templates

### Repository Analysis Prompt

```
Analyze this GitHub repository for technical skill extraction:

Repository: [URL/Name]
Purpose: Extract 3-5 high-priority technical skills for documentation

Process:
1. Examine README.md, architecture docs, and dependency files
2. Identify advanced technical implementations
3. Assess professional relevance and transferability
4. Create comprehensive skill documentation using provided templates
5. Update quick reference with new skill metadata

Focus on technologies that demonstrate:
- Advanced or specialized implementations
- Core project functionality
- Professional-level competency
- Unique combinations or innovative approaches

Provide detailed documentation that showcases technical depth and practical application.
```

### Skill Documentation Prompt

```
Create comprehensive skill documentation for: {TECHNOLOGY}

From repository: {REPOSITORY_NAME}

Requirements:
- Use templates/complementary_skills_template.md structure
- Include specific project examples from the repository
- Demonstrate technical depth and professional relevance
- Provide proper YAML metadata and categorization
- Focus on transferable skills and career applications

Evidence to include:
- Code examples and implementations
- Technical challenges overcome
- Tools and technologies mastered
- Learning progression and growth
- Professional application potential
```

## Best Practices

### Technical Assessment

* **Depth over Breadth**: Focus on advanced usage rather than simple tool adoption
* **Evidence-Based**: Use specific code examples and project outcomes
* **Context Matters**: Consider the complexity and innovation of the implementation
* **Professional Relevance**: Emphasize skills that translate to career advancement

### Documentation Quality

* **Comprehensive Coverage**: Include all template sections with meaningful content
* **Specific Examples**: Use concrete project details and technical specifications
* **Professional Tone**: Write for technical audiences and career contexts
* **Consistent Structure**: Follow templates and naming conventions exactly

### System Integration

* **Metadata Accuracy**: Ensure proper YAML formatting and categorization
* **Quick Reference Updates**: Maintain consistency across all documentation
* **File Organization**: Use correct directory structure and naming patterns
* **Version Control**: Document changes and maintain update timestamps

This systematic approach ensures consistent, high-quality skill documentation that effectively captures technical expertise and professional development.
