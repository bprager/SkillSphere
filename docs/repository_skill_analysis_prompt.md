# Repository Skill Analysis Prompt

## Instructions for LLM Assistants

Use this prompt template when analyzing a GitHub repository to extract technical skills for documentation in the SkillSphere system.

## Primary Analysis Prompt

```
# GitHub Repository Skill Extraction Task

## Context
You are analyzing a GitHub repository to extract technical skills for documentation in the SkillSphere career intelligence system. Your goal is to identify 3-5 high-priority technical skills demonstrated in the codebase and create comprehensive documentation.

## Repository Information
- Repository: [REPOSITORY_URL/NAME]
- Primary Language: [LANGUAGE]
- Project Type: [PROJECT_TYPE]

## Analysis Process

### Step 1: Repository Assessment
1. Examine README.md, architecture documentation, and configuration files
2. Identify core technologies, frameworks, and design patterns
3. Assess technical complexity and sophistication level
4. Note any innovative or advanced implementations

### Step 2: Skill Identification
Using the priority framework:
- **High Priority**: Core functionality, advanced implementations, unique solutions
- **Medium Priority**: Supporting technologies, well-implemented standard features
- **Low Priority**: Configuration tools, standard development utilities

Focus on technologies that demonstrate:
- Advanced or specialized technical implementations
- Core project functionality and architecture
- Professional-level competency and expertise
- Unique combinations of technologies or innovative approaches

### Step 3: Skill Categorization
Categorize each identified skill:
- **software/**: Programming, APIs, databases, DevOps, cloud platforms
- **hardware/**: Electronics, embedded systems, IoT, manufacturing
- **creative/**: Technical documentation, UI/UX, multimedia, visualization
- **research/**: Experimental implementations, prototypes, learning projects

### Step 4: Documentation Creation
For each identified skill, create comprehensive documentation using the provided template structure.

## Required Deliverables

1. **Skill Analysis Summary**: List of 3-5 identified skills with priority levels
2. **Detailed Documentation**: Complete skill files using the template
3. **Quick Reference Updates**: YAML metadata for each new skill
4. **File Organization**: Proper directory placement and naming

## Template Structure Requirements

Each skill file must include:
- Complete YAML frontmatter with metadata
- Skill overview and learning journey
- Tools & technologies with proficiency levels
- Project examples from the repository
- Competencies developed and professional relevance
- Future development plans

## Quality Standards

- Technical depth demonstrates advanced usage
- Specific project examples from the repository
- Clear connection to professional applications
- Proper categorization and metadata
- Comprehensive tool and technology coverage
- Evidence of learning progression and growth

## File Naming Convention

Use descriptive filenames:
- `{technology}-{application}.md`
- Examples: `neo4j-hypergraphs.md`, `docker-orchestration.md`, `fastapi-microservices.md`

## Expected Output Format

For each skill, provide:
1. Filename and directory location
2. Complete skill documentation following the template
3. YAML metadata for quick reference integration
4. Brief justification for inclusion and categorization

Begin your analysis now.
```

## Example Usage

Replace the bracketed placeholders with actual repository information:

```
# GitHub Repository Skill Extraction Task

## Context
You are analyzing a GitHub repository to extract technical skills for documentation in the SkillSphere career intelligence system. Your goal is to identify 3-5 high-priority technical skills demonstrated in the codebase and create comprehensive documentation.

## Repository Information
- Repository: https://github.com/bprager/SkillSphere-Agent
- Primary Language: Python
- Project Type: AI/ML Infrastructure - MCP Server with Neo4j Hypergraph

## Analysis Process
[Continue with the standard process...]
```

## Follow-up Prompts

### For Additional Context

```
Please analyze the following specific files for additional technical details:
- [FILE_PATH_1]: [REASON_FOR_ANALYSIS]
- [FILE_PATH_2]: [REASON_FOR_ANALYSIS]

Focus on identifying any additional technical skills or deepening the understanding of already identified skills.
```

### For Skill Refinement

```
Based on your initial analysis, please refine the skill documentation for [SKILL_NAME] by:
1. Adding more specific technical details from the codebase
2. Providing concrete examples of implementation
3. Clarifying the professional relevance and transferability
4. Ensuring all template sections are comprehensively filled
```

### For Quality Assurance

```
Please review the created skill documentation and ensure:
1. All template sections are complete and meaningful
2. Technical accuracy and depth are appropriate
3. Professional relevance is clearly demonstrated
4. YAML metadata is properly formatted
5. File naming and organization follow conventions
```

## Integration Instructions

After skill extraction:

1. **File Creation**: Create skill files in appropriate directories
2. **Quick Reference Update**: Add YAML metadata to `templates/complementary_skills_quick_reference.md`
3. **Documentation Review**: Ensure all quality standards are met
4. **System Integration**: Verify proper formatting for hypergraph processing

This systematic approach ensures consistent, high-quality skill documentation that effectively captures technical expertise and supports career intelligence objectives.
