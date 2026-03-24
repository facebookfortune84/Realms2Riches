# Git Workflow & Deployment Strategy

## Overview
This document outlines the Git branching strategy, commit conventions, and deployment process for the Realms2Riches project. It aims to ensure a streamlined, reliable, and auditable path from development to production, aligning with CI/CD practices for Vercel deployment.

## Branching Strategy

We employ a streamlined Gitflow-inspired strategy, prioritizing efficient integration and deployment:

-   **`main` (or `master`)**: Represents the ultimate production-ready, stable release. This branch is protected and **never directly pushed to**. It serves as a historical marker for official releases.
-   **`stasis`**: This is the **production branch**. All code deployed to Vercel Production originates from this branch. It must always reflect a stable, tested, and verified state. Merges to `stasis` are typically performed from `dev` after successful validation and approval.
-   **`dev`**: The primary development branch. All new features, bug fixes, and experimental work are developed on separate `feature/` branches and merged into `dev`. `dev` should be kept in a relatively stable state, representing the next upcoming release candidate.
-   **`feature/` branches**: Short-lived branches created from `dev` for specific tasks (e.g., `feature/stripe-webhook-enhancement`). These branches are intended for isolated development and are merged back into `dev` via Pull Requests (PRs).

## Commit Conventions

We adhere to the **Conventional Commits** specification for all commit messages. This standardizes commit structure, making them clear, concise, and machine-readable, which aids in automated changelog generation and semantic versioning.

**Format:** `type(scope): subject`

*   **type:** Must be one of the following:
    *   `feat`: New feature implementation.
    *   `fix`: Bug fix.
    *   `chore`: Build process, auxiliary tools, or dependency updates.
    *   `docs`: Documentation changes.
    *   `style`: Code formatting, punctuation, etc. (no code logic change).
    *   `refactor`: Code restructuring without changing functionality.
    *   `perf`: Performance improvements.
    *   `test`: Adding or correcting tests.
    *   `build`: Changes affecting the build system or external dependencies.
    *   `ci`: Changes to CI configuration files and scripts.
*   **scope (optional):** The part of the codebase affected (e.g., `api`, `worker`, `frontend`, `genesis`, `docs`).
*   **subject:** Concise description of the change in the imperative mood (e.g., "add user login", "fix calculation error").

**Examples:**
-   `feat(api): implement affiliate tracking endpoint`
-   `fix(worker): correct error handling for LLM calls`
-   `chore(deps): update FastAPI to latest stable version`

## Tagging & Versioning

-   **Semantic Versioning:** Releases are tagged using semantic versioning (e.g., `v1.0.0`, `v1.1.0`, `v2.0.0`).
-   **Tagging Process:** Tags are created exclusively on the `stasis` branch to mark production releases. These tags should be pushed to the remote repository (`git push origin --tags`).

## Deployment Strategy (Vercel Integration)

-   **Production Deployment:** The `stasis` branch is the **source of truth for production**. CI/CD pipelines (e.g., GitHub Actions, GitLab CI) should be configured to automatically deploy commits to Vercel Production when changes are merged into `stasis`.
-   **Staging Deployment:** The `dev` branch is intended for pre-production validation. It can be configured to deploy to a Vercel staging environment for testing and review before merging into `stasis`.
-   **Branch Prioritization:** The `stasis` branch is explicitly designated for production. The CI/CD system must intelligently determine when to deploy to `stasis` (e.g., upon successful merge from `dev` to `stasis`, or via manual trigger/tagging).

## Workflow Summary

1.  **Develop:** Create a `feature/` branch from `dev`.
2.  **Commit:** Make atomic commits adhering to Conventional Commits.
3.  **Test Locally:** Run unit, integration, and E2E tests locally.
4.  **Pull Request:** Open a PR from `feature/` branch targeting `dev`.
5.  **Review & Merge:** Conduct thorough code review. Merge into `dev` upon approval.
6.  **Validate:** Run comprehensive E2E tests, security audits, and performance checks on `dev` (potentially triggering a staging deployment).
7.  **Release Candidate:** Merge `dev` into `stasis`. Tag the release (e.g., `v1.2.0`).
8.  **Production Deploy:** CI/CD pipeline automatically deploys the `stasis` branch to Vercel Production.

## Branch Management

-   **`dev` to `stasis` Merge:** This transition signifies a release candidate. Changes merged into `stasis` must be thoroughly tested and verified.
-   **`stasis` Branch for Vercel Production:** Vercel deployment pipeline must be configured to monitor and deploy from the `stasis` branch exclusively for production. Staging deployments should point to the `dev` branch.

## Lineage & Tags

-   **Lineage Tracking:** The `lineage.py` script (run via `make lineage` or similar) should be executed after significant architectural changes or before tagging releases to lock down code state.
-   **Tagging:** Use `git tag -a vX.Y.Z -m "Version X.Y.Z"` for releases. Ensure tags are pushed: `git push origin --tags`.

---
*Doc Version: 1.1 | Last Updated: March 10, 2026*
*Authored by: Realms2Riches AI Core*