PYTHON ?= python
PIP ?= pip
POETRY ?= poetry

# Default environment file
ENV_FILE ?= .env.prod

.PHONY: setup test lint format docker-build docker-up launch-check seed-products package-exe verify hash-registry

setup:
	poetry install
	pre-commit install

test:
	poetry run pytest tests/e2e/test_full_flow.py tests/e2e/test_marketing_ready_flow.py tests/integration/test_voice_flow.py

launch-check:
	poetry run python tests/e2e/test_launch_readiness.py

verify:
	poetry run python infra/scripts/full_cycle_test.py

hash-registry:
	poetry run python infra/scripts/hash_registry.py

seed-products:
	poetry run python -m orchestrator.src.core.catalog.ingest

package-exe:
	bash infra/scripts/package_exe.sh

lint:
	poetry run ruff check .
	poetry run mypy .

format:
	poetry run black .
	poetry run ruff check --fix .

docker-build:
	cd infra/docker && docker compose -f docker-compose.prod.yml build

docker-up:
	cd infra/docker && docker compose -f docker-compose.prod.yml up -d

docker-down:
	cd infra/docker && docker compose -f docker-compose.prod.yml down -v

clean:
	rm -rf dist build *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
