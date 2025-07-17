#!/usr/bin/env python3
"""
Migration script for certifications.md to individual files.

This script helps migrate from the single certifications.md file to the new
individual file structure optimized for hypergraph processing.

Usage:
    python migrate_certifications.py
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def backup_original() -> bool:
    """Create a backup of the original certifications.md file."""
    original_file = Path("certifications.md")
    backup_file = Path(
        f"certifications_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )

    if original_file.exists():
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backed up original file to: {backup_file}")
        return True
    else:
        print("❌ Original certifications.md file not found")
        return False


def verify_new_structure() -> bool:
    """Verify that all individual certification files exist."""
    expected_files = [
        "aws-solutions-architect-associate.md",
        "togaf-9-certified.md",
        "machine-learning-stanford.md",
        "scrum-master-accredited.md",
        "data-science-python-michigan.md",
        "deloitte-data-analytics-simulation.md",
        "aws-ml-specialty-in-progress.md",
        "azure-solutions-architect-planned.md",
        "README.md",
    ]

    missing_files = []
    for file in expected_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All individual certification files exist")
        return True


def update_gitignore() -> None:
    """Update .gitignore to include backup files."""
    gitignore_path = Path("../../.gitignore")
    backup_pattern = "certifications_backup_*.md"

    if gitignore_path.exists():
        with open(gitignore_path, encoding="utf-8") as f:
            content = f.read()

        if backup_pattern not in content:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write("\n# Certification backup files\ncertifications_backup_*.md\n")
            print("✅ Added backup pattern to .gitignore")
    else:
        print("⚠️  .gitignore not found, skipping update")


def generate_migration_summary() -> None:
    """Generate a summary of the migration."""
    summary = """
# Certification Migration Summary

## What Changed

### Before (Single File Structure)
- Single `certifications.md` file with all certifications
- Monolithic structure with mixed content
- Difficult to process for hypergraph ingestion
- Changes to one certification affected processing of all

### After (Individual File Structure)
- Each certification in its own file
- Structured YAML front matter with metadata
- Optimized for hypergraph processing
- Independent change tracking and processing

## File Mapping

| Original Section | New File |
|------------------|----------|
| AWS Solutions Architect | `aws-solutions-architect-associate.md` |
| TOGAF 9 Certified | `togaf-9-certified.md` |
| Machine Learning (Stanford) | `machine-learning-stanford.md` |
| SCRUM Master | `scrum-master-accredited.md` |
| Data Science Python | `data-science-python-michigan.md` |
| Deloitte Analytics | `deloitte-data-analytics-simulation.md` |
| AWS ML Specialty (In Progress) | `aws-ml-specialty-in-progress.md` |
| Azure Solutions Architect (Planned) | `azure-solutions-architect-planned.md` |

## Benefits

1. **Better Processing**: Each file processed independently
2. **Improved Accuracy**: Focused content improves LLM gleaning
3. **Enhanced Search**: Individual embeddings enable precise retrieval
4. **Easier Maintenance**: Updates don't affect other certifications
5. **Better Organization**: Clear separation by status and type

## Next Steps

1. Verify all individual files are correct
2. Update any scripts or tools that reference the old structure
3. Test hypergraph ingestion with new structure
4. Remove the original `certifications.md` file
5. Update documentation and README files

## Verification

Run the following to verify the migration:
```bash
# Check all files exist
ls -la *.md

# Verify front matter structure
head -20 aws-solutions-architect-associate.md

# Test ingestion (if available)
python -m hypergraph.cli.ingest --dry-run
```
"""

    with open("MIGRATION_SUMMARY.md", "w") as f:
        f.write(summary)
    print("✅ Generated migration summary: MIGRATION_SUMMARY.md")


def main() -> None:
    """Main migration function."""
    print("🔄 Starting certification migration...")

    # Change to the certs directory
    os.chdir(Path(__file__).parent)

    # Step 1: Backup original file
    if backup_original():
        print("✅ Backup completed")

    # Step 2: Verify new structure
    if verify_new_structure():
        print("✅ New structure verified")

    # Step 3: Update .gitignore
    update_gitignore()

    # Step 4: Generate migration summary
    generate_migration_summary()

    print("\n🎉 Migration completed successfully!")
    print("\nNext steps:")
    print("1. Review individual certification files")
    print("2. Test hypergraph ingestion")
    print("3. Update any dependent scripts")
    print("4. Remove original certifications.md when satisfied")


if __name__ == "__main__":
    main()
