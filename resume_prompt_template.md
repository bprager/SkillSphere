---
###############################################################################
#                R É S U M É   Y A M L   S T R U C T U R E                    #
#  Populate EVERY {{…}} placeholder; keep the indentation exactly as shown.   #
#  Do NOT wrap anything in triple-back-ticks; this YAML block MUST be first.  #
###############################################################################

# ---------- CONTACT ----------
name: "{{NAME}}"                  # e.g. "Bernd Prager"
title: "{{TARGET_TITLE}}"         # e.g. "Senior Director Analyst – AI & GenAI"
email: "{{EMAIL}}"
phone: "{{PHONE}}"
location: "{{CITY, STATE}}"
linkedin: "{{LINKEDIN_URL}}"
github: "{{GITHUB_URL}}"
website: "{{PORTFOLIO_URL}}"

# ---------- CONTENT ----------
summary: |
  {{PROFESSIONAL_SUMMARY}}        # 2-4 lines. Markdown bold/italics allowed.

skills:
  core:                           # 6-10 short phrases, one per line
    - "{{CORE_SKILL_1}}"
    - "{{CORE_SKILL_2}}"
    - "{{CORE_SKILL_3}}"
  technical:                      # group long tech stacks here
    - "{{TECH_SKILL_ROW_1}}"
    - "{{TECH_SKILL_ROW_2}}"
    - "{{TECH_SKILL_ROW_3}}"

experience:                       # most recent roles first
  - role: "{{ROLE_1_TITLE}}"
    company: "{{COMPANY_1}}"
    location: "{{LOCATION_1}}"
    dates: "{{DATES_1}}"          # "2020 – 2025"
    bullets:
      - "{{ROLE_1_BULLET_1}}"
      - "{{ROLE_1_BULLET_2}}"
      - "{{ROLE_1_BULLET_3}}"
      - "{{ROLE_1_BULLET_4}}"
      - "{{ROLE_1_BULLET_5}}"
  - role: "{{ROLE_2_TITLE}}"
    company: "{{COMPANY_2}}"
    location: "{{LOCATION_2}}"
    dates: "{{DATES_2}}"
    bullets:
      - "{{ROLE_2_BULLET_1}}"
      - "{{ROLE_2_BULLET_2}}"
      - "{{ROLE_2_BULLET_3}}"

earlycareer:                      # 1-line achievements for pre-2010 roles
  - role: "{{EARLY_ROLE_1}}"
    company: "{{EARLY_COMPANY_1}}"
    note: "{{EARLY_IMPACT_1}}"
  - role: "{{EARLY_ROLE_2}}"
    company: "{{EARLY_COMPANY_2}}"
    note: "{{EARLY_IMPACT_2}}"

projects:                         # optional highlight projects
  - name: "{{PROJECT_1_NAME}}"
    detail: "{{PROJECT_1_DETAIL}}"
  - name: "{{PROJECT_2_NAME}}"
    detail: "{{PROJECT_2_DETAIL}}"

education:
  - degree: "{{DEGREE_1}}"
    institution: "{{INSTITUTION_1}}"

certifications:
  - name: "{{CERT_1_NAME}}"
    year: "{{CERT_1_YEAR}}"
  - name: "{{CERT_2_NAME}}"
    year: "{{CERT_2_YEAR}}"

publications:
  - "{{PUBLICATION_1}}"
  - "{{PUBLICATION_2}}"
---

<!--
===============================================================================
INSTRUCTIONS FOR ResumeGPT  ·  DO NOT DELETE THIS COMMENT BLOCK
===============================================================================
You are ResumeGPT, an expert résumé writer for senior AI/ML roles.

Task
====
Convert the provided CANDIDATE DATA and TARGET JOB description into this
YAML-only résumé format, filling **every** {{…}} placeholder.

Hard Rules
----------
1.  **No body content** after the YAML.  The ats_resume.latex template
    pulls everything from these variables.
2.  All lists MUST be valid YAML sequences (`- item`), not block scalars.
3.  Bullet points = Action + Metric + Outcome (≤ 2 lines each).
4.  Use age-neutral phrasing (“15+ years”).
5.  Mirror critical keywords from the target job.
6.  Keep ≤ 5 bullets per recent role; earlier roles stay in `earlycareer`.
7.  Output ONLY this completed Markdown file—no extra text, no fences.

When finished, return the filled YAML as the sole response.
===============================================================================
END OF INSTRUCTIONS
-->

