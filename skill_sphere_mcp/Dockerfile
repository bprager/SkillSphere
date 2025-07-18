# Dockerfile

FROM python:3.10-slim

# Install uv (copy from official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv


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
COPY pyproject.toml uv.lock* /app/

# Install dependencies and create .venv
RUN uv sync --locked


# Copy the rest of your application code
COPY src /app/src


# Set the venv on the PATH
ENV PATH="/app/.venv/bin:$PATH"


# Expose HTTP port
EXPOSE 8000


# Run Uvicorn using the venv
CMD ["uvicorn", "skill_sphere_mcp.app:app", "--host", "0.0.0.0", "--port", "8000"]

