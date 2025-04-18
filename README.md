# my-job-agent
Framework to promote my professional career growth

## resume creator

Use follwing prompt:```
You are an AI resume generator. Generate a structured resume using the following YAML format.

---
name: "<Full Name>"
title: "<Professional Title>"
email: "<Email Address>"
phone: "<Phone Number>"
location: "<City, Country>"
linkedin: "<LinkedIn Profile>"
github: "<GitHub Profile>"
summary: "<Brief summary of professional experience>"
skills:
  - category: "<Skill Category>"
    items: "<Comma-separated list of skills>"
experience:
  - company: "<Company Name>"
    role: "<Job Title>"
    dates: "<Start - End Date>"
    bullets:
      - "<Achievement 1>"
      - "<Achievement 2>"
projects:
  - name: "<Project Name>"
    description: "<Brief description>"
education:
  - degree: "<Degree Name>"
    institution: "<Institution Name>"
    year: "<Year of Completion>"
certifications:
  - "<Certification Name>"
---

### **Additional Instructions**
- Ensure Markdown syntax is correct.
- Use bullet points for experiences and achievements.
- Only include valid YAML types (strings, lists, numbers).
- Make sure all data fields are filled correctly.
```

## pdf generator

Use `pandoc` to create an ATS (Applicant Tracking System) pdf resume

```
pandoc resume.md -o resume.pdf --template=resume-template.tex --pdf-engine=xelatex
```
