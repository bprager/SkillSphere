#!/bin/bash

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "Error: Virtual environment not found at $PROJECT_ROOT/.venv"
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$PYTHON_VERSION" != "3.10" ]; then
    echo "Error: Expected Python 3.10, but got $PYTHON_VERSION"
    exit 1
fi

# Run tests with coverage
echo "Running tests with coverage..."
PYTHONPATH=skill_sphere_mcp/src .venv/bin/python -m pytest skill_sphere_mcp/tests/ -v --cov=skill_sphere_mcp --cov-report=term-missing

# Deactivate virtual environment
deactivate 