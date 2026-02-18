# Governance

## Policies

1.  **No Secrets**: Code must not contain secrets. Checked via regex scan.
2.  **Tests Required**: All PRs must have associated tests.
3.  **Docker Labels**: Images must include `swarm.project.id` and `swarm.build.sha256`.

## Enforcement

*   **Pre-commit**: Local checks.
*   **CI Pipeline**: GitHub Actions blocks merge if checks fail.
*   **Deployment**: Docker images are only pushed if validation passes.

## Lineage

Every artifact (code commit, docker image) is recorded in the `lineage` table/file with:
*   `producer_agent_id`
*   `timestamp`
*   `hash`
