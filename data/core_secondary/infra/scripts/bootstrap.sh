#!/bin/bash
# infra/scripts/bootstrap.sh

set -e

echo "Bootstrapping Orchestrator Environment..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from example"
fi

# Ensure Python 3.11 is available
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 is required but not found."
    exit 1
fi

# Install dependencies
poetry install

# Run tests to verify setup
poetry run pytest tests/e2e/

echo "Bootstrap complete. Run 'make docker-up' to start."
