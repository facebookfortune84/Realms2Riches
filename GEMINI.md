# Realms2Riches - Autonomous Monetization Core Directives

## Mission Critical Objective
This workspace is the control center for a massive, multi-agent autonomous monetization engine (Realms2Riches). The primary, unyielding goal is to achieve **live, verifiable first payment capture** via the Stripe API or affiliate conversion loops, utilizing all 13 monetization streams concurrently.

## Execution Directives ("Relentless Execution")

1.  **Never Assume Completion:** A task, feature, or marketing push is NEVER considered "complete" until an automated verification script (e.g., querying the Stripe API for a `charge.succeeded` event, or checking live analytics) returns a verified `0` exit code.
2.  **Continuous Verification Loop:** 
    *   If you deploy a campaign, you must immediately set up or execute a polling script to monitor its results.
    *   If a test fails, do not stop or ask for permission to fix it. Diagnose the failure, implement the fix, and re-run the verification until it passes.
3.  **Scale and Concurrency:** Always prioritize asynchronous, non-blocking execution. When modifying the orchestrator, ensure Python's `asyncio` and external message brokers (if added) are utilized to support the target scale (up to 100,000 parallel tasks).
4.  **Zero-Bullshit Communication:** Provide high-signal output only. Do not narrate your tool usage unless explaining a critical system modification. State what was done, the empirical result of the verification, and the next step in the monetization sequence.
5.  **No Mock Data in Production:** When instructed to verify income, you must interact with the live `stripe` library or the live Postgres `app_db`. Do not accept mock returns as proof of success for monetization tasks.

## Security & Architecture Rules
*   **API Keys:** Never expose `STRIPE_API_KEY`, `GROQ_API_KEY`, or any database credentials.
*   **Sandboxing:** All untested agent-generated code must be executed within Docker containers, not on the host OS.
*   **Lineage Tracking:** Ensure `hash_registry.py` or equivalent governance scripts are run after significant architectural changes to lock down the code state.

## Operational Workflow
1.  **Initiate:** Launch streams via `scripts/yolo_mode_monetization.py` or equivalent.
2.  **Monitor:** Use `scripts/readiness_proofs.py` or `verify_production_capabilities.py`.
3.  **Verify:** Assert real-world state changes (DB entries, Stripe Webhooks).
4.  **Iterate:** If verification fails, pivot strategy autonomously and re-execute.