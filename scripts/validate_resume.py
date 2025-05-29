#!/usr/bin/env python3
import re
import sys

import yaml

# Define the expected schema
EXPECTED_SCHEMA = {
    "name": str,
    "title": str,
    "email": str,
    "phone": str,
    "location": str,
    "linkedin": str,
    "github": str,
    "summary": str,
    "skills": list,
    "experience": list,
    "projects": list,
    "education": list,
    "certifications": list
}

REQUIRED_FIELDS = ["name", "title", "email", "phone", "location", "skills", "experience", "education"]

def extract_yaml_front_matter(markdown_text):
    """Extracts the YAML front matter from a Markdown file."""
    match = re.match(r"^---\n(.*?)\n---\n", markdown_text, re.DOTALL)
    if match:
        return match.group(1)
    return None

def validate_resume(yaml_text):
    """Validates the resume's YAML content against the expected schema."""
    try:
        data = yaml.safe_load(yaml_text)
        if not isinstance(data, dict):
            raise ValueError("YAML content must be a dictionary.")

        # Check required fields
        missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Check field types
        for field, expected_type in EXPECTED_SCHEMA.items():
            if field in data and not isinstance(data[field], expected_type):
                raise ValueError(f"Invalid type for '{field}': Expected {expected_type.__name__}, got {type(data[field]).__name__}")

        print("✅ YAML resume is valid!")
        return data

    except yaml.YAMLError as e:
        print(f"❌ YAML Parsing Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)

def main():
    """Main function to validate a resume markdown file."""
    if len(sys.argv) != 2:
        print("Usage: python validate_resume.py resume.md")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r") as file:
            content = file.read()
            yaml_part = extract_yaml_front_matter(content)

            if not yaml_part:
                raise ValueError("YAML front matter not found. Ensure it starts with `---` and ends with `---`.")

            validate_resume(yaml_part)

    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

