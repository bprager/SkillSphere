# Complementary Skills Template Usage Guide

## Overview

The `complementary_skills_template.md` file provides a standardized format for documenting skills and projects developed outside of formal professional experience. This template captures hobby projects, self-directed learning, and complementary skills that enhance your professional profile and demonstrate continuous learning.

## When to Use This Template

### Ideal Use Cases
- **Technical Hobbies:** PCB design, 3D printing, CAD modeling, electronics
- **Creative Skills:** Video editing, graphic design, music production, writing
- **Programming Projects:** Personal apps, open-source contributions, automation scripts
- **Research & Learning:** Self-directed studies, experiments, proof-of-concepts
- **Making & Building:** Woodworking, mechanical projects, repair work

### Not Suitable For
- **Formal Education:** Use certification templates for courses and degrees
- **Professional Work:** Use job experience templates for paid work
- **Volunteer Work:** Use extracurricular templates for community involvement

## Directory Structure

```
ingestion_docs/skills/
├── hardware/
│   ├── pcb-design-kicad.md
│   ├── 3d-printing-bambulab.md
│   └── cad-design-freecad.md
├── software/
│   ├── home-automation-python.md
│   ├── data-analysis-r.md
│   └── mobile-app-flutter.md
├── creative/
│   ├── video-editing-davinci.md
│   ├── graphic-design-gimp.md
│   └── technical-writing.md
└── research/
    ├── machine-learning-experiments.md
    ├── blockchain-exploration.md
    └── iot-prototypes.md
```

## YAML Front Matter Guide

### Required Fields

```yaml
title: "PCB Design with KiCAD"
type: "hardware_skill"
category: "electronics"
entity_id: "skill_pcb_design_kicad"
status: "active"
start_date: "2023-01-15"
proficiency_level: "intermediate"
primary_tools: ["KiCAD", "Multimeter", "Oscilloscope"]
technologies: ["PCB Design", "Circuit Analysis", "Component Selection"]
competencies: ["circuit_design", "troubleshooting", "technical_documentation"]
time_investment: "5-8 hours/week"
projects_completed: 12
last_updated: "2025-07-16"
```

### Field Guidelines

#### Type Values
- **`hardware_skill`** - Physical design, electronics, mechanical work
- **`software_skill`** - Programming, development, technical tools
- **`creative_skill`** - Design, multimedia, content creation
- **`research_skill`** - Learning, experimentation, analysis

#### Category Examples
- **Electronics:** `electronics`, `circuit_design`, `embedded_systems`
- **Mechanical:** `mechanical_design`, `manufacturing`, `prototyping`
- **Software:** `programming`, `data_analysis`, `automation`, `web_development`
- **Creative:** `multimedia`, `design`, `content_creation`, `technical_writing`

#### Status Values
- **`active`** - Currently practicing and developing
- **`learning`** - Actively learning, early stage
- **`completed`** - Finished learning/project phase
- **`on_hold`** - Temporarily paused

#### Proficiency Levels
- **`beginner`** - Basic understanding, simple projects
- **`intermediate`** - Solid foundation, complex projects
- **`advanced`** - Deep expertise, teaching others
- **`expert`** - Recognized expertise, innovation

## Content Structure Guide

### 1. Skill Overview
- **Purpose:** Explain what the skill is and why you pursued it
- **Context:** How it fits into your broader interests
- **Motivation:** What drove you to learn this skill

### 2. Learning Journey
- **Starting Point:** How you first encountered this skill
- **Resources:** Books, courses, mentors, communities
- **Progression:** How you've developed over time
- **Challenges:** Obstacles overcome and lessons learned

### 3. Tools & Technologies
- **Primary Tools:** Main software/hardware you use
- **Proficiency:** Your skill level with each tool
- **Supporting Tech:** Additional technologies that complement the skill

### 4. Projects & Applications
- **Concrete Examples:** Specific projects you've completed
- **Technical Details:** Challenges solved and approaches used
- **Outcomes:** Results, deliverables, lessons learned
- **Skills Applied:** Specific technical skills demonstrated

### 5. Competencies Developed
- **Technical Skills:** Hard skills gained through practice
- **Transferable Skills:** Soft skills that apply professionally
- **Problem-Solving:** How this skill enhanced your thinking

### 6. Professional Relevance
- **Direct Applications:** How this could apply to work
- **Skill Synergies:** Connections to professional skills
- **Career Enhancement:** How this differentiates you

## Examples for Your Specific Skills

### PCB Design with KiCAD
```yaml
title: "PCB Design with KiCAD"
type: "hardware_skill"
category: "electronics"
entity_id: "skill_pcb_design_kicad"
status: "active"
proficiency_level: "intermediate"
primary_tools: ["KiCAD", "Multimeter", "Hot Air Station"]
technologies: ["PCB Design", "Circuit Analysis", "SMD Soldering"]
competencies: ["circuit_design", "troubleshooting", "technical_documentation"]
```

### 3D Printing with BambuLab P1S
```yaml
title: "3D Printing with BambuLab P1S"
type: "hardware_skill"
category: "manufacturing"
entity_id: "skill_3d_printing_bambulab"
status: "active"
proficiency_level: "advanced"
primary_tools: ["BambuLab P1S", "Bambu Studio", "Calipers"]
technologies: ["Additive Manufacturing", "CAD Integration", "Material Science"]
competencies: ["rapid_prototyping", "design_optimization", "quality_control"]
```

### Video Creation with DaVinci Resolve
```yaml
title: "Video Creation with DaVinci Resolve"
type: "creative_skill"
category: "multimedia"
entity_id: "skill_video_davinci_resolve"
status: "active"
proficiency_level: "intermediate"
primary_tools: ["DaVinci Resolve", "Audio Interface", "Lighting Kit"]
technologies: ["Video Editing", "Color Grading", "Audio Production"]
competencies: ["storytelling", "technical_communication", "project_management"]
```

## Integration with Hypergraph System

### Processing Benefits
- **Individual Files:** Each skill processed independently for accuracy
- **YAML Metadata:** Structured data for relationship mapping
- **Skill Connections:** Graph can identify synergies between skills
- **Professional Relevance:** Clear mapping to career applications

### Search Optimization
- **Tool-Based Filtering:** Find skills by specific tools used
- **Competency Matching:** Match skills to job requirements
- **Proficiency Tracking:** Show skill development over time
- **Project Portfolio:** Demonstrate practical application

## Best Practices

### Documentation
- **Be Specific:** Use concrete examples and measurable outcomes
- **Show Progress:** Document your learning journey and growth
- **Technical Details:** Include enough detail to demonstrate expertise
- **Professional Connection:** Always connect to potential career applications

### Maintenance
- **Regular Updates:** Keep proficiency levels and project counts current
- **New Projects:** Add new projects as you complete them
- **Learning Goals:** Update future development plans regularly
- **Resource Updates:** Keep learning resources current and relevant

### Consistency
- **Naming Conventions:** Use consistent entity IDs and categories
- **Proficiency Assessment:** Be honest and consistent about skill levels
- **Time Investment:** Track actual time spent, not aspirational goals
- **Project Counting:** Count substantial projects, not trivial exercises

## Template Workflow

1. **Copy Template:** `cp templates/complementary_skills_template.md ingestion_docs/skills/[category]/[skill-name].md`
2. **Fill YAML Front Matter:** Complete all required fields
3. **Document Learning Journey:** Describe how you acquired the skill
4. **List Projects:** Include specific examples with outcomes
5. **Connect to Professional Context:** Show career relevance
6. **Remove Template Notes:** Clean up before finalizing
7. **Test Processing:** Verify with hypergraph ingestion

This template system ensures that your complementary skills are captured with the same rigor as professional experience, enabling the hypergraph to identify valuable connections and enhance your professional profile.
