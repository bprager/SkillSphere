from owlready2 import *

# Create a new ontology
onto = get_ontology("http://www.prager.ws/ontology/skills-hypergraph.owl")

with onto:
    # === Classes ===
    class Person(Thing): pass
    class Job(Thing): pass
    class Project(Thing): pass
    class Skill(Thing): pass
    class Technology(Thing): pass
    class Certification(Thing): pass
    class Organization(Thing): pass
    class Location(Thing): pass
    class TimeRange(Thing): pass
    class ExperienceType(Thing): pass

    # === Object Properties ===
    class hasExperience(Person >> Job): pass
    class workedFor(Job >> Organization): pass
    class heldRole(Person >> Project): pass
    class usedSkill(Job >> Skill): pass
    class usedTechnology(Job >> Technology): pass
    class locatedIn(Job >> Location): pass
    class during(Job >> TimeRange): pass
    class achievedCertification(Person >> Certification): pass
    class issuedBy(Certification >> Organization): pass
    class experienceType(Job >> ExperienceType): pass
    class relatedTo(Job >> Skill): pass  # General purpose link

# Save to an .owl file (optional)
onto.save(file="skills_hypergraph.owl", format="rdfxml")

# Print ontology contents (for verification)
print("Ontology IRI:", onto.base_iri)
print("Classes:", list(onto.classes()))
print("Object Properties:", list(onto.object_properties()))

