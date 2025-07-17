FROM python:3.10.13-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .
COPY README.md .

# Install dependencies
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Run as non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Command to run the ingestion
CMD ["python", "-m", "hypergraph.cli.ingest"]
