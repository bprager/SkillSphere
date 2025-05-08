---
job_id: senior_tech_architect_sp_ratings_2008_2016
role: Senior Technical Architect / Chief Enterprise Architect
company: Standard & Poor’s (later S&P Global Ratings)
start_date: "2008-02"
end_date: "2016-09"
location: New York, NY, USA
---

# Senior Technical Architect / Chief Enterprise Architect
**Standard & Poor’s (S&P Global Ratings)**
New York, NY | February 2008 – September 2016

## Summary
Owned the end-to-end enterprise-architecture vision for S&P Global Ratings during a period of intense regulatory scrutiny and rapid model innovation. Re-built the EA practice, modernised the credit-risk modelling stack (CreditModel™, CM 3.0, Monte-Carlo engines), and steered the first wave of AWS migrations—laying the groundwork for highly governed, “four-nines”‐available model-risk platforms that analysts still rely on today. :contentReference[oaicite:0]{index=0}

## Responsibilities
- Established an **Architecture Council** that vetted all $1 M+ initiatives, with special focus on model lifecycle governance and SR 11-7/SEC compliance. :contentReference[oaicite:1]{index=1}
- Defined a global **Model SDLC** reference—source-controlled code, independent model-validation environments, automated performance back-testing, and audit-grade lineage.
- Led the design of a **petabyte-scale Risk & Market-Data Lake** (Oracle Exadata → S3/Redshift) powering CreditModel™ and Monte Carlo CDO simulators.
- Piloted and documented the AWS landing-zone blueprint adopted for ratings analytics workloads, using VMware Cloud on AWS for “lift-and-shift” phases. :contentReference[oaicite:2]{index=2}
- Directed vendor selection for analytics grids (GridGain/Hazelcast), GPU clusters, and risk-data feeds; negotiated board-level contracts.
- Mentored 10 direct EAs and ~30 solution architects across New York, London, Tokyo, Mumbai, and Melbourne.

## Achievements
- **Unified model-risk architecture** → 30 % faster back-testing cycles and 25 % fewer late regulatory findings.
- Migrated two mission-critical ratings pipelines (CMBS & Corporate Ratings) to AWS, realising 40 % infra-cost savings and 100 % uptime on regulatory portals. :contentReference[oaicite:3]{index=3}
- Published 150+ reusable Architecture Decision Records and automated compliance gates in CI/CD, trimming project onboarding by 35 % and eliminating $4 M/yr of duplicate spend.
- Sponsored the adoption of CreditModel™ Corporates 3.0 & Financial-Institutions models—scaling coverage to 50 k+ entities and delivering early-warning dashboards for analysts. :contentReference[oaicite:4]{index=4}

## Significant Projects
### Ratings Model Management Platform (RMMP)
End-to-end ModelOps stack for credit-risk & market-risk engines.
- **Pipeline**: Git-based model source → Jenkins CI → automated validation suite → containerised deployment on AWS ECS/Fargate.
- **Governance**: embedded SR 11-7 controls—versioned datasets, challenger-model harness, and independent review checkpoints.
- **Outcome**: Cut model release cycle from 90 → 30 days; passed first SEC post-settlement audit with zero material findings. :contentReference[oaicite:5]{index=5}

### Historical & Stress-Testing Data Lake
Petabyte-scale repository combining 20 yrs of issuer financials, macro factors, and market data.
- Ingested 3 TB/day via Kinesis; partitioned in Parquet @ S3; queried with Redshift Spectrum for ad-hoc Monte-Carlo stress runs.
- Enabled 30 % faster scenario analysis for sovereign & structured-finance models.

## AI & Machine-Learning Contributions
- **AI Scope** Industrialised statistical credit-risk models (CreditModel™ FI & Corporates 3.0) and market-risk VaR engines within a governed ModelOps framework. :contentReference[oaicite:6]{index=6}
- **Techniques / Models** Logistic-regression and gradient-boosting scorecards, time-series anomaly detection for ratings drift, GPU-accelerated Monte-Carlo CDO pricing.
- **Datasets & Tooling** > 50 M quarterly financial statements; Bloomberg & Reuters market feeds; Spark/Hive ETL; TensorFlow for prototype R&D.
- **Impact Metrics** Cut analyst model-run time from 4 h → 40 min; delivered 15 % earlier watch-list flags (back-tested 2000-2015).
- **Leadership & Collaboration** Chaired cross-functional **Model Governance Forum**; partnered with Market Intelligence to align CreditModel™ releases with Ratings criteria.
- **Continuous Learning** Completed AWS Certified Data Analytics and GARP “Model Risk Management” courses; ran internal workshops on scalable ModelOps patterns.

## Skills
- Enterprise architecture & governance
- Model-risk management (SR 11-7)
- Cloud migration & hybrid architecture (AWS / VMware Cloud)
- Data-lake & HPC design
- Model SDLC / DevSecOps
- Regulatory engagement & board communication

## Technologies
- **Cloud** AWS (EC2, S3, Redshift, ECS/Fargate, KMS), VMware Cloud on AWS
- **Data** Oracle Exadata, PostgreSQL, Hadoop/Spark, Hive, Parquet
- **Compute** GridGain/Hazelcast IMDG, CUDA/GPU clusters
- **Languages** Java 7/8, Python 2.7/3.x, Scala, PL/SQL
- **CI/CD** Jenkins, Artifactory, Terraform, CloudFormation
- **Analytics** CreditModel™ FI / CM 3.0, TensorFlow, R

## Lessons Learned
- Robust ModelOps and transparent governance are non-negotiable for credibility in regulated analytics.
- Cloud elasticity + infrastructure-as-code unlock both cost savings and faster model experimentation.
- Cross-disciplinary architecture councils create shared ownership and reduce “shadow IT” in modelling teams.

