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

## SCRUM Master Accredited Certification**

* **Issuer:** International Scrum Institute™ (Scrum Institute)
* **Issued:** 2016-04-07
* **Certificate:** <https://www.scrum-institute.org/certifications/Scrum-Institute.Org-SMAC62422c588f-06709196959156.pdf>

<details>
<summary>✎ Notes (click to expand)</summary>

* Badge earners show deep command of the **Scrum framework**—roles, events, and artifacts—able to facilitate *Sprint Planning, Daily Scrum, Sprint Review,* and *Retrospectives* in line with the official Scrum Guide. [oai_citation:0‡International Scrum Institute](https://www.scrum-institute.org/Scrum_Master_Accredited_Certification_Program.php)
* Proven **servant-leadership** skills: coaching cross-functional teams, clearing impediments, and driving continuous improvement to maximise product value and team velocity. [oai_citation:1‡International Scrum Institute](https://www.scrum-institute.org/Scrum_Master_Accredited_Certification_Program.php)
* Passed a **50-question, 60-minute online exam** with a ≥ 60 % score; the credential is **lifetime & worldwide-recognised** with no renewal fees. [oai_citation:2‡International Scrum Institute](https://www.scrum-institute.org/Scrum_Master_Accredited_Certification_Program.php)
* Certification provides a portable **“proof of competence”** in Agile delivery, boosting career prospects for roles such as Architect, Product Manager, Project Manager, and QA/Test. [oai_citation:3‡International Scrum Institute](https://www.scrum-institute.org/Scrum_Master_Accredited_Certification_Program.php)
* Holders gain access to Scrum Institute’s premium self-study resources (e-book, video masterclasses, sample tests) designed to reinforce practical, real-world application of Scrum. [oai_citation:4‡International Scrum Institute](https://www.scrum-institute.org/Scrum_Master_Accredited_Certification_Program.php)

</details>


---

## Introduction to Data Science in Python

* **Issuer:** Coursera / University of Michigan
* **Issued:** 2020-03-12
* **Verification:** <https://www.coursera.org/account/accomplishments/verify/K3ZSV46VV76H>

<details>
<summary>✎ Notes (click to expand)</summary>

* Completed the **34-hour** University of Michigan course that forms the first step of the “Applied Data Science with Python” pathway, proving a solid command of Python-centric data science tooling.  [oai_citation:0‡Coursera](https://www.coursera.org/account/accomplishments/verify/K3ZSV46VV76H)
* Mastered the core data stack—**NumPy, pandas, SciPy**—to ingest, clean, transform, and query tabular data with efficient, vectorised code.  [oai_citation:1‡Coursera](https://www.coursera.org/account/accomplishments/verify/K3ZSV46VV76H)
* Demonstrated proficiency with **lambda functions, CSV I/O, DataFrame grouping/merging, reshaping, and pivot operations** for end-to-end exploratory analysis.  [oai_citation:2‡Coursera](https://www.coursera.org/account/accomplishments/verify/K3ZSV46VV76H)
* Gained foundational statistics skills, including understanding **distributions, sampling methods, and t-tests** to validate hypotheses.  [oai_citation:3‡Coursera](https://www.coursera.org/account/accomplishments/verify/K3ZSV46VV76H)
* Skill set formally recognised by Coursera covers **data cleansing, data management, general & statistical programming, critical thinking, and analytical storytelling**, equipping holders to contribute immediately to real-world data projects.  [oai_citation:4‡Coursera](https://www.coursera.org/account/accomplishments/verify/K3ZSV46VV76H)

</details>

---

## Deloitte Data Analytics Job Simulation

* **Issuer:** Deloitte (Australia) · Forage Virtual Experience
* **Issued:** 2025-04-30
* **Verification:** <https://forage-uploads-prod.s3.amazonaws.com/completion-certificates/9PBTqmSxAf6zZTseP/io9DzWKe3PTsiS6GG_9PBTqmSxAf6zZTseP_HCQJzaYT6bGXeHaG6_1746050490036_completion_certificate.pdf>

<details>
<summary>✎ Notes (click to expand)</summary>

* Completed Deloitte’s **self-paced 1–2 hour data-analytics virtual internship**, taken by 30 k+ learners and designed to mirror real consulting engagements.  [oai_citation:0‡Forage](https://www.theforage.com/simulations/deloitte-au/data-analytics-s5zy)
* Produced two client deliverables for heavy-machinery firm *Daikibo Industrials*:
  * **Tableau dashboard** that mined factory telemetry to surface downtime patterns, KPIs and actionable recommendations.  [oai_citation:1‡Forage](https://www.theforage.com/simulations/deloitte-au/data-analytics-s5zy)
  * **Excel fairness model** that classified pay-equality scores (Fair / Unfair / Highly Discriminative) via IF-based logic, enabling HR insight.  [oai_citation:2‡GitHub](https://github.com/mohitsharma614/Deloitte-Virtual-Internship-)
* Practised core skills in **data modelling, cleaning, exploratory analysis, spreadsheets and visual storytelling**—aligned with Deloitte’s forensic-analytics methodology.  [oai_citation:3‡Forage](https://www.theforage.com/simulations/deloitte-au/data-analytics-s5zy)
* Program context highlights Deloitte’s **Forensic Technology** services, giving exposure to investigative analytics and risk insights.  [oai_citation:4‡forage-uploads-prod.s3.amazonaws.com](https://forage-uploads-prod.s3.amazonaws.com/completion-certificates/9PBTqmSxAf6zZTseP/io9DzWKe3PTsiS6GG_9PBTqmSxAf6zZTseP_HCQJzaYT6bGXeHaG6_1746050490036_completion_certificate.pdf)
* Certificate signed by Deloitte CHRO **Tina McCreery**; includes unique enrolment (rCPpFQNWGAoW6q9pS) and user (HCQJzaYT6bGXeHaG6) verification codes for lifetime validation.  [oai_citation:5‡forage-uploads-prod.s3.amazonaws.com](https://forage-uploads-prod.s3.amazonaws.com/completion-certificates/9PBTqmSxAf6zZTseP/io9DzWKe3PTsiS6GG_9PBTqmSxAf6zZTseP_HCQJzaYT6bGXeHaG6_1746050490036_completion_certificate.pdf)

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

