#!/usr/bin/env python3
import yaml

def validate_resume(yaml_text):
    try:
        data = yaml.safe_load(yaml_text)
        required_fields = ["name", "title", "email", "phone", "location", "skills", "experience"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        print("✅ YAML resume is valid!")
    except yaml.YAMLError as e:
        print(f"❌ YAML Parsing Error: {e}")
    except ValueError as e:
        print(f"❌ Validation Error: {e}")

# Load your Markdown file and extract YAML front matter
with open("resume.md", "r") as file:
    content = file.read()
    yaml_part = content.split("---")[1]  # Extract YAML front matter
    validate_resume(yaml_part)

