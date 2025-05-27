"""Skills Hypergraph Ontology.

This module defines the core ontology for the Skills Hypergraph, which represents
professional skills, experiences, and relationships in a semantic graph structure.
"""

# pylint: disable=no-member,import-error,too-few-public-methods
from owlready2 import Thing, get_ontology

# Create a new ontology
onto = get_ontology("http://www.prager.ws/ontology/skills-hypergraph.owl")

with onto:
    # === Classes ===
    class Person(Thing):
        """Represents a person in the skills graph."""

    class Job(Thing):
        """Represents a job or position held by a person."""

    class Project(Thing):
        """Represents a project that a person has worked on."""

    class Skill(Thing):
        """Represents a skill that can be demonstrated through experience."""

    class Technology(Thing):
        """Represents a technology that can be used in jobs or projects."""

    class Certification(Thing):
        """Represents a professional certification."""

    class Organization(Thing):
        """Represents an organization where work was performed."""

    class Location(Thing):
        """Represents a geographical location."""

    class TimeRange(Thing):
        """Represents a time period for an experience."""

    class ExperienceType(Thing):
        """Represents the type of experience (e.g., full-time, contract)."""

    # === Object Properties ===
    class HasExperience(Person >> Job):
        """Links a person to their job experiences."""

    class WorkedFor(Job >> Organization):
        """Links a job to the organization where it was performed."""

    class HeldRole(Person >> Project):
        """Links a person to projects they worked on."""

    class UsedSkill(Job >> Skill):
        """Links a job to the skills used in that role."""

    class UsedTechnology(Job >> Technology):
        """Links a job to the technologies used in that role."""

    class LocatedIn(Job >> Location):
        """Links a job to its geographical location."""

    class During(Job >> TimeRange):
        """Links a job to its time period."""

    class AchievedCertification(Person >> Certification):
        """Links a person to their certifications."""

    class IssuedBy(Certification >> Organization):
        """Links a certification to its issuing organization."""

    class HasExperienceType(Job >> ExperienceType):
        """Links a job to its type of experience."""

    class RelatedTo(Job >> Skill):
        """General purpose link between jobs and skills."""


# Save to an .owl file (optional)
onto.save(file="skills_hypergraph.owl", format="rdfxml")

# Print ontology contents (for verification)
print("Ontology IRI:", onto.base_iri)
print("Classes:", list(onto.classes()))
print("Object Properties:", list(onto.object_properties()))
