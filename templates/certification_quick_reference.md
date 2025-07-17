# Certification Template Quick Reference

## Common Entity ID Patterns

```yaml
# Cloud Computing
cert_aws_sa_associate          # AWS Solutions Architect Associate
cert_aws_ml_specialty          # AWS Machine Learning Specialty
cert_azure_architect           # Azure Solutions Architect
cert_gcp_architect             # Google Cloud Architect

# Machine Learning / AI
cert_stanford_ml               # Stanford Machine Learning
cert_deeplearning_ai           # DeepLearning.AI Specialization
cert_tensorflow_dev            # TensorFlow Developer
cert_pytorch_cert              # PyTorch Certification

# Data Science
cert_michigan_data_science     # Michigan Data Science
cert_coursera_data_analyst     # Coursera Data Analyst
cert_tableau_desktop           # Tableau Desktop Specialist
cert_power_bi_analyst          # Power BI Data Analyst

# Enterprise Architecture
cert_togaf_9                   # TOGAF 9 Certified
cert_zachman_framework         # Zachman Framework
cert_open_ca                   # Open CA Certification

# Agile / Project Management
cert_scrum_master              # Scrum Master Certification
cert_pmp                       # Project Management Professional
cert_safe_agilist              # SAFe Agilist
cert_kanban_management         # Kanban Management

# Security
cert_cissp                     # CISSP
cert_ceh                       # Certified Ethical Hacker
cert_security_plus             # CompTIA Security+
cert_aws_security              # AWS Security Specialty
```

## Common Category Values

```yaml
category: "cloud_computing"          # AWS, Azure, GCP
category: "machine_learning"         # ML, AI, data science
category: "enterprise_architecture"  # TOGAF, Zachman
category: "agile_methodology"        # Scrum, Kanban, SAFe
category: "data_science"            # Analytics, statistics
category: "security"                # InfoSec, cybersecurity
category: "project_management"      # PMP, Prince2
category: "software_development"    # Programming, frameworks
category: "data_engineering"        # ETL, pipelines, big data
category: "devops"                  # CI/CD, infrastructure
```

## Status Templates

```yaml
# Active certification
status: "active"
issued_date: "2024-03-15"
expiry_date: "2027-03-15"

# Lifetime certification
status: "lifetime"
issued_date: "2024-03-15"
expiry_date: null

# Expired certification
status: "expired"
issued_date: "2021-03-15"
expiry_date: "2024-03-15"

# In progress
status: "in_progress"
issued_date: null
expiry_date: null
target_date: "2025-12-31"
progress_percentage: 65

# Planned
status: "planned"
issued_date: null
expiry_date: null
target_date: "2026-06-30"
```

## Common Technology Arrays

```yaml
# Cloud Computing
technologies: ["AWS", "EC2", "S3", "VPC", "CloudFormation", "Lambda"]
technologies: ["Azure", "Virtual Machines", "Storage", "Networking", "ARM Templates"]
technologies: ["GCP", "Compute Engine", "Cloud Storage", "BigQuery", "Kubernetes"]

# Machine Learning
technologies: ["Python", "TensorFlow", "scikit-learn", "Jupyter", "NumPy", "pandas"]
technologies: ["R", "Statistics", "Data Visualization", "Machine Learning", "Deep Learning"]
technologies: ["PyTorch", "Neural Networks", "Computer Vision", "NLP", "MLOps"]

# Data Science
technologies: ["Python", "SQL", "Tableau", "Power BI", "Excel", "Statistics"]
technologies: ["Spark", "Hadoop", "Kafka", "Airflow", "Docker", "Kubernetes"]

# Enterprise Architecture
technologies: ["TOGAF", "Enterprise Architecture", "ADM", "Business Architecture"]
technologies: ["ArchiMate", "BPMN", "UML", "System Design", "Strategy"]
```

## Common Competency Arrays

```yaml
# Technical Competencies
competencies: ["solution_architecture", "cloud_design", "cost_optimization"]
competencies: ["machine_learning", "data_analysis", "statistical_modeling"]
competencies: ["enterprise_architecture", "business_analysis", "strategy"]
competencies: ["agile_methodology", "team_leadership", "continuous_improvement"]

# Business Competencies
competencies: ["project_management", "stakeholder_engagement", "risk_management"]
competencies: ["business_intelligence", "data_visualization", "reporting"]
competencies: ["process_optimization", "change_management", "governance"]
```

## Issuer ID Patterns

```yaml
issuer_id: "aws"                    # Amazon Web Services
issuer_id: "microsoft"              # Microsoft
issuer_id: "google"                 # Google Cloud
issuer_id: "stanford_coursera"      # Stanford University on Coursera
issuer_id: "michigan_coursera"      # University of Michigan on Coursera
issuer_id: "open_group"             # The Open Group
issuer_id: "scrum_institute"        # International Scrum Institute
issuer_id: "pmi"                    # Project Management Institute
issuer_id: "comptia"                # CompTIA
issuer_id: "isc2"                   # (ISC)² International
```

## Quick Template Commands

```bash
# Create new certification
cp templates/certification_template.md ingestion_docs/certs/[cert-name].md

# Common patterns
cp templates/certification_template.md ingestion_docs/certs/aws-data-engineer.md
cp templates/certification_template.md ingestion_docs/certs/azure-ai-engineer.md
cp templates/certification_template.md ingestion_docs/certs/gcp-ml-engineer.md
cp templates/certification_template.md ingestion_docs/certs/pmp-certification.md
cp templates/certification_template.md ingestion_docs/certs/cissp-certification.md
```
