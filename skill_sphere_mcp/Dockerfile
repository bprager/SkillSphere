# Dockerfile
FROM python:3.10-slim

# Allow installation of binary deps if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only metadata first for cached installs
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and project deps (no dev)
RUN pip install --no-cache-dir .

# Copy the rest of your application code
COPY src /app/src

# Set Python path so package is importable
ENV PYTHONPATH=/app/src

# Expose HTTP port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "skill_sphere_mcp.app:app", "--host", "0.0.0.0", "--port", "8000"]

