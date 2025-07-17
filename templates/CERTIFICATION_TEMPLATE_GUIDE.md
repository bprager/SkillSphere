# Certification Template Usage Guide

## Overview

The `certification_template.md` file provides a standardized format for creating new certification records that are optimized for the SkillSphere hypergraph system. This template ensures consistency, proper metadata structure, and effective processing.

## Quick Start

1. **Copy the template:**
   ```bash
   cp templates/certification_template.md ingestion_docs/certs/[new-cert-name].md
   ```

2. **Update the YAML front matter** with certification details

3. **Fill in the content sections** with specific information

4. **Remove the template usage notes** at the bottom

5. **Test the file** with the hypergraph ingestion system

## YAML Front Matter Guide

### Required Fields

```yaml
title: "AWS Certified Solutions Architect - Associate"
type: "professional_certification"
category: "cloud_computing"
entity_id: "cert_aws_sa_associate"
status: "active"
issued_date: "2024-03-15"
expiry_date: "2027-03-15"
issuer: "Amazon Web Services"
issuer_id: "aws"
technologies: ["AWS", "Cloud Architecture", "EC2", "S3", "VPC"]
competencies: ["solution_architecture", "cloud_design", "cost_optimization"]
last_updated: "2025-07-16"
```

### Optional Fields

```yaml
credential_id: "ABC123XYZ789"           # For completed certifications
target_date: "2025-12-31"              # For in-progress/planned
study_start_date: "2025-06-01"         # For in-progress
progress_percentage: 65                 # For in-progress
instructor: "John Smith"                # For course-based certifications
platform: "Coursera"                   # For online certifications
duration_hours: 40                      # For course-based certifications
```

## Field Guidelines

### Entity ID Format
- **Prefix:** Always start with `cert_`
- **Format:** Use lowercase with underscores
- **Uniqueness:** Ensure each ID is unique across all certifications
- **Examples:**
  - `cert_aws_sa_associate`
  - `cert_togaf_9`
  - `cert_stanford_ml`
  - `cert_scrum_master`

### Status Values
- **`active`** - Currently valid, requires renewal
- **`expired`** - Previously valid, now expired
- **`lifetime`** - Permanently valid, no renewal required
- **`in_progress`** - Currently studying, exam scheduled
- **`planned`** - Future goal, not yet started

### Category Examples
- **`cloud_computing`** - AWS, Azure, GCP certifications
- **`machine_learning`** - ML, AI, data science certifications
- **`enterprise_architecture`** - TOGAF, Zachman, etc.
- **`agile_methodology`** - Scrum, Kanban, SAFe, etc.
- **`data_science`** - Analytics, statistics, data engineering
- **`security`** - InfoSec, cybersecurity, compliance
- **`project_management`** - PMP, Prince2, etc.
- **`software_development`** - Programming, frameworks, tools

### Technologies Array
- Use consistent naming (e.g., "Python" not "python")
- Include both broad and specific technologies
- Focus on key technologies covered by the certification
- Examples: `["Python", "TensorFlow", "scikit-learn", "Jupyter"]`

### Competencies Array
- Focus on transferable skills and capabilities
- Use underscores for multi-word competencies
- Examples: `["solution_architecture", "machine_learning", "data_analysis"]`

## Content Structure Guide

### 1. Certification Overview
- **Purpose:** Explain what the certification demonstrates
- **Significance:** Describe its recognition and value in the industry
- **Difficulty:** Indicate the level of expertise required

### 2. Verification & Credentials
- **Credential ID:** Unique identifier for the certification
- **Verification URL:** Direct link to verification page
- **Status:** Current status with relevant dates

### 3. Core Competencies
- **Organize by domain:** Group related skills together
- **Be specific:** Describe actual capabilities, not just topics
- **Use bullet points:** For easy scanning and processing

### 4. Practical Application
- **Real examples:** Describe specific projects or applications
- **Measurable outcomes:** Include quantifiable results when possible
- **Business context:** Explain how the knowledge was applied

### 5. Business Value
- **Professional impact:** How the certification advances career goals
- **Organizational benefit:** Value to employers or clients
- **Industry recognition:** Credibility and expertise demonstration

### 6. Related Experience
- **Connections:** Link to other certifications, projects, or roles
- **Progression:** Show how this fits into broader career development
- **Applications:** Describe where the knowledge has been used

## Special Cases

### In-Progress Certifications
- Set `issued_date` to `null`
- Add `target_date` field
- Include study progress and resources
- Update progress regularly

### Planned Certifications
- Set both `issued_date` and `expiry_date` to `null`
- Focus on learning objectives and preparation plan
- Include prerequisites and timeline

### Expired Certifications
- Keep original `issued_date` and `expiry_date`
- Set status to `expired`
- Consider including renewal plans if applicable

## Best Practices

### Consistency
- Use the same format across all certifications
- Follow naming conventions for fields and values
- Maintain consistent section structure

### Accuracy
- Verify all URLs and credential IDs
- Keep dates in ISO-8601 format (YYYY-MM-DD)
- Update `last_updated` field when making changes

### Optimization
- Write for both human readers and AI processing
- Include relevant keywords naturally
- Structure content for easy scanning

### Maintenance
- Review and update certification files regularly
- Check for expired URLs or credentials
- Update progress for in-progress certifications

## Integration with Hypergraph System

### Processing Benefits
- **Individual files** are processed independently
- **YAML front matter** provides structured metadata
- **Consistent format** improves LLM gleaning accuracy
- **Entity relationships** enable better graph connections

### Search Optimization
- **Technologies** enable skill-based filtering
- **Competencies** support capability searches
- **Categories** allow domain-specific queries
- **Status** enables current vs. historical views

### Timeline Analysis
- **Issued dates** support career progression tracking
- **Expiry dates** enable renewal planning
- **Status tracking** shows certification lifecycle

## Example Usage

```bash
# Create a new certification file
cp templates/certification_template.md ingestion_docs/certs/azure-data-engineer.md

# Edit the file with certification details
# Remove template usage notes
# Test with hypergraph ingestion

# Verify the file structure
head -20 ingestion_docs/certs/azure-data-engineer.md
```

## Validation Checklist

Before finalizing a new certification file:

- [ ] YAML front matter is complete and valid
- [ ] Entity ID is unique and follows format
- [ ] Status matches the certification's current state
- [ ] All URLs are functional and verifiable
- [ ] Technologies and competencies are accurate
- [ ] Content sections are complete and relevant
- [ ] Template usage notes are removed
- [ ] File is tested with hypergraph ingestion
- [ ] `last_updated` field is current

This template system ensures that all certification records maintain consistency while providing the rich metadata and structure needed for optimal hypergraph processing.
