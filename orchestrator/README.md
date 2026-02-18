# Orchestrator

The central nervous system of the Agentic Software Agency.

## Structure

- `src/core/`: Main loop, agent definitions, routing logic.
- `src/agents/`: Concrete implementations of specific agents (PM, Dev, etc.).
- `src/tools/`: Tool implementations (Git, Docker, etc.).
- `src/memory/`: Long-term memory (Vector Store) and Structured Memory (SQL).
- `src/validation/`: Pydantic schemas and guardrails.

## Running in Dev Mode

```bash
poetry install
poetry run python -m orchestrator.src.core.orchestrator
```
