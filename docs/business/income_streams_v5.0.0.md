# Income Streams & Stripe Monetization v5.0.0

This document describes the 13 active income streams and Stripe monetization model.

## Monetization Model
Realms2Riches uses a **Multi-Vector Monetization Engine** (`orchestrator/src/core/monetization/engine.py`), which manages both **Affiliate Arbitrage** and **Direct SaaS Billing**.

### Income Streams Overview

| Stream Name | Revenue Model | Primary Integration |
|-------------|---------------|---------------------|
| **Affiliate Arbitrage** | Affiliate | ClickFunnels (Affiliate Link) |
| **API SaaS Billing** | Direct Billing | Stripe (Jarvis Basic) |
| **Lead Gen Broker** | Affiliate | Pollo AI (Affiliate Link) |
| **Digital Product Store** | Direct Billing | Stripe (Brand Kit / Consultation) |
| **Newsletter Sponsorship** | Ad Revenue | Brand Push (Affiliate Link) |
| **Print On Demand** | Affiliate | CapCut (Affiliate Link) |
| **Programmatic Ads** | Ad Revenue | TikTok Shop / VidIQ (Affiliate Links) |
| **Crypto Yield Farming** | Simulated | Startup Accelerator (Stripe) |
| **Paid Community** | Subscription | Stripe (Elite Support) |
| **Data Licensing API** | Enterprise | Stripe (Jarvis Custom) |
| **SEO Traffic** | Indirect | Jarvis Basic (Stripe) |
| **Cold Outreach** | Enterprise | Jarvis Custom (Stripe) |
| **Fast Deploy** | Direct Billing | Startup Accelerator (Stripe) |

## Stripe Integration
All direct billing is handled via **Stripe Checkout and Subscriptions**.

### Secure Configuration
- **Environment**: `.env.prod` contains `STRIPE_API_KEY` and `STRIPE_WEBHOOK_SECRET`.
- **Modes**: Test and Production keys are strictly separated via environment variables.

### Webhook Handling
A production-ready webhook handler is located at `/api/v1/monetization/webhook` (`orchestrator/src/core/monetization/webhooks.py`). 
- **Events**: `checkout.session.completed`, `customer.subscription.created`, `invoice.payment_failed`.
- **Actions**: Automated onboarding, access provisioning, and dunning sequences.
