# Professional Certifications Directory

This directory contains individual certification files that are optimized for processing and ingestion into the SkillSphere hypergraph system. Each certification is stored as a separate Markdown file with structured metadata and comprehensive content.

## Directory Structure

```
certs/
├── README.md                              # This file
├── aws-solutions-architect-associate.md   # AWS Solutions Architect (Expired)
├── togaf-9-certified.md                   # TOGAF 9 Certified (Lifetime)
├── machine-learning-stanford.md           # Stanford ML Course (Lifetime)
├── scrum-master-accredited.md             # Scrum Master Certification (Lifetime)
├── data-science-python-michigan.md        # Michigan Data Science (Lifetime)
├── deloitte-data-analytics-simulation.md  # Deloitte Analytics (Lifetime)
├── aws-ml-specialty-in-progress.md        # AWS ML Specialty (In Progress)
└── azure-solutions-architect-planned.md   # Azure Solutions Architect (Planned)
```

## File Structure

Each certification file follows a consistent structure optimized for hypergraph processing:

### YAML Front Matter

```yaml
---
title: "Certification Name"
type: "professional_certification|certification_in_progress|certification_planned"
category: "domain_area"
entity_id: "unique_identifier"
status: "active|expired|lifetime|in_progress|planned"
issued_date: "YYYY-MM-DD"
expiry_date: "YYYY-MM-DD|null"
issuer: "Organization Name"
issuer_id: "organization_identifier"
technologies: ["tech1", "tech2", ...]
competencies: ["skill1", "skill2", ...]
last_updated: "YYYY-MM-DD"
---
```

### Content Structure

1. **Certification Overview** - Summary and significance
2. **Verification & Credentials** - Links and credential IDs
3. **Core Competencies** - Technical skills and knowledge areas
4. **Practical Application** - Real-world experience and projects
5. **Business Value** - Impact and career significance
6. **Related Experience** - Context and connections

## Processing Benefits

### Hypergraph Optimization

- **Individual Files:** Each certification is processed independently
- **Change Detection:** SHA-256 hashing tracks individual file changes
- **Chunking:** 1,500-word windows with 200-word overlap work better with focused content
- **Embedding:** FAISS embeddings are more precise with single-topic documents
- **Gleaning:** LLM triple extraction is more accurate with structured, focused content

### Metadata Richness

- **Structured Data:** YAML front matter provides consistent metadata
- **Entity Relationships:** Clear connections between certifications, skills, and technologies
- **Temporal Information:** Dates enable timeline and progression analysis
- **Status Tracking:** Current, expired, and planned certifications are distinguished
- **Categorization:** Domain-based grouping for better organization

## Status Categories

| Status | Description | Example |
|--------|-------------|---------|
| `active` | Currently valid, requires renewal | AWS certifications |
| `expired` | Previously valid, now expired | Expired AWS Solutions Architect |
| `lifetime` | Permanently valid, no renewal required | TOGAF, Stanford ML |
| `in_progress` | Currently studying, exam scheduled | AWS ML Specialty |
| `planned` | Future goal, not yet started | Azure Solutions Architect |

## Entity Relationships

### Technologies

Each certification maps to specific technologies, enabling skill clustering and technology expertise tracking.

### Competencies

Core competencies create skill hierarchies and enable competency-based filtering and search.

### Issuers

Issuer organizations create authoritative sources and enable credential verification.

### Categories

Domain categories enable subject matter expertise grouping and career path analysis.

## Migration Notes

This structure replaces the single `certifications.md` file with:

- **Better Processing:** Each file is independently processed for changes
- **Improved Accuracy:** Focused content improves LLM gleaning results
- **Enhanced Search:** Individual embeddings enable more precise retrieval
- **Easier Maintenance:** Updates to individual certifications don't affect others
- **Better Organization:** Clear separation of current, expired, and planned certifications

## Usage Guidelines

### For AI/Automation Systems

**IMPORTANT:** When generating any external document (CV, client profile, website):

1. **Export Only Active/Lifetime:** Use `status: active|lifetime` for external documents
2. **Label In-Progress:** In-progress/planned items may be exported **only** if clearly labelled "(In Progress, ETA YYYY-MM)" — they must never be shown as completed
3. **Respect Privacy:** `planned` certifications are internal goals only and MUST NOT be shown as earned credentials
4. **Preserve Metadata:** Maintain YAML front matter for downstream processing
5. **Preserve ISO-8601 Dates:** Downstream scripts parse them for timeline analysis
6. **Link Verification:** Ensure credential URLs remain accessible for verification

### For Human Readers

- Each file is self-contained and human-readable
- Front matter provides quick overview of certification details
- Structured content enables easy scanning and reference
- Related experience sections provide context and connections

## Future Enhancements

- **Automated Renewal Tracking:** Calendar integration for certification renewals
- **Competency Mapping:** Skill progression visualization and gap analysis
- **Credential Verification:** Automated verification of credential status
- **Learning Path Recommendations:** Suggested certifications based on career goals
- **Performance Analytics:** Certification impact on career progression metrics

## Template Usage

For creating new certification files, use the standardized template:

```bash
# Copy the template
cp ../../templates/certification_template.md [new-certification-name].md

# Edit with certification details
# Remove template usage notes
# Test with hypergraph ingestion
```

See `../../templates/CERTIFICATION_TEMPLATE_GUIDE.md` for detailed usage instructions and best practices.
