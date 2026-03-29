# SOP: MON-014 NEW PRODUCT LAUNCH

**Purpose:** Automate the end-to-end launch of a new monetization product.
**Category:** Monetization
**Agent:** Revenue Agent

## Preconditions
1. Client product configuration available (JSON/YAML).
2. Stripe test keys available in environment.
3. Access to `data/catalog/products.json`.

## Step-by-Step Actions

1.  **Catalog Registration:**
    - Run `python scripts/build_catalog.py` to ensure the new product is added to `data/catalog/products.json`.
    - Verify metadata (funnel_stage, upsell_to, cross_sell_with) is correct.
2.  **Stripe Integration:**
    - Run `python scripts/create_new_stripe_products.py` to sync with Stripe.
    - Validate the audit log in `data/catalog/stripe_sync_audit.json`.
3.  **Frontend Update:**
    - Verify the product appears in the pricing matrix on the Vercel frontend.
    - Trigger `FrontendDeveloper` to check layout and accessibility.
4.  **Analytics Instrumentation:**
    - Verify product view events are correctly firing in the frontend.
    - Check `/api/v1/analytics/event` for registration during test purchases.
5.  **Voice Sales Wiring:**
    - Update `VoiceSession` recommendation logic (if needed).
    - Validate via `tests/unit/test_voice_monetization.py`.
6.  **Outreach:**
    - Create a campaign entry in `orchestrator/src/core/outreach/campaigns.py`.
    - Run a dry-run campaign via `SMTPOutreachTool`.

## Checks
- Does the product appear on `/products`?
- Is there a valid Stripe checkout URL in the catalog?
- Does the voice agent suggest the product when queried for its category?

## Rollback
- If the sync fails: Delete the newly created product in Stripe and revert `products.json` from git.
