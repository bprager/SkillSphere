# Dockerfile
FROM python:3.11-slim

# Allow installation of binary deps if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only metadata first for cached installs
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and project deps (no dev)
RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-dev

# Copy the rest of your application code
COPY src /app/src
COPY README.md .env.example /app/

# Set Python path so package is importable
ENV PYTHONPATH=/app/src

# Expose HTTP port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "skill_sphere_mcp.app:app", "--host", "0.0.0.0", "--port", "8000"]

