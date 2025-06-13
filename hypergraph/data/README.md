# Data Directory

This directory contains all data-related files for the Hypergraph project. The directory is structured to maintain a clear separation between different types of data and configurations.

## Directory Structure

```
data/
├── config/     # Configuration files for data processing and storage
├── raw/        # Raw, unprocessed data files
├── processed/  # Processed and transformed data files
└── schema/     # Schema definitions and data models
```

## Directory Purposes

### `config/`
- Contains configuration files for data processing pipelines
- Database connection settings
- Feature extraction parameters
- Model configuration files

### `raw/`
- Original, unmodified data files
- Input data for processing pipelines
- Backup of original data sources
- **Note**: This directory is git-ignored by default

### `processed/`
- Cleaned and transformed data
- Feature-engineered datasets
- Preprocessed data ready for model training
- **Note**: This directory is git-ignored by default

### `schema/`
- Graph schema definitions
- Data model specifications
- Entity relationship diagrams
- Data validation rules

## Data File Guidelines

1. **File Naming**
   - Use lowercase with underscores
   - Include date in YYYY-MM-DD format if applicable
   - Include version number if multiple versions exist
   - Example: `skill_graph_2024-03-20_v1.yaml`

2. **File Formats**
   - Configuration files: `.yaml`, `.json`
   - Schema definitions: `.yaml`, `.json`
   - Raw data: `.csv`, `.json`, `.txt`
   - Processed data: `.csv`, `.json`, `.parquet`

3. **Version Control**
   - Only commit files in `config/` and `schema/`
   - Do not commit files in `raw/` or `processed/`
   - Use `.gitkeep` files to maintain directory structure

## Data Processing Workflow

1. Place raw data files in `raw/`
2. Process data using scripts in the project
3. Save processed data to `processed/`
4. Update schemas in `schema/` if data structure changes
5. Update configurations in `config/` if processing parameters change

## Best Practices

1. **Data Privacy**
   - Never commit sensitive or personal data
   - Use data anonymization when necessary
   - Follow data protection regulations

2. **Data Quality**
   - Document data sources and processing steps
   - Include data validation checks
   - Maintain data lineage

3. **Storage**
   - Use appropriate file formats for data size and type
   - Compress large files when possible
   - Consider using version control for large files (e.g., Git LFS)

4. **Documentation**
   - Document all data processing steps
   - Include data dictionaries
   - Maintain changelog for schema changes 