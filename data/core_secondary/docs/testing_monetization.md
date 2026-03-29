# Monetization Testing Strategy for Realms2Riches

This document outlines the automated testing strategy for all monetization-critical features within the Realms2Riches platform. The goal is to ensure reliability, scalability, and correctness across various environments (development, testing, production).

## 1. Test Environment & Configuration

Our testing strategy leverages environment variables to configure the system for different test scenarios.

### `.env.test` File
This file is used for automated tests and defines environment-specific overrides:

```ini
# .env.test - Environment variables for testing
ENV_MODE=dev # Typically 'dev' for tests, not 'prod'
TEST_MODE=True # Activates test-specific behaviors in the application
ANALYTICS_ENABLED=False # Analytics are generally disabled during tests to avoid noise

# Stripe test keys (replace with your actual test keys for integration tests)
STRIPE_TEST_MODE=True # Ensures the application uses Stripe test mode or mocks
STRIPE_API_KEY=sk_test_mock_key # Placeholder: Replace with a real Stripe test secret key for integration tests
STRIPE_PUBLISHABLE_KEY=pk_test_mock_key # Placeholder: Replace with a real Stripe test publishable key for integration tests
STRIPE_WEBHOOK_SECRET=whsec_test_mock_secret # Placeholder: Replace with a real Stripe test webhook secret for integration tests

# SMTP Test config (ensures no real emails are sent during tests)
OUTREACH_ENABLED=False # Disable live outreach
DRY_RUN_MODE=True # Force dry-run mode for outreach
OUTREACH_TEST_RECIPIENT=test@example.com # All test emails will be routed here

# Database for testing (SQLite by default for isolated tests)
DATABASE_URL=sqlite:///./test_orchestrator.db
POSTGRES_HOST=localhost # Ensures no attempt to connect to a Dockerized Postgres
```

### Configuration Loading (`orchestrator/src/core/config.py`)
The `Settings` class loads environment variables with the following precedence:
`.env.test` > `.env.prod` > `.env.local` > `.env.example`.
The `TEST_MODE` flag, when `True`, triggers specific behaviors:
- Stripe API calls are expected to use test keys or mock clients.
- Outreach is forced into `DRY_RUN_MODE`.

## 2. Test Types and Locations

All tests are implemented using `pytest` and organized into `tests/unit`, `tests/integration`, and `tests/e2e` directories.

### a. Unit Tests (`tests/unit/`)
Focus: Isolated testing of individual functions or modules with mocked dependencies.
- **`test_build_catalog.py`**: Verifies that `scripts/build_catalog.py` generates `products.json` with 18 products and is idempotent.
- **`test_monetization_engine.py`**: Validates the `MonetizationEngine`'s ability to load products, filter by stage, and provide recommendations.
- **`test_stripe_products.py`**: Tests the logic within `scripts/create_new_stripe_products.py` for creating/updating Stripe products, prices, and payment links, using a mocked Stripe client.
- **`test_voice_monetization.py`**: Verifies the `VoiceSession`'s sales logic (e.g., handling price inquiries, cheapest options, and 'send link' requests).

### b. Integration Tests (`tests/integration/`)
Focus: Testing interactions between multiple components, often involving the FastAPI application or external services (mocked).
- **`test_api_endpoints.py`**: Tests the `/products` endpoint for correct filtering and recommendation responses. Also verifies analytics event recording via `POST /api/v1/analytics/event` and `unified_stripe_webhook`.
- **`test_catalog_build.py`**: Integration test for `scripts/build_catalog.py`, ensuring it correctly produces a valid `products.json`.
- **`test_stripe_sync_integration.py`**: Tests `scripts/create_new_stripe_products.py` with a mocked Stripe API to confirm idempotency and correct catalog updates.
- **`test_outreach_integration.py`**: Verifies the `SMTPOutreachTool`'s `DRY_RUN_MODE` and `OUTREACH_ENABLED` safety switches, ensuring emails are logged but not sent.

### c. End-to-End (E2E) Tests (`tests/e2e/`)
Focus: Simulating real user journeys across the entire system (frontend to backend to external services).
- **`test_web_checkout.py`**: (To be implemented) Will use a browser automation tool (e.g., Playwright) to simulate a user:
    - Navigating to the pricing page.
    - Selecting a product.
    - Clicking "Initiate Acquisition".
    - Verifying redirection to Stripe (mocked or test mode).
    - Confirming backend receives webhook events.
- **`test_voice_sales_e2e.py`**: (To be implemented) Will simulate a voice interaction with the `VoiceRouter` and `VoiceSession` to:
    - Verify product recommendation flow.
    - Test barge-in scenarios.
    - Confirm "send purchase link" triggers the expected actions (e.g., a mocked email send).

## 3. Smoke Tests (`scripts/test_monetization_smoke.py`)

A fast-running suite designed to quickly verify the health of critical monetization components on every code change.
- **Checks:**
    - Database connectivity (SQLite fallback).
    - Product catalog loading.
    - Correct loading of environment configurations.
    - (Future: Basic health check endpoint response for the FastAPI app).

## 4. How to Run Tests

### Run all tests:
```bash
pytest
```

### Run specific test types:
```bash
pytest tests/unit/
pytest tests/integration/
pytest pytest tests/e2e/
```

### Run smoke tests:
```bash
python scripts/test_monetization_smoke.py
```

### Running with Analytics Enabled (for testing analytics events):
To test analytics event recording, you must explicitly enable it:
```bash
ANALYTICS_ENABLED=True pytest tests/integration/test_api_endpoints.py::test_record_analytics_event_enabled
```

### Running with Stripe Live Mode (use with caution, only for real integration testing):
```bash
ENV_MODE=prod STRIPE_TEST_MODE=False pytest tests/integration/your_stripe_live_test.py
```
**Ensure `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY` are correctly set in `.env.prod` for this to work.**

## 5. Quality Gates & CI Readiness

- **Automated Checks:** All unit and integration tests must pass.
- **Linting:** Ensure no critical linting errors in monetization modules (`flake8`, `mypy`).
- **No Stub Code:** Production-critical paths must not contain `TODO` comments or placeholder code.
- **CI Integration:**
    - Configure GitHub Actions (or your CI tool) to run `pytest` (for unit/integration) and `playwright test` (for E2E) on pull requests and merges.
    - `scripts/test_monetization_smoke.py` can be used as a fast pre-commit hook.
