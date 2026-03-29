# Realms2Riches: Monetization & Outreach Setup Guide

This document outlines the procedure for taking the Realms2Riches monetization stack live.

## 1. Required Environment Variables (.env.prod)

Ensure these variables are correctly set in your `.env.prod` file.

### Stripe Configuration
| Variable | Description |
| :--- | :--- |
| `STRIPE_API_KEY` | Your live Stripe Secret Key (`sk_live_...`). |
| `STRIPE_PUBLISHABLE_KEY` | Your live Stripe Publishable Key (`pk_live_...`). |
| `STRIPE_WEBHOOK_SECRET` | Obtained from the Stripe Dashboard after setting up your webhook endpoint. |

### SMTP & Outreach Configuration
| Variable | Description |
| :--- | :--- |
| `SMTP_USER` | Your email address (e.g., `robertdemottojr83@gmail.com`). |
| `SMTP_PASS` | Your App Password (not your account password). |
| `SMTP_SERVER` | SMTP host (default: `smtp.gmail.com`). |
| `SMTP_PORT` | SMTP port (465 for SSL, 587 for TLS). |
| `OUTREACH_ENABLED` | Set to `True` to enable real email dispatch. |
| `DRY_RUN_MODE` | Set to `False` to send to real targets. If `True`, all emails go to `OUTREACH_TEST_RECIPIENT`. |
| `OUTREACH_TEST_RECIPIENT`| The fallback email for dry runs. |

## 2. Stripe Product Synchronization

The system uses a centralized catalog in `data/catalog/products.json`. To sync this with your live Stripe account:

1.  **Generate the Catalog:**
    ```bash
    python scripts/build_catalog.py
    ```
2.  **Sync with Stripe:**
    ```bash
    python scripts/create_new_stripe_products.py
    ```
    *This script is idempotent. It will only create products that do not yet exist in your Stripe account based on the product name.*

## 3. Webhook Setup

1.  Go to the Stripe Dashboard -> Developers -> Webhooks.
2.  Add an endpoint: `https://api.realms2riches.com/api/v1/monetization/webhook`
3.  Select event: `checkout.session.completed`.
4.  Copy the **Signing Secret** and paste it as `STRIPE_WEBHOOK_SECRET` in your `.env.prod`.

## 4. "Go-Live" Checklist

### Payments
- [ ] `ENV_MODE=prod` is set in `.env.prod`.
- [ ] `STRIPE_API_KEY` starts with `sk_live_`.
- [ ] `STRIPE_WEBHOOK_SECRET` is verified.
- [ ] Run `scripts/create_new_stripe_products.py` and verify success logs.
- [ ] Perform a test transaction using a real card or Stripe Test Card (if in test mode).

### Outreach
- [ ] `OUTREACH_ENABLED=True`.
- [ ] `DRY_RUN_MODE=True` (for initial testing).
- [ ] `SMTP_PASS` is a valid App Password.
- [ ] Run `scripts/verify_smtp_stream.py` and check the test recipient's inbox.
- [ ] Set `DRY_RUN_MODE=False` only when ready for mass outreach.

