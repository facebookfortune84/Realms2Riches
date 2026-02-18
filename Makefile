PYTHON ?= python
PIP ?= pip
POETRY ?= poetry

# Default environment file
ENV_FILE ?= .env.prod

# -------------------------------
# Environment & Dependencies
# -------------------------------
.PHONY: init
init:
    $(PYTHON) -m venv venv
    . venv/bin/activate && $(PIP) install --upgrade pip
    . venv/bin/activate && $(PIP) install -e orchestrator[dev]

# -------------------------------
# Local Development
# -------------------------------
.PHONY: dev
dev:
    cd infra/docker && docker-compose -f docker-compose.prod.yml up --build

.PHONY: dev-down
dev-down:
    cd infra/docker && docker-compose -f docker-compose.prod.yml down

# -------------------------------
# Tests & Checks
# -------------------------------
.PHONY: test
test:
    . venv/bin/activate && cd orchestrator && pytest

.PHONY: launch-check
launch-check:
    . venv/bin/activate && cd orchestrator && pytest ../tests/e2e/test_launch_readiness.py

# -------------------------------
# Build Artifacts
# -------------------------------
.PHONY: build
build:
    cd infra/docker && docker-compose -f docker-compose.prod.yml build

# -------------------------------
# Data & Seeding
# -------------------------------
.PHONY: seed-products
seed-products:
    . venv/bin/activate && $(PYTHON) orchestrator/src/tools/seed_products.py --env-file $(ENV_FILE)

# -------------------------------
# Packaging (.exe)
# -------------------------------
.PHONY: package-exe
package-exe:
    . venv/bin/activate && $(PIP) install pyinstaller
    . venv/bin/activate && pyinstaller orchestrator/src/main_cli.py --name Realms2Riches --onefile --clean
    @echo "Executable built in dist/Realms2Riches"

# -------------------------------
# CI Helper
# -------------------------------
.PHONY: ci
ci: test launch-check
    @echo "CI checks complete."