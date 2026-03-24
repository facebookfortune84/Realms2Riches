# Contributing to Realms2Riches

We welcome contributions to enhance the Realms2Riches project! Please adhere to the following guidelines to ensure a smooth and efficient contribution process.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a positive and inclusive environment.

## Getting Started

1.  **Fork the Repository:** Create a personal fork of the Realms2Riches repository.
2.  **Clone Your Fork:** Clone your fork locally:
    ```bash
    git clone https://github.com/your-username/realms2riches.git
    cd realms2riches
    ```
3.  **Set Upstream Remote:** Add the main repository as an upstream remote to fetch changes:
    ```bash
    git remote add upstream https://github.com/realms2riches/realms2riches.git
    git fetch upstream
    ```

## Branching Strategy

We follow a streamlined Gitflow-inspired strategy:

-   **`main` / `master`**: Represents the ultimate production-ready, stable release. This branch is protected and **never directly pushed to**. It serves as a historical marker for official releases.
-   **`stasis`**: This is the **production branch**. All code deployed to Vercel Production originates from this branch. It must always reflect a stable, tested, and verified state. Merges to `stasis` are typically performed from `dev` after successful validation and approval.
-   **`dev`**: The primary development branch. All new features, bug fixes, and experimental work are developed on separate `feature/` branches and merged into `dev`. `dev` should be kept in a relatively stable state, representing the next upcoming release candidate.
-   **`feature/` branches**: Short-lived branches created from `dev` for specific tasks (e.g., `feature/stripe-webhook-enhancement`, `fix/genesis-forge-bug`). These branches are intended for isolated development and are merged back into `dev` via Pull Requests (PRs).

## Development Workflow

1.  **Create Branch:** Start a new feature branch from the latest `dev`:
    ```bash
    git checkout dev
    git pull upstream dev # Ensure dev is up-to-date
    git checkout -b feature/your-branch-name
    ```
2.  **Code Changes:** Implement your feature or fix. Adhere to project conventions, style guides, and use idiomatic code.
3.  **Commit Messages:** Use **Conventional Commits** format (e.g., `feat(api): add affiliate tracking`).
4.  **Run Linters & Tests:** Ensure your code adheres to project standards and passes all tests locally.
    ```bash
    # Install dependencies (if needed)
    # poetry install

    # Run linters
    # make lint

    # Run tests
    # make test 
    ```
5.  **Pull Request (PR):** Create a Pull Request from your `feature/` branch targeting `dev`.
6.  **Code Review:** A maintainer will review your PR. Address feedback as needed.
7.  **Merge to `dev`:** Once approved, merge into `dev`.
8.  **Release Process:** Periodically, `dev` is merged into `stasis` for a release candidate. Thorough testing (including E2E, security, performance) is performed on `stasis`.
9.  **Production Deploy:** CI/CD pipeline automatically deploys the `stasis` branch to Vercel Production.

## Adding New Features / Tools

-   **Agent Tools:** If adding new tools for agents, ensure they are well-documented, adhere to the `BaseTool` interface, and are registered appropriately for agent discovery.
-   **New Monetization Streams:** Follow the pattern of existing scripts and integrate with the `MonetizationEngine` or relevant daemons.

## Security Best Practices

-   **Secrets Management:** NEVER commit secrets, API keys, or sensitive credentials directly to Git. Use `.env.prod` and secure methods for deployment.
-   **Dependency Audits:** Regularly scan dependencies for vulnerabilities.
-   **Input Validation:** Always validate external input rigorously.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---
*Contributing Guide Version: 1.1 | Last Updated: March 10, 2026*
*Authored by: Realms2Riches AI Core*