# Realms2Riches Data Lifecycle

This document defines the standard data lifecycle for all agents in the Realms2Riches swarm. Agents must follow this lifecycle to ensure system reliability and consistency.

## 1. Lifecycle Stages

### Stage 1: Inputs
*   **Static Config:** /oracle (business/product/tech docs), .env.prod (secrets/env settings), data/catalog/products.json (source of truth for products).
*   **Dynamic Inputs:** Web traffic, form submissions, voice audio streams, outreach replies.
*   **System SOPs:** /sops/ and /agents/ define the "how" for any operation.

### Stage 2: Processing
*   **Orchestration:** Orchestrator reads goals, selects SOPs, and dispatches to appropriate agents.
*   **Execution:** Agents use tools to:
    *   Read/write repo files (CodebaseTool).
    *   Query/Update memory and RAG (VectorStore/SQLStore).
    *   Run tests (TestRunnerTool).
    *   Wire analytics and outreach.

### Stage 3: Outputs
*   **Artifacts:** Updated code (backend/frontend), updated catalog, new outreach templates.
*   **Deployments:** Vercel frontend updates, backend behavior changes.
*   **Communication:** Outreach emails, voice interactions, purchase links.
*   **Instrumentation:** Analytics events logged to the internal `analytics_events` table.

### Stage 4: Feedback Loops
*   **Tests:** `pytest` (unit/integration/E2E) must run after every change.
*   **Analytics:** Internal reports (in `scripts/analytics/`) validate revenue impact.
*   **Owner Review:** Final output and voice summary presented for approval.

## 2. Agent Data Standards
*   **Read/Write:** Use `CodebaseTool` and `SQLStore` standard APIs. Do not bypass existing abstractions (e.g., use `MonetizationEngine` instead of direct catalog file access where possible).
*   **Safety:** Never log secrets. Always use `ANALYTICS_ENABLED` and `OUTREACH_ENABLED` flags.
*   **Verification:** A task is incomplete if it lacks verification (test, smoke test, or analytics check).
