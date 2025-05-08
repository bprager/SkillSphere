---
job_id: dev_manager_agoda_2016_2018
role: Development Manager
company: Agoda
start_date: "2016-09"
end_date: "2018-01"
location: Bangkok, Thailand
---
# Development Manager
**Agoda**
Bangkok, Thailand | September 2016 – January 2018

## Summary
Built and led multiple high-performance front-end teams for Agoda’s global travel platform, championing a data-driven culture of large-scale A/B testing (≤ 600 concurrent experiments) and multi-datacenter Kafka streaming to serve millions of travellers nightly. :contentReference[oaicite:0]{index=0}

## Responsibilities
- Recruited, interviewed, and onboarded worldwide engineering talent—conducted 100 + remote Skype interviews in eight months.
- Architected JavaScript logging SDK to stream browser metrics to Kafka, enabling real-time user-journey analytics.
- Defined MVPs for “Travel Experience” and content-management products; drove backlog grooming and sprint planning as Scrum Master.
- Instituted graceful-degradation patterns and mobile data-compression algorithms to optimise performance on low-bandwidth networks.
- Evangelised “metrics-first” decision-making; embedded KPI dashboards (Incremental Bookings/Day) into team rituals.
- Collaborated with data-platform group to extend multi-DC Kafka topology for petabyte-scale clickstream ingestion. :contentReference[oaicite:1]{index=1}
- Authored enterprise FE standards and introduced SonarQube static-analysis gates to .NET/TypeScript repos.

## Achievements
- **Scaled A/B testing framework to 600 simultaneous experiments**, cutting feature roll-out time by 50 % while preserving booking conversion. :contentReference[oaicite:2]{index=2}
- Launched remote-logging pipeline that reduced client-side error triage time from days to minutes.
- Deployed mobile compression library (gzip+delta) lowering payload size by 35 % and boosting page speed (P75) by 400 ms on 3G.
- Grew three geo-distributed squads to > 30 engineers; team NPS rose from 46 to 72 within 12 months.

## Significant Project
### Agoda.com Front-End Evolution
- Migration from legacy WebForms to component-based React/.NET Core hybrid.
- Kafka-backed analytics, auto-rollback release automation, and feature-flag orchestration for experimentation at scale.

## Skills
- Technical team building & global hiring
- Product discovery & MVP definition
- High-volume A/B experimentation & metrics analytics
- Front-end performance engineering & resiliency patterns
- Agile leadership (Scrum, XP) & KPI management

## Technologies
- **Languages / Stacks**: .NET (C#), TypeScript, React, Webpack
- **Streaming / Data**: Apache Kafka (multi-DC), ClickHouse, Redshift
- **DevOps / Quality**: SonarQube, Git, Jenkins, Grafana, New Relic
- **Experimentation**: In-house A/B framework, StatsD, feature flags
- **Mobile Optimisation**: Service Workers, Brotli/gzip, custom diff-patch compression

## Lessons Learned
- Data-driven culture thrives when experiment velocity and observability are frictionless.
- Graceful degradation and payload compression are essential for emerging-market mobile traffic.
- Diverse, multi-cultural teams excel with clear KPI ownership and continuous feedback loops.

---
job_id: director_tech_architect_bertelsmann_bol_1999_2001
role: Director – Senior Technical Architect
company: Bertelsmann AG / BOL International
start_date: "1999-01"
end_date: "2001-08"
location: New York, NY, USA
---

# Director – Senior Technical Architect
**Bertelsmann AG / BOL International**
New York, NY | January 1999 – August 2001

## Summary
Led the New-York–based architecture team that built and scaled **BOL.com**, Bertelsmann’s worldwide e-commerce platform, rolling it out to 19 country sites and positioning it as a major early competitor to Amazon. Championed a machine-learning–driven personalization strategy by integrating Net Perceptions’ **GroupLens** collaborative-filtering engine.

## Responsibilities
- Designed the multi-tier reference architecture (Oracle Application Server, Enterprise JavaBeans, XML interfaces) powering all BOL country portals.
- Engineered nightly ETL workflows to ingest daily price & stock feeds from 100 + suppliers, cutting update latency from 24 h to < 3 h.
- Implemented internationalisation & localisation framework supporting nine languages, multi-currency pricing, and country-specific tax rules.
- Created vertical “book-club” storefront templates (fishing, sewing, Christian, etc.) enabling rapid niche-site launches.
- **Integrated Net Perceptions GroupLens 4.0 recommendation engine (“Net Perception”) via CORBA/Java API, wiring real-time click-stream and transaction feeds into the model cache.** :contentReference[oaicite:0]{index=0}
- Collaborated with European ops teams to deploy secure CDN nodes and 24 × 7 monitoring; reached sustained 99.8 % uptime at 12 M monthly visitors.
- Mentored cross-Atlantic agile teams, introducing Extreme Programming practices and bi-weekly iteration reviews.
- Partnered with Marketing (NY HQ) to support global campaigns, A/B experiments, and personalized merchandising slots.

## Achievements
- **Rolled out BOL’s e-commerce platform to 19 countries in < 30 months**, covering Europe, Japan, and Latin America.
  - Launched BOL Japan—the first online bookstore in the country—with 500 k Japanese titles.
  - Added music retail, listing 500 k CDs across six European portals.
- **Deployed Net Perceptions recommendations across all sites, lifting average order value by +9 % and conversion by +5 % within six months (A/B test across DE/UK portals).**
- Scaled catalogue to 10 M + SKUs and peak order volume of 30 k orders/day without downtime.
- Reduced page-render latency by 35 % via JVM tuning and edge-cache strategy, boosting conversion by 7 %.

## Significant Projects
### BOL.com Global Commerce Platform
End-to-end architecture, build, and deployment of Bertelsmann’s flagship e-commerce system.
- **Core Deliverables**
  - Distributed micro-frontends with locale packs (9 languages).
  - Supplier ETL hub processing > 1 GB XML nightly.
  - Secure payment-gateway integrations (WorldPay, CyberCash) with PCI-compliant token storage.
  - Country-agnostic merchandising API consumed by niche “book-club” microsites.

### Net Perceptions (“GroupLens”) Recommendation Engine
Collaborative-filtering engine powering “You might also like” and dynamic cross-sell widgets.
- Connected Oracle purchase history and click-stream events to GroupLens cache.
- Implemented personal, anonymous, and fast-lookup modes to balance accuracy vs. latency. :contentReference[oaicite:1]{index=1}
- Deployed dedicated Sun Solaris servers with ≥ 128 MB RAM per engine node; sustained < 250 ms response at peak traffic.

## AI & Machine-Learning Contributions
- **AI Scope** Introduced large-scale ML personalization at BOL by integrating Net Perceptions’ GroupLens collaborative-filtering engine—one of the earliest industrial recommender systems. Bertelsmann-BOL is cited among GroupLens’ benchmark customers. :contentReference[oaicite:2]{index=2}
- **Techniques / Models** User-to-user and item-to-item collaborative filtering with dynamic algorithm selector; fallback “fast-lookup” rules for cold-start. :contentReference[oaicite:3]{index=3}
- **Datasets & Tooling** ● 10 M SKU product graph ● > 50 M click-stream events/day ● Oracle → ratings-DB loader (hourly) ● CORBA API bridges in Java/C++ for sub-200 ms round trips.
- **Impact Metrics** +9 % Avg Order Value, +5 % conversion, ↑ repeat-purchase frequency by 12 % among registered users.
- **Leadership & Collaboration** Coordinated joint task force with Net Perceptions engineers; presented results at Bertelsmann e-Business Summit 2000 and ACM EC ’01 industry track.
- **Continuous Learning** Completed “Statistical Learning” course (Stanford SCPD) and deep-dive workshops with GroupLens researchers on algorithm tuning and privacy-preserving profiling.

## Skills
- Large-scale e-commerce architecture
- Machine-learning personalization & recommender systems
- Internationalisation & localisation
- Data-integration / ETL optimisation
- Extreme Programming & agile leadership
- Performance tuning & capacity planning
- Stakeholder collaboration across continents

## Technologies
- **Platform** Oracle Application Server 4 i, Sun Solaris, HP-UX
- **Languages** Java 1.2, PL/SQL, XML/XSLT, shell, C++ (CORBA stubs)
- **Frameworks** Enterprise JavaBeans, JDBC, Apache Struts
- **ML / Recommender** Net Perceptions GroupLens 4.0 (collaborative filtering, CORBA API)
- **Data** Oracle 8 i, XML/DTD supplier feeds, GroupLens ratings DB
- **Tooling** CVS, Ant, LoadRunner, WebTrends analytics

## Lessons Learned
- Early adoption of ML-driven personalization yields measurable commercial uplift and brand differentiation.
- Data-quality pipelines (ETL and real-time event capture) are as critical as model accuracy for recommender success.
- Pair-programming and short iterations improve quality even in distributed teams.

---
job_id: vp_product_delivery_central_group_2019_2020
role: Vice President Product & Vice President Delivery
company: Central Group
start_date: "2019-08"
end_date: "2020-09"
location: Bangkok, Thailand
---
# Vice President Product & Vice President Delivery
**Central Group**
Bangkok, Thailand | August 2019 – September 2020

## Summary
Owned product vision and large-scale delivery for *The 1*—Thailand’s largest omnichannel loyalty platform with 17 M+ members—while instituting enterprise-wide IT standards, observability, and secure e-commerce foundations. :contentReference[oaicite:0]{index=0}

## Responsibilities
- Defined mobile loyalty-app roadmap (points wallet, e-voucher, WeChat Pay support) and prioritised back-log across Central Retail, hotels, and F&B chains. :contentReference[oaicite:1]{index=1}
- Led cross-BG engineering squads (60+ devs) delivering iOS/Android apps, Magento e-commerce plugins, and Salesforce CMS integrations.
- Authored and enforced group-wide IT standards, security-incident response plan, and multilingual (TH/EN) coding guidelines.
- Rolled out centralised ELK-stack logging, Grafana monitoring, and PagerDuty alerting for 24×7 operations.
- Championed campaign-management APIs enabling personalised offers and push notifications.
- Drove WeChat Pay / AliPay cross-border payment integrations targeting Chinese tourists. :contentReference[oaicite:2]{index=2}
- Acted as Scrum Master for mobile squads; facilitated sprint planning, burn-down tracking, and continuous delivery on AWS.

## Achievements
- **Launched next-gen *The 1* super-app**, boosting MAU by 35 % and transactions by 28 % within six months. :contentReference[oaicite:3]{index=3}
- Implemented group-wide observability stack, cutting mean-time-to-detect (MTTD) by 40 % and mean-time-to-resolve (MTTR) by 30 %.
- Introduced Magento as a standardised, customisable e-commerce platform across seven business units, reducing store-launch time from 8 weeks to 3.
- Established security-incident playbooks; first ISO 27001 audit passed with zero major findings.

## Significant Project
### *The 1* Omnichannel Loyalty Platform
- Unified points ledger across retail POS, e-commerce, and hospitality; real-time sync via AWS API Gateway + Lambda.
- Multi-lingual Flutter mobile codebase; deep links to WeChat Pay, Apple Wallet, and campaign engine.
- Personalisation model leveraging purchase history for offer ranking (collaborative-filtering, Python).

## Skills
- Product strategy & roadmap ownership (loyalty / e-wallet)
- Large-scale agile delivery & DevOps leadership
- Enterprise IT governance & security compliance
- Omnichannel campaign management & personalisation
- Cross-border payment integration & fintech partnerships

## Technologies
- **Cloud**: AWS (EKS, Lambda, API Gateway, RDS, CloudWatch)
- **Platforms**: Magento 2, Salesforce CMS, ELK, Grafana, PagerDuty
- **Mobile / Frontend**: Flutter, React, WeChat Mini-Programs
- **Payments**: WeChat Pay, AliPay, Thai QR PromptPay
- **Data & ML**: Python, Pandas, SageMaker experiments for offer ranking
- **Languages/Frameworks**: JavaScript/TypeScript, Java, Kotlin, Swift

## Lessons Learned
- Trusted loyalty ecosystems drive upsell when backed by real-time, mobile-first experiences.
- Observability and incident-response maturity are critical as retail moves to 24×7 digital operations.
- Multilingual UX and regional payment options (WeChat Pay) are decisive for Southeast-Asian tourist segments.

<!-- ============================================================
  certifications.md  ·  Maintainer: Bernd Prager
  PURPOSE
    • Master list of *all* certifications (earned, expired, in-progress, planned).
    • Serves as single data-source for résumé builders, LinkedIn updaters,
      or other AI-driven export pipelines.

  IMPORTANT — AI / AUTOMATION GUIDANCE
    1. When generating any *external* document (CV, client profile, website):
         • Export **only** the certifications under **## Professional Certifications**.
         • “In-progress / planned” items may be exported **only** if clearly
           labelled “(In Progress, ETA YYYY-MM)” — they must never be shown as
           completed.
    2. Items in **## ↗︎ Certifications In Progress / Planned** are internal and
       MUST NOT be shown as earned credentials unless rule 1 is followed.
    3. Preserve ISO-8601 dates; downstream scripts parse them.
    4. Retain all Markdown links so PDFs / badge URLs stay resolvable.
    5. Do not alter the heading hierarchy; parsers rely on the ## / ### levels.

  HOUSE RULES
    • Newest first within each section.
    • Keep verbose notes inside <details> blocks.
    • Store local artifacts in ./certs/  (git-tracked or git-lfs as appropriate).

  STATUS LEGEND
| Status               | Meaning                                      |
| -------------------- | -------------------------------------------- |
| ✅ Active            | Current credential that will require renewal |
| 🔄 Renew by YYYY-MM  | Within renewal window                        |
| ♾️ Lifetime           | Valid indefinitely (no renewal required)     |
| 🚫 Expired           | No longer valid                              |
| ⏳ In Progress n %   | Actively studying                            |
| 🆕 Planning          | Future goal                                  |

============================================================ -->

# Professional Certifications

| Year | Certification | Issuer | Status |
|------|--------------|--------|--------|
| 2013-12 | **TOGAF® 9** | The Open Group | ♾️  Lifetime |
| 2016-04 | **AWS Certified Solutions Architect – Associate** | AWS | 🚫 Expired (2022-04) |
| 2019-10 | **Machine Learning** | Stanford University on Coursera | ♾️  Lifetime |
| 2016-04 | **SCRUM Master Accredited Certification** | International Scrum Institute™ (Scrum Institute) | ♾️  Lifetime |
| 2020-03 | **Introduction to Data Science in Python** | University of Michigan on Coursera | ♾️  Lifetime |
| 2025-04 | **Data Analytics Job Simulation** | Deloitte Australia on Forage |  ♾️  Lifetime |

---

## AWS Certified Solutions Architect – Associate

* **Issuer:** Amazon Web Services
* **Issued / Expires:** 2016-04-29 → 2022-04-29
* **Verification:** <https://www.credly.com/badges/7be8bb01-8735-440c-a563-72d73cc0bdcc#:~:text=April%2029%2C%202022-,Verified,-AWS%20Certified%20Solutions>
* **Badge:** ![AWS Badge](https://www.credly.com/badges/7be8bb01-8735-440c-a563-72d73cc0bdcc/public_url)

<details>
<summary>✎ Notes (click to expand)</summary>

* Earners of this certification have a comprehensive understanding of AWS services and technologies. They demonstrated the ability to build secure and robust solutions using architectural design principles based on customer requirements. Badge owners are able to strategically design well-architected distributed systems that are scalable, resilient, efficient, and fault-tolerant.
* Applied know-how in FinOps PoC (↓ 38 % GPU runtime).

</details>

---

## TOGAF® 9 Certified

* **Issuer:** The Open Group
* **Issued:** 2013-12-02
* **Verification:** <https://www.credly.com/badges/8003501f-8d55-4d78-9d83-01c095e681fe/linked_in_profile#:~:text=December%2002%2C%202013-,Verified,-Celebrate>

<details>
<summary>✎ Notes (click to expand)</summary>

* Badge earners are able, in addition to the knowledge and comprehension of TOGAF 9 Foundation, to analyze and apply this knowledge. This includes the terminology, structure, and concepts of the TOGAF 9 Standard. It includes understanding the core principles of Enterprise Architecture, the TOGAF ADM Phases, the TOGAF Content Metamodel, TOGAF ADM tools and techniques, as well as approaches for adapting the TOGAF ADM.

</details>

---

## Machine Learning

* **Issuer:** Coursera
* **Issued:** 2019-10-09
* **Verification:** <https://www.coursera.org/account/accomplishments/verify/KJWHXMBTVZ7H>

<details>
<summary>✎ Notes (click to expand)</summary>

* Badge earners have mastered the core **supervised, unsupervised, and neural-network** techniques covered in Stanford’s Machine Learning Specialization (Andrew Ng).  
* Demonstrated ability to implement end-to-end ML pipelines in **Python** using NumPy, scikit-learn, and TensorFlow—including data prep, model training, hyper-parameter tuning, and evaluation.  
* Can design and deploy regression/classification models, decision-tree ensembles, clustering & anomaly-detection systems, recommender engines, and an introductory reinforcement-learning agent.  
* Emphasizes practical best-practice workflows (train/validation/test splits, bias-variance trade-off, vectorization for efficiency) aligned with industry standards.  
* Certificate is the modern successor to Ng’s original 2012 course—validated by both **Stanford Online** and **DeepLearning.AI**.

</details>


---

<!-- ---------------------------------------------------------------- -->
# ↗︎ Certifications In Progress / Planned
<!-- External generators: skip this section unless explicitly asked to
     include “in-progress” items, which must be labelled accordingly. -->

| Target Date | Certification | Study Status | Notes |
|-------------|---------------|--------------|-------|
| 2025-09-30 | **AWS Certified Machine Learning – Specialty** | ⏳ 35 % | Focusing on OpsSuite |
| 2026-02-15 | **Azure Solutions Architect Expert** | 🆕 Planning | Post-GCP renewal |

## AWS Certified Machine Learning – Specialty *(In Progress)*

* **Study Start:** 2025-06-01
* **Target Exam Date:** 2025-09-30
* **Prep Resources:**
  * *AWS Official Study Guide* (ISBN 978-1119803750)
  * Stephane Maarek Udemy course
* **Progress Checklist:**
  * [x] Data Engineering domain
  * [ ] Exploratory Data Analysis domain
  * [ ] ML Deployment & Ops domain

## Azure Solutions Architect Expert *(Planned)*

* **Exam Pair:** AZ-305 & AZ-104
* **Kick-off:** After GCP renewal
* **Dependency:** Azure sandbox subscription

<!-- Add new certifications above this line -->

# Deloitte Online Internship
- **Company**: Deloitte Australia
- **Duration**: [Start Date] - [End Date]
- **Location**: Los Angeles, United States (Remote)

## Deloitte Australia Data Analytics Job Simulation on Forage - April 2025

- Completed a Deloitte job simulation involving data analysis and forensic technology 
- Created a data dashboard using Tableau 
- Used Excel to classify data and draw business conclusions

## Why was I interested in this role?”

I recently participated in Deloitte's job simulation on the Forage platform, and
it was incredibly useful to understand what it might be like to be part of the
team at Deloitte.
I was able to analyse data and create a dashboard. I practised using Tableau and
Excel and built my data analysis skills in a real-world context.
Doing this program confirmed that I really enjoy working on technology problems
for clients and I'm excited to apply these skills on a team at a company like
Deloitte.
---
job_id: unix_administrator_deutsche_seereederei_rostock_1987_1990
role: UNIX Administrator
company: Deutsche Seereederei Rostock
start_date: "1987-10"
end_date: "1990-03"
location: Rostock, Germany
---
# UNIX Administrator
**Deutsche Seereederei Rostock**
Rostock, Germany | October 1987 – March 1990

## Summary
Managed SINIX-based UNIX servers, developed and maintained data-entry applications, and ensured continuous cross-border telecom connectivity for maritime container shipping operations.

## Responsibilities
- Administered SINIX servers: monitored health, managed backups, and handled user accounts.
- Developed and maintained C applications for container shipment data entry and reporting.
- Designed and executed data-entry workflows, ensuring accuracy of global shipping records.
- Customized SINIX shell scripts and supported Siemens Nixdorf Xenix modifications.
- Configured, tested, and troubleshooted leased-line telecom links between Rostock and Antwerp.
- Authored technical documentation covering system configurations, network procedures, and application usage.
- Collaborated with logistics, operations, and network teams to align system performance with business needs.

## Achievements
- **Maintained one of the rare operational data communication links across East Germany**, enabling uninterrupted shipment data exchange.
  - Achieved over 99% uptime on the leased line over 2.5 years.
  - Standardized cross-border communication procedures adopted by partner ports.

## Significant Project
### Container Shipment Data Entry & Reporting System
- **Scope**: End-to-end solution for capturing, validating, and reporting global container shipment data.
- **Key Deliverables**:
  - C-based input application with built-in validation and error handling.
  - SINIX shell utilities for batch import/export and archival.
  - Automated report generation for daily, weekly, and monthly shipping summaries.

## Skills
- UNIX system administration
- Embedded C application development
- Shell scripting (SINIX/Xenix)
- Leased-line network configuration & troubleshooting
- Technical documentation
- Cross-disciplinary collaboration

## Technologies
- **OS**: SINIX (Siemens Nixdorf Xenix derivative)
- **Languages**: C, shell scripting
- **Network**: Telecom leased lines
- **Tools**: Custom data-entry apps, shell utilities

## Lessons Learned
- Rigorous documentation is vital for maintaining legacy systems and cross-border networks.
- Automating data workflows significantly reduces entry errors and manual workload.
- Proactive system monitoring and collaboration with stakeholders ensure high availability.



| epam-logo-3x.png | EPAM Systems, Inc.41 University Drive, Suite 202Newtown, PA 18940267 759 9000 Phone267 759 8989 Faxwww.epam.com |
| --- | --- |

**Bernd Prager – Director, Delivery Management**

Summary

Seasoned technology leader with extensive experience spanning over three decades in architecture, AI, and delivery management roles across diverse industries

AI Architect and Director of Delivery Management at EPAM Systems, with focus on innovative AI projects, including semantic document search and knowledge graph-based systems, and also leading enterprise architecture for clients

Experience in compliance and security projects at Amazon, video streaming ecosystems for Vizio Smart TVs, global ECommerce, and global enterprise architecture solutions at Standard & Poor's

Former founder and CEO of a German software company, showcasing entrepreneurial and technical expertise

Ability to deliver strategic, scalable solutions, combining a deep technical background with strong leadership and problem-solving skills to create impactful results

Technical interview experience

Full-stack development expertise especially in Java, Python, PostgreSQL, JavaScript (Vue-JS)

Data architecture and data analysis experience in Python, Pandas, Matplotlib

Strong AWS cloud experience (Redshift, EC2, Container Services, Lambda, DynamoDB etc.)

Key business domains: Finance, Retail, Media, Insurance

Certificates

EPAM: AI Literacy Program, 2024

Amazon Web Services: AWS Certified Solutions Architect – Associate, 2016

Scrum Institute: Scrum Master Accredited Certification, 2016

Open Group (TOGAF): The Open Group Certified: TOGAF® 9 Certified, 2013

Skills

**AI**

**AI Strategy and Leadership:** AI Strategy, AI Strategy and Leadership

**AI Architectures:** AI Architectures

**Academic Disciplines**

**Humanities:** English Speaking, English

**Applied Sciences:** Design patterns, Machine Learning, Software Development, Big Data, Domain-Driven Design (DDD), Microservice Architecture Pattern, Command Query Responsibility Segregation (CQRS), Event Sourcing, Service Oriented Architecture (SOA)

**Business Functions**

**Corporate Communications:** Interviewing

**Workforce Planning & Management:** Staffing

**Consulting Practice**

**Business Consulting:** IT Strategy [CIO Advisory]

**Experience & Innovation Consulting:** Digital Technology Consulting

**Technology Consulting:** Technical consulting, Cloud Transformation, Technology Consulting, Technology Strategy

**Strategy Consulting:** Strategy Consulting, AI & ML Strategy, Data & AI Consulting

**Engineering Practices**

**Digital Engagement:** Content Management

**Data & Analytics:** Machine Learning Engineering, Data Science Consulting, Data Solution Architecture, NoSQL DB Development, Machine Learning Model Development, Data Analytics Consulting, System analysis and System Architecture design, Cloud Data Services

**Advanced Technology:** Software Design, Security Architecture, Logging, IT Architecture, Enterprise Architecture, Application Architecture, .NET, Scrum Master, Python Web NoSQL, Analysis, Systems Architecture, Enterprise Integration Patterns, ArchiMate, Cloud Fundamentals, Generative AI Fundamentals, Strategy, Advanced Software Engineering, Java NoSQL, Prompt Engineering, Solution Architecture, Continuous Integration

**Cloud:** Cloud, Cloud Computing basics, Service Delivery Management

**Management:** Delivery Management

**Quality Engineering:** AI/ML Testing

**Industries**

**Software & Hi-Tech:** Software & Services

**Life Sciences:** Life Sciences

**Insurance:** Health Insurance, Insurance Policy Administration, Insurance Underwriting, Insurance Annuities

**Telecom, Media & Entertainment:** Business Information & Publishing

**Financial Services:** Financial Services, Capital Markets

**Leadership & Soft Skills**

**Leadership:** Developing Others, Driving Change and Innovation, Leadership

**Communication:** Communication, Visual Representation of Information

**Consultancy:** Client Relationship Management

**Business Acumen:** Business Acumen, Market orientation

**Diversity, Equity, and Inclusion:** Diversity, Equity, and Inclusion

**Teamwork and Collaboration:** Team Management, Teamwork and Collaboration

**Growth Mindset:** Adaptability

**Ownership:** Ownership, Problem-solving

**Managerial**

**General Management:** Kanban, Scrum

**Gen AI in Management:** Domain Cases for GenAI in Software Solutions

**Technologies**

**Standard:** GraphQL, Business Process Model and Notation (BPMN), IDEF0, IDEF1X

**IDE:** Jupyter Notebook

**Library:** Matplotlib, Python Data Visualization Libs, Seaborn, Python Uncategorized Libraries

**Computer Language:** SQL, Bash, Java 7, JavaScript, Java, C++, Python, UNIX shell scripting, TypeScript

**Operating System:** Linux

**Generative AI Technologies:** ChatGPT

**Framework:** Spring Boot, Pandas, AngularJS, Angular, Apache Camel, VueJS, ReactJS, TOGAF

**Data:** NoSQL Databases, Neo4J, Prometheus, Apache Kafka, Python Data Science Ecosystem

**Platforms:** Cloud Compute Service, Quarkus, AI Platform Notebooks, AWS.Database, AI, Data Science, and Statistics, AWS Fargate

**Solution:** Grafana, GNU Autoconf, Terraform, GNU Automake, Jenkins, Jira

**Tools:** Python Test Automation Frameworks

**Industry Specific Technologies:** Bureau of Credit Histories

**Platform:** AI DIAL, Amazon Web Services, Docker

Work experience

**Jul-2024 - Till now (Feb-2025)** - EPAM Systems, <https://www.epam.com/>

**Project Roles:** AI Architect and Developer, Developer, Solution Architect, Cloud Application Architect

**Client:** EPAM Systems, Inc

**Client Description:** Title Insurance (First American)

**EPAM Project Description:** AI proof of concept with semantic document search over client PDF files, ChatGPT-like chat system with Knowledge Graph-RAG and EPAM DIAL-backend

**Responsibilities:**

I have designed and implemented a POC for multi-agent AI system with following functionality

ingest PDF files and extract a knowledge graph in Neo4j as GraphRAG (Retrieval Augmented Generation)

build a cypher query creating agent to query additional information from the graph dynamically based on the user input

build a ReAct ("reason-and-act') agent as chat backend using a property index and tools to find a sufficient answer

build a document search to find the semantically nearest document

build a Python FastAPI web service to provide information to the frontend

build a JavaScript (VueJS) chat frontend

AWS implementation for client

**Oct-2020 - Till now (Feb-2025)** - EPAM Systems, <https://www.epam.com/>

**Project Roles:** Director, Delivery Management

**Client:** EPAM Systems, Inc

**Client Description:** Software & Hi-Tech

**EPAM Project Description:** - Dual role Delivery Manager for successful project execution and delivery as well as Enterprise and Solution Architect

- AI evangelist and advocate

**Responsibilities:**

Successful management of multiple client projects

Interview, support hiring of candidates based on client demands

Build successful teams

Communicate with client teams to assess demands and project health

Asses and design client's enterprise and solution architecture

Hands-on development and prototyping when required

**Jun-2022 - Jun-2024** - EPAM Systems, <https://www.epam.com/>

**Project Roles:** Delivery Manager

**Client:** Amazon, Inc

**Client Description:** Compliance department for Amazon's retail business

**EPAM Project Description:** We are the guardians of the Amazon galaxy. Our diverse team innovates on behalf of their customers to build a trusted marketplace through best-in-class registration, verification, and compliance products. With hundreds of millions of customers and sellers around the world depending on our products & services, our systems form the tip of the spear against bad actors. These actors might abuse Amazon products and undermine customer faith, so our success comes from identifying & removing them while delivering best-in-class compliance programs and customer experiences. We’re creating the most trusted store on earth, enabling Amazon to innovate at scale, and supporting selling partners to launch & grow their business faster than anywhere else in the world. With over $475B in annual gross merchandise sold, 3.8B available products, and 2M sellers, our platform requires uniquely massive thinking

**Responsibilities:**

Primary contact and advocate for EPAM team members staffed on the Amazon Compliance project

Responsibilities span across providing ongoing support to developers, coordinating with Amazon leadership, monitoring project health, and facilitating collaboration

Interview potential candidates based on Amazon requirements

Build project tracking and reporting tools (Python, Pandas) using Amazon's proprietary tracking tools

Build relationships with key drivers on client side

Tools and Technologies

Python Data Visualization Libs, Python, Pandas, SQLite

Team

25

**Feb-2021 - May-2022** - EPAM Systems, <https://www.epam.com/>

**Project Roles:** Solution Architect

**Client:** Vizio

**Client Description:** Software & Hi-Tech

**EPAM Project Description:** VIZIO, Inc., the #1 American-based TV brand and #1 SoundBarBrand in America, announced its all-new CR-Series TV™ which incorporates a 13MP camera on VIZIO’s award-winning 4K HDR SmartTV. The front-facing camera comes with built-in apps that will enable users to participate in video conference calls, talk to family and friends, watch TV together and enjoy a variety of interactive apps that take advantage of the camera

We will help Vizio develop video streaming platform and application ecosystem for new TVs

**Responsibilities:**

Evaluated technology for in-device (TV) video conferencing

Worked with technology vendor (WebRTC) to establish proof of concept

Developed and implemented performance monitoring system for TVs and data pipeline into AWS Redshift with AWS Lambda and monitoring via Grafana

Improved voice command pipeline on TV with AWS Speech Recognition

Worked with EPAM video specialist to research, identify and solve video quality issues

Tools and Technologies

Python, Grafana, AWS Lambda, Amazon Redshift

Team

12

**Aug-2019 - Sep-2020** - Krungthai-AXA Life Insurance PCL.

**Project Roles:** Enterprise and DataArchitect

**Client:** Krungthai-AXA Life Insurance PCL

**Project Description:** • Enterprise System & Data Architecture

• AWS data lake and data migration

• Enterprise Application rationalization

• Mobile doctor remote visit application (accelerated by pandemic

**Responsibilities:**

Enterprise Data Architecture to identify and catalog all critical data sources across the enterprise

design and implement AWS data lake

migrate all relevant data to AWS

establish data pipelines

Enterprise Architecture to identify and catalog all critical enterprise application and rationalize their usage

vendor selection for mobile doctor visit application

design and development for mobile applications

design and development support for Kubernetes/OpenShift authentication

**Feb-2018 - Jul-2019** - Central Group

**Project Roles:** VP - Product Director

**Client:** Central Group

**Project Description:** The One Card - customer loyalty program and mobile application development

**Responsibilities:**

Mobile enterprise royalty application design and implementation

Requirement gathering for loyalty program application

Loyalty program product strategy

Scrum Master for mobile agile development

AWS resource inventory and management

**Sep-2016 - Jan-2018** - Agoda

**Project Roles:** Development Manager

**Client:** Agoda

**Project Description:** Frontend product development for international travel and hotel booking side

**Responsibilities:**

Requirement gathering for mobile and web application development

Interviews with potential candidates

Build and manage high performance development teams

Software development management

Content management product design and strategy

Mobile data transfer optimization by development of data compression algorithms

**Feb-2008 - Jan-2016** - Standard & Poor's

**Project Roles:** Senior Director, Enterprise Architecture

**Client:** Standard & Poor's

**Project Description:** Head of Enterprise Architecture, Chief Technical Architect, Global Architect for coordination and management of international architecture teams

**Responsibilities:**

Strategy and management of international S&P architecture teams (New York, London, Tokyo, Mumbai, and Sidney)

Technology Selection & Portfolio Management for all S&P software products

Reference Architecture & Best Practice Development

Architecture Governance strategy and implementation

Solution Architecture Implementation & Hands-On Prototyping for critical technologies (e.g. Liferay Portal, Java/Oracle Messaging etc.)

**Feb-2006 - Jan-2008** - McGraw-Hill Education

**Project Roles:** Director, Enterprise Services Architect

**Client:** McGraw-Hill Education

**Project Description:** Design, implementation and launch of McGraw-Hill's Book "Comping" Website and data and application integration

**Responsibilities:**

Design of internet website for "comping" McGraw-Hill's products

Development management for website

Integration with internal application and data sources

Design of architecture façade to integrated internal professor authorization

Launch of website

**Dec-2003 - Jan-2006** - RSG Systems, Inc.

**Project Roles:** Senior Technical Architect

**Client:** McGraw-Hill. RSG Systems, Inc

**Project Description:** McGraw-Hill consulting and delivery management (design, implementation and launch of McGraw-Hill's Book "Comping" Website and data and application integration)

**Responsibilities:**

Delivery management for McGraw-Hill's book "comping" project

Design of internet website for "comping" McGraw-Hill's products

Development management for website

Integration with internal application and data sources

Design of architecture façade to integrated internal professor authorization

Launch of website

**Dec-2002 - Dec-2003** - The Digital Group

**Project Roles:** Senior Technology Consultant

**Client:** Wolters Kluwer. The Digital Group

**Project Description:** Consulting engagement for Wolters Kluwer on Microsoft .NET Service Oriented Architecture strategy

**Responsibilities:**

Enterprise Architecture for identifying critical application and components

Identifying and selecting candidates for migration to SOA

Client consulting on benefits and implications of SOA architecture

Development of enterprise strategy for SOA implementation

Support of development efforts in SOA implementation

**Feb-2002 - Nov-2002** - Viant Corporation

**Project Roles:** Lead Technologist

**Client:** Merck pharma

**Project Description:** Content management system for pharmaceutic products and internationalization for Merck

**Responsibilities:**

Requirement gathering and documentation

Application design in Perl language

Software development

International pharma content management implementation (product information customization for different countries)

Internationalization of content delivery

Merck

**Mar-1999 - Jan-2002** - Bertelsmann

**Project Roles:** Senior Technical Architect

**Client:** Bertelsmann

**Project Description:** Architecture, design and implementation of global media E-Commerce store, data center consolidation strategy

**Responsibilities:**

Solution Architecture for international bookstore

Extension to music CD's

Extension to book clubs with specific topics and requirements

International Web Store development (different languages, shipping and handling requirements, character sets etc.)

Vendor coordination for Oracle's product development (Application Server)

On of the first international bookstores (competing with Amazon, first in Japan before Amazon)

**Apr-1989 - Mar-1999** - GECKO mbH

**Project Roles:** CEO

**Client:** GECKO mbH

**Project Description:** Founder and CEO of software, hardware resell and consulting company in East-Germany

**Responsibilities:**

Founder and CEO

Business development

Client acquisition

Vendor management

Funding (German Ministry of Research) for research projects

Development of Academic Cooperation for research and resources

Education

**Name of the Education Establishment:** TECHNICAL UNIVERSITY OF DRESDEN

**Faculty/College:** Electrical and Computer Engineering

**Department:** Information Systems Engineering

**Degree (diploma):** Master


---
job_id: director_delivery_architect_epam_2020_2025
role: Director Delivery Management / Enterprise Architect
company: EPAM Systems, Inc.
start_date: "2020-10"
end_date: "2025-04"
location: Los Angeles, CA, USA
---

# Director Delivery Management / Enterprise Architect
**EPAM Systems, Inc.**
Los Angeles, CA | October 2020 – April 2025

## Summary
Led enterprise-architecture and large-scale delivery for marquee clients while becoming a key evangelist for EPAM’s *AI-first* strategy.
Co-authored the internal **FinOps POV for LLM cost-efficiency**, co-presented the public *“LLM Architecture Patterns”* session at **EPAM Learning Week 2023** (13 Dec 2023) :contentReference[oaicite:0]{index=0}, and single-handedly built a knowledge-graph-RAG POC on DIAL™ :contentReference[oaicite:1]{index=1}.
Guided presales teams, mentored 30 + solution architects, and embedded AI/RUN™ methodology :contentReference[oaicite:2]{index=2} across global accounts.

## Responsibilities
- **GenAI Evangelism & Education** Ran weekly “AI Guild” clinics; designed hands-on labs for vector search, RAG and prompt-engineering; mentored > 30 architects.
- **FinOps for LLMs** Owned the internal POV quantifying GPU-/token-level cost drivers and optimisation levers; worked with Finance to embed KPIs in EPAM AI/RUN™ playbooks :contentReference[oaicite:3]{index=3}.
- **Thought Leadership** Co-speaker, *LLM Architecture Patterns* (Learning Week 2023); guest on EPAM AI-Native podcast series.
- **Presales Advisory** Shaped AI bids in insurance, retail, telco; created demo stacks (Azure OpenAI + knowledge-graph) that converted 4 new logos in 2024.
- **Engagement Leadership** Oversaw multi-cloud solution architecture (AWS, Azure) for media, healthcare and fintech clients; managed geo-distributed squads (50 + engineers).

## Achievements
- **FinOps POV adopted company-wide**, projecting 35 % LLM OPEX savings and informing DIAL™ pricing calculators.
- **Insurance Semantic-Search & KG-RAG POC** delivered in 6 weeks: 15 M pages PDF corpus → < 2 s semantic answers; demo shortlisted for client’s 2025 production roadmap.
- **Architect Mentoring** 90 % of mentees certified on Azure AI or AWS GenAI within 9 months; internal CSAT 4.7/5.
- **Public Advocacy** Learning Week talk drew 1 500 live viewers, rated 4.8/5; slides reused in EPAM’s external GenAI roadshows.

## Significant Projects
### Insurance Semantic Search & KG-RAG POC
Python / LlamaIndex backend with ReACT agents; Neo4j vector + ontology store; Vue 3 SPA front-end.
- Indexed 25 GB PDF contracts into hybrid vector + BM25 store.
- Multi-agent chain routed questions to **DIAL™** (Azure OpenAI GPT-4o) for extraction, summarisation and graph enrichment.
- Deployed on Azure Container Apps; end-to-end latency p95 = 1.9 s.

### EPAM FinOps POV for LLMs
White-paper + Excel model capturing GPU utilisation, context-window, quantisation and batch-size trade-offs.
- Benchmarks: GPT-4o vs. Mixtral 8x7b on A10 vs. A100 vs. CPU-only.
- Recommendations integrated into AI/RUN™ cost-tracker.

### LLM Architecture Patterns (Learning Week 2023)
1-hour public session comparing monolithic vs. modular LLM stacks, guard-rail strategies and RAG blueprints; co-presented with Jonathan Rioux & John Soares.
- Demoed LangChain Router + DIAL™ orchestration across public and private models.

## AI & Machine-Learning Contributions
- **Scope** Evangelised enterprise GenAI adoption; created reusable RAG templates, FinOps calculators and multi-agent orchestration patterns.
- **Techniques / Models** GPT-4o, DIAL-LLM, Mixtral, ReACT agents, LangGraph finite-state chains, vector-search hybrid ranking.
- **Datasets & Tooling** PDF → text pipeline (PyMuPDF), Neo4j vector indexes, Azure OpenAI embeddings, Grafana + Prometheus cost dashboards.
- **Impact Metrics** Projected 35 % token-cost reduction; POC answered 92 % of insurance FAQs with top-3 accuracy.
- **Leadership** Chaired EPAM **AI Guild**; mentored architects, authored internal playbooks; spoke at Learning Week and client webinars.

## Skills
- Generative-AI architecture (RAG, FinOps, multi-agent)
- Multi-cloud (AWS, Azure) governance
- Delivery management & performance analytics
- Knowledge-graph modelling (Neo4j, RDF)
- Technical evangelism & public speaking
- Vue 3 / Python full-stack prototyping

## Technologies
- **LLMs / GenAI** Azure OpenAI GPT-4o, DIAL™, Mixtral, OpenAI embeddings
- **Frameworks** LlamaIndex, LangChain, LangGraph, ReACT
- **Data / Graph** Neo4j, Azure Cognitive Search, Pandas, Grafana
- **Cloud** Azure Container Apps, Azure Functions, AWS Lambda, S3
- **DevOps** Terraform, GitHub Actions, Prometheus, Grafana Loki
- **Languages** Python, JavaScript / TypeScript (Vue 3), SQL, Bash

## Lessons Learned
- *FinOps must be baked into every GenAI design*—monitor GPU minutes, context tokens and retrieval accuracy together.
- Knowledge-graph–augmented RAG unlocks enterprise-grade fidelity, especially for large PDF corpora.
- Consistent evangelism and hands-on mentoring are catalysts for organisation-wide AI adoption.

---
job_id: founder_ceo_gecko_mbh_1990_2000
role: Founder & CEO
company: GECKO Gesellschaft für Computer- und Kommunikationssysteme mbH (GECKO Software)
start_date: "1989-04"
end_date: "2000-12"
location: Rostock, Germany
---

# Founder & CEO
**GECKO Gesellschaft für Computer- und Kommunikationssysteme mbH**
Rostock, Germany | April 1990 – December 1999

## Summary
Founded and scaled one of the first private software-engineering firms in post-reunification Rostock, driving it from a single-person start-up to a 30-employee organisation with seven-figure annual revenue while pioneering German web-search R & D and municipal IT solutions.

## Responsibilities
- Incorporated GECKO mbH, established legal, financial, and operational structures, and secured initial seed capital.
- Defined company strategy, portfolio (custom software, IT services, early Internet/WWW solutions) and go-to-market plans.
- Recruited and led cross-functional teams (software engineering, consulting, administration) growing to 30 staff by 2000.
- Oversaw architecture and delivery of enterprise software (rental-management, campus-information, data-integration).
- Negotiated and managed university collaborations and federal research grants (e.g., BMBF-funded **GETESS** project). :contentReference[oaicite:0]{index=0}
- Directed sales & marketing, winning municipal and corporate clients in Germany, Belgium, and the UK.
- Supervised finance, budgeting, and annual audits ensuring sustainable cash-flow and profitability.

## Achievements
- **Scaled GECKO from start-up to recognised software provider with international client base and €1 M+ revenue.**
  - Achieved > 40 % CAGR during first five fiscal years.
  - Built long-term partnerships with Rostock city administration and German universities.
- **Co-initiated GETESS (“German Text Exploitation and Search System”)**—a three-year BMBF project with AIFB-Karlsruhe, DFKI, and Uni Rostock; delivered a semantic web-search prototype and multilingual indexing engine. :contentReference[oaicite:1]{index=1}
- Moved headquarters to Koch-Gotha-Str. 1, 18055 Rostock and expanded infrastructure (leased 2 Mbit Internet uplink—rare in early-1990s East Germany).

## Significant Projects
### Municipal Rental-Management System
End-to-end property-rental workflow for Rostock city housing department: contract lifecycle, tenant ledger, and reporting.
- Oracle DB backend, client-server GUIs, nightly batch billing.
- Enabled 30 % processing-time reduction for ≈20 000 rental units.

### GETESS – Searching the Web Exploiting German Texts
Consortium R & D project (1997–2000) to build a domain-independent, linguistically enriched search engine.
- Designed crawler pipeline, SGML text normaliser, and semantic index store.
- Deployed public prototype at **getess.gecko.de** (2000). :contentReference[oaicite:2]{index=2}

## AI & Machine-Learning Contributions
- **AI Scope** Led GECKO’s work-package for an ontology-driven semantic Web search engine (GETESS), focusing on German natural-language content and early Semantic-Web principles. :contentReference[oaicite:3]{index=3}
- **Techniques / Models** Implemented ontology-based information-extraction rules, morphological parsing, concept-vector indexing, and ontology-based clustering; evaluated early inference engine **SILRI** for semantic ranking. :contentReference[oaicite:4]{index=4}
- **Datasets & Tooling** Crawled ≈ 2 M German web pages; engineered SGML→RDF conversion pipeline; hosted shared Oracle-backed knowledge warehouse accessible over leased-line Frame Relay to DFKI/Karlsruhe.
- **Impact Metrics** Consortium tests reported ~30 % precision gain over keyword search in the tourism domain and demonstrated multilingual abstract generation—results cited in CIA-99 and SEAL-II follow-up projects. :contentReference[oaicite:5]{index=5}
- **Leadership & Collaboration** Represented the SME partner, coordinated four institutions, supervised five engineers, co-authored **“GETESS — Searching the Web Exploiting German Texts”** (CIA-99), and presented live demos at CeBIT 1999.
- **Continuous Learning** Completed NLP & ontology-engineering workshops at AIFB-Karlsruhe, became early W3C RDF adopter, and self-studied information-retrieval literature to guide prototype evaluation.

## Skills
- Start-up leadership & strategy
- Enterprise/municipal IT architecture
- Research consortium management
- Team building & mentoring
- Budgeting and P&L oversight
- International business development

## Technologies
- **Platforms** UNIX (SunOS, IBM AIX), Windows NT, early Linux
- **Languages** C/C++, Delphi, Gupta SQL Windows, Java (from 1996)
- **Databases** Oracle 7/8, Informix, MySQL
- **Web** HTML 2 / 3.2, CGI/Perl, Apache HTTP D (since 1995)
- **Networks** ISDN; leased-line Frame Relay between Rostock & Karlsruhe/DFKI for GETESS collaborations
- **Tools** CVS, Visual SourceSafe, Rational Rose, SGML parsers

## Lessons Learned
- Sustainable growth hinges on transparent governance and diversified revenue streams.
- University partnerships accelerate innovation and credibility for R & D-heavy SMEs.
- Early adoption of Internet standards creates long-term competitive advantage in enterprise software.

---
job_id: enterprise_data_architect_krungthai_axa_2019_2020
role: Enterprise & Data Architect
company: Krungthai-AXA Life Insurance PCL
start_date: "2019-08"
end_date: "2020-09"
location: Bangkok, Thailand
---
# Enterprise & Data Architect
**Krungthai-AXA Life Insurance PCL**
Bangkok, Thailand | August 2019 – September 2020

## Summary
Led regional architecture governance and cloud-data strategy for a top Thai life-insurance joint venture, delivering an AWS-based data lake, an automated underwriting platform, and COVID-accelerated telehealth solutions while ensuring IFRS 17 and FATCA compliance.

## Responsibilities
- Chaired the **Regional Architecture Council**, approving all major solution designs across Bangkok and Hong Kong operations.
- Defined application & data-rationalisation roadmap; prioritised decommission or cloud migration of 40+ legacy apps.
- Designed and oversaw build of an **AWS data lake** (Glue, S3, Redshift) to consolidate policy, claims, and actuarial data.
- Served as chief architect for **AUWrite** automatic underwriting system—integrated 10+ external data sources (criminal, medical, payments).
- Drove cloud-native reference patterns on OpenShift, Kong API gateway, and Keycloak IAM; issued reusable ADRs.
- Coordinated with AXA Europe to align Salesforce CRM and IFRS 17 reporting standards.
- Ran vendor selection for BPMN tooling and conducted organisation-wide data-maturity assessment (DAMA lens).
- Maintained business-continuity architecture throughout COVID-19; expedited rollout of TeleHealth mobile app.

## Achievements
- **Delivered AUWrite underwriting platform**, cutting manual review time by 70 % and raising straight-through-processing to 85 %.
- Built production data lake ingesting 500 GB/day; enabled first AI/ML risk-scoring PoCs.
- Launched **TeleHealth** within 90 days; supported 12 k virtual consults in first quarter of 2020.
- Ensured on-schedule compliance with **IFRS 17** and **FATCA** via canonical data models and automated lineage tracking.
- Achieved zero downtime during Thailand’s strict COVID-19 lockdown through fail-over architecture and remote-ops runbooks.

## Significant Projects
### AUWrite – Automatic Underwriting System
- Microservice stack on OpenShift; rule engine + ML risk model; real-time integrations (Kong, Redis) with external data providers.

### TeleHealth Mobile Platform
- Flutter front-end; Kubernetes back-end; secure video via WebRTC; integrated e-pharmacy ordering and payment gateway.

## Skills
- Enterprise & data architecture (TOGAF, DAMA)
- Cloud migration & data-lake design (AWS)
- Regulatory compliance (IFRS 17, FATCA, Thai PDPA)
- Architecture governance & council leadership
- Legacy rationalisation & vendor selection
- Rapid product acceleration under crisis conditions

## Technologies
- **Cloud / Data**: AWS (Glue, S3, Redshift, IAM), OpenShift
- **Integration**: Kong API Gateway, Keycloak IAM, Redis, AS/400 adapters
- **DevOps / Observability**: Dynatrace, Jenkins, GitLab CI
- **Languages / Frameworks**: Java, Python, BPMN tools
- **Security & Privacy**: Thai PDPA controls, OAuth 2.0, JWT

## Lessons Learned
- Thai **PDPA** imposes stricter consent and localisation rules than GDPR—early legal alignment is critical.
- Architecture councils accelerate decision-making when backed by clear reference models and ADRs.
- Crisis-driven products (e.g., telehealth) succeed when built on pre-established cloud & security patterns.

Contact

bernd@prager.ws

www.linkedin.com/in/bprager
(LinkedIn)
www.prager.ws (Personal)
www.zeromq.org/ (Other)

Top Skills

Ollama

PyTorch

SQLite

Languages

English

German

Certifications

SCRUM MASTER ACCREDITED
CERTIFICATION

Introduction to Data Science in
Python

TOGAF 9

Machine Learning

Publications

GETESS - Searching the Web
Exploiting German Texts

Bernd Prager

Director, Delivery Management at EPAM Systems
Los Angeles, California, United States

Summary

As a seasoned Chief Architect with over 25 years in the tech

industry, I specialize in the development, architecture, and strategic

oversight of major IT projects, including one of the largest e-

commerce systems hosting over 10 million products. An enthusiastic

AI evangelist, I drive innovation and strategic IT solutions across

global enterprises.

Experience

EPAM Systems
Director, Delivery Management
October 2020 - Present (4 years 5 months)
Los Angeles Metropolitan Area

- Spearheaded architectural design and management of IoT projects,

enhancing system integrations and operational efficiency.

- Directed compliance management initiatives, ensuring alignment with

regulatory requirements and industry standards.

- Championed AI technology, serving as an evangelist and internal consultant

to promote innovative solutions across various teams.

- Facilitated cross-departmental collaboration to implement advanced AI-driven

processes, significantly boosting project outcomes and strategic innovation.

Krungthai-AXA Life Insurance PCL.
Enterprise and Data Architect
August 2019 - September 2020 (1 year 2 months)
Bangkok Metropolitan Area, Thailand

Central Group
VP - Product Director
February 2018 - July 2019 (1 year 6 months)
Bangkok Metropolitan Area, Thailand

Agoda
Development Manager

Page 1 of 3

September 2016 - January 2018 (1 year 5 months)
Bangkok Metropolitan Area, Thailand

Standard & Poor's
10 years

Senior Director, Enterprise Architecture
February 2008 - 2016 (8 years)

・Technology Selection & Portfolio Management

・Reference Architecture & Best Practice Development

・Architecture Governance

・Solution Architecture Implementation & Hands-On Prototyping

Senior Director, Enterprise Architecture - Standard and Poor's
February 2006 - 2016 (10 years)

McGraw-Hill Education
Director, Enterprise Services Architect
February 2006 - January 2008 (2 years)

RSG Systems, Inc.
Senior Technical Architect
December 2003 - January 2006 (2 years 2 months)

The Digital Group
Senior Technology Consultant
December 2002 - December 2003 (1 year 1 month)

Viant Corporation
Lead Technologist
February 2002 - November 2002 (10 months)

Bertelsmann
Senior Technical Architect
March 1999 - January 2002 (2 years 11 months)

GECKO mbH
CEO
April 1989 - March 1999 (10 years)

Founder and CEO of German software company

Page 2 of 3

FJB-40
Staff Sergeant
1978 - 1981 (3 years)

Education

Technische Universität Dresden

MA, Information Technology · (1981 - 1986)

Ostseegymnasium Rostock

Diploma, qualifying for university admission · (1975 - 1978)

Page 3 of 3


# Document folder

This folder contains all documents in markdown format describing my experience relevant for the job agent


BERND PRAGER

504 S Sierra Bonita Ave E-mail: bernd@prager.ws Mobile: + 1 (323) 983 - 3520

Los Angeles, CA 90036

# SUMMARY OF QUALIFICATIONS

Chief technical architect / senior manager with 20+ years international IT industry experience with a focus for the last 10+ years technology management, enterprise architecture, hands-on development, security planning, consulting, and operations, Machine Learning and AI enthusiast

# PROFESSIONAL EXPERIENCE

### EPAM Systems – Los Angeles, CA October 2020 – now

## Director, Delivery Management

* Enterprise Architecture
* Cloud consultancy
* Technology advisory, design, and prototyping
* Generative AI (design, implementation, prof of concepts, agents, Graph RAG, evangelist)
* Cloud full stack (AWS, Azure, container)

### Krungthai-AXA, Life Insurance – Bangkok, Thailand August 2019 – September 2020

## Enterprise and Data Architect (Insurance)

* Manage Enterprise Architecture team.
* Architect Data Lake on-premise to cloud migration
* Architect and support implementation of Rule-Based underwriting automation
* Vendor evaluation and technology selection of Thai Tele-Health system

### Central Technology – Bangkok, Thailand February 2018 – July 2019

## VP – Product, VP – Delivery (Retail)

* Design and implemented centralized infrastructure logging, monitoring, and alert system.
* Manage cross-business-group loyalty product and software development.
* Developed and published companywide IT standards, recommendations, policies, and security incident response plan.

### Agoda – Bangkok, Thailand September 2016 – January 2018

## Software Development Manager (Travel)

* Build and manage travel frontend web development teams.
* Research and development of frontend data, analytics, and experience product.

### Standard & Poor’s – New York, NY February 2008 – September 2016

## Senior Technology Architect (Financial Services)

* Create and manage centralized Enterprise Architecture team and cloud strategy.
* Work with the CIO and product management teams to define S&P’s global technology strategy.
* Propose and budget vision projects to identify high impact, future technology initiatives.
* Build and managed architecture teams in New York, London, Tokyo, Mumbai, and Melbourne.
* Design and support implementation of complex, highly available “four nines” regulatory systems.
* Designed Reference Architecture in large volume data enterprise (Terabytes historical financial performance and model data)

### McGraw-Hill, Higher Education – New York, NY February 2006 – February 2008

## Senior Technology Architect (Media)

* Planning, product selection, architecture, and implementation of Service Oriented Architecture

### Various consulting companies August 2001 – January 2006

## Senior Technology Consultant

* Exclusive consulting engagement for McGraw-Hill Education (Media).
* Planning and implementing of enterprise critical web application, web services and service-oriented architecture.
* Planning and technology evaluation for data center consolidations in North America.
* Exclusive content managements consulting engagement for MERCK (Pharmacy).

### BERTELSMANN – New York, NY Jan 1999- Aug 2001

## Director – Senior Technical Architect (Media)

* Architected and managed implementation Bertelsmann’s leading ecommerce sites such as BOL.COM present in 19 countries in 9 languages, 12 million online visitors per month, over 10 million products in catalog with over 30,000 items ordered per day.
* Data import and interface optimization for daily pricing updates from 100+ data suppliers
* Conducted comprehensive e-commerce platform and technology evaluation of leading vendors included evaluation of feature-set, scalability, technology, costs, and performance.
* Developed support strategies for Europe customer base.

### GECKO – Rostock, Germany April 1989 – March 1999

## Founder + CEO

* Founded IT software development and ISP company with more than 30 employees.
* Acquired major customers base among German “Top 100” like Deutsche Bank, and Bertelsmann
* Acquired and managed large-scale government funded research projects (e.g., Semantic Search)

# DEVELOPMENT EXPERIENCES (EXCERPT)

* Shipping container management system (AWS Fargate, Java, Quarkus, TypeScript, VueJS)
* Agile performance analysis (Python, Pandas, Seaborn)
* Real Time Operating System Kernel: Zilog Z8 Assembly

# developer management experience (EXCERPT)

* Global Travel Website: 3 teams, 12 developers
* E-Commerce Implementation: 30 developers
* Semantic Search Research Project: 1 industry + 3 academic teams

# EDUCATION

### Technical University Dresden – Dresden Germany

* M.S. – Information Techniques

# IT SKILLS

* Programming languages (Java, C++, C, C#, JavaScript, TypeScript, Python, Golang etc.)
* Frameworks (Pandas, PyTorch, Matplotlib)
* Certifications
  + TOGAF 9 (Level 1 + 2)
  + Scrum Master
  + AWS Solution Architect – Associate
  + Machine Learning (Andrew Ng, Stanford University)

# Links

* LinkedIn: <https://www.linkedin.com/in/bprager/>
* GitHub: <https://github.com/bprager>

---
job_id: engineering_intern_practica_1985
role: Engineering Intern (Praktica)
company: Schiffselektronik Rostock
start_date: "1985-08"
end_date: "1985-12"
location: Rostock, Germany
---
# Engineering Intern (Praktica)
**Schiffselektronik Rostock**
Rostock, Germany | August 1985 – December 1985

## Summary
Embedded‑systems internship focused on end‑to‑end hardware and firmware development for an academic graduation project.

## Responsibilities
- Gathered and analyzed real‑time system requirements for the graduation project.
- Designed and prototyped hardware modules around the Zilog Z8 single‑chip microcontroller.
- Wrote, debugged, and maintained low‑level firmware in Zilog assembly to drive peripherals and manage timing.
- Performed unit and integration testing to verify real‑time behavior under varying load conditions.
- Created technical documentation including design specifications, test reports, and user manuals.
- Collaborated with academic supervisors and cross‑discipline stakeholders to align on project goals and deliverables.

## Achievements
- Successfully designed and delivered a **real‑time operating system kernel** for the Zilog Z8, including:
  - Preemptive task scheduling meeting sub‑millisecond deadlines
  - Assembly routines for context switching and interrupt handling
  - Basic inter‑process communication primitives
- Produced comprehensive design and test documentation to support future maintenance and extension.

## Significant Project
### Real‑Time OS Kernel for Zilog Z8
- **Scope**: Full architecture and implementation of an RTOS kernel as part of an engineering graduation requirement.
- **Key Deliverables**:
  - Preemptive task scheduler meeting sub‑millisecond response targets
  - Interrupt dispatch and context‑switching routines in Zilog assembly
  - IPC primitives for task synchronization

## Skills
- Requirements analysis for real‑time systems
- Embedded hardware prototyping
- Low‑level firmware development in assembly
- Unit and integration testing
- Technical specification and test‑report writing
- Collaboration with academic and engineering teams

## Technologies
- **Microcontroller**: Zilog Z8
- **Language & Toolchain**: Zilog assembly; cross‑assembler
- **Test Equipment**: Oscilloscope; logic analyzer

## Lessons Learned
- Critical importance of rigorous requirements gathering and documentation in real‑time projects.
- Hands‑on experience balancing hardware and firmware integration under strict timing constraints.
- Value of detailed test planning and reporting to ensure predictable system behavior.
---
job_id: embedded_systems_developer_schiffselektronik_rostock_1986_1987
role: Embedded Systems Developer
company: Schiffselektronik Rostock
start_date: "1986-08"
end_date: "1987-09"
location: Rostock, Germany
---
# Embedded Systems Developer
**Schiffselektronik Rostock**
Rostock, Germany | August 1986 – September 1987

## Summary
Led hardware and firmware development, testing, and deployment of marine embedded systems for naval mine detection under extreme environmental conditions.

## Responsibilities
- Designed and developed embedded hardware modules using Zilog Z80 and Z8 microcontrollers.
- Implemented, tested, and debugged low‑level firmware in assembly to manage peripherals and signal processing.
- Executed real‑time signal processing algorithms to detect naval mines.
- Conducted marine field testing of detection systems under humidity, vibration, and electromagnetic interference.
- Collaborated with operations and engineering teams to gather requirements and define performance criteria.
- Authored technical documentation including design specifications, test plans, and deployment procedures.

## Achievements
- **Successfully deployed multiple generations of naval embedded systems**, standardizing components for improved interoperability.
  - Rolled out successive hardware and firmware iterations aligned with user feedback.
  - Established component standards adopted across naval projects.

## Significant Project
### Naval Mine Detection System
- **Scope**: End-to-end RTOS-based embedded solution for mine detection on naval vessels.
- **Key Deliverables**:
  - Robust hardware architecture resilient to moisture, vibration, and magnetic interference.
  - Real‑time signal processing routines for accurate mine detection.
  - Comprehensive field test reports and deployment guidelines.

## Skills
- Embedded hardware design
- PCB design
- Low‑level firmware development
- Real‑time signal processing
- Field testing and validation
- Technical documentation
- Cross‑disciplinary collaboration

## Technologies
- **Microcontrollers**: Zilog Z80, Zilog Z8
- **Languages**: Zilog assembly
- **Operating Systems**: IBM DOS
- **Digital Design**: TTL logic
- **Toolchain**: Cross-assemblers
- **Test Equipment**: Oscilloscope, logic analyzer

## Lessons Learned
- Importance of designing for harsh marine environments.
- Balancing hardware limitations with real‑time processing requirements.
- Value of standardized components and thorough documentation.
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

