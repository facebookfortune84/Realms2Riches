# SOP: Stripe Webhook Integration & Security - v2.1

## Objective
Establish and secure an industrial-grade webhook listener to capture real-time payment events from Stripe and trigger autonomous fulfillment loops and commission attribution. This SOP guides through setup, security, and testing for production readiness.

## 1. Set Up Stripe Webhook Endpoint

1.  **Navigate to Stripe Dashboard:** Log in to your Stripe account at [dashboard.stripe.com](https://dashboard.stripe.com).
2.  **Webhook Configuration:** Go to **Developers > Webhooks**.
3.  **Add Endpoint:** Click **+ Add endpoint**.
    *   **Endpoint URL:** Enter your production backend URL followed by the webhook path.
        *   Example: `https://api.realms2riches.com/api/v1/monetization/webhook` (Ensure this matches your deployed API's webhook path).
    *   **Events to listen to:** Select the following critical events:
        *   `checkout.session.completed` (Primary for sales and fulfillment)
        *   `payment_intent.succeeded`
        *   `customer.subscription.created`
        *   `invoice.payment_succeeded`
        *   *(Add others as needed for specific fulfillment logic, e.g., `charge.disputed`)*
4.  **Create Endpoint:** Click **Add endpoint**.

## 2. Procure the Webhook Signing Secret

1.  **Endpoint Details:** After creating the endpoint, click on it in the Webhooks list to view its details.
2.  **Signing Secret:** Locate the **Signing secret** section.
3.  **Reveal & Copy:** Click **Reveal** to display the `whsec_...` key. Copy this secret immediately. **Treat this secret like an API key; it is sensitive.**

## 3. Secure Environment Variables

1.  **Locate `.env.prod`:** Open your project's `.env.prod` file.
2.  **Add/Update Secret:** Add or update the following variable with the copied secret:
    ```env
    STRIPE_WEBHOOK_SECRET=whsec_your_copied_secret_here
    ```
3.  **Restart Services:** Ensure your backend services (FastAPI app) are restarted after updating `.env.prod` for the new secret to be loaded. This is typically handled by `SOVEREIGN_START.ps1` or your CI/CD pipeline.

## 4. Local Testing with Stripe CLI

Use the Stripe CLI for efficient local testing and development.

1.  **Install Stripe CLI:** Follow instructions at [stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli).
2.  **Log In:** Authenticate with your Stripe account: `stripe login`.
3.  **Forward Events:** Set up event forwarding to your local webhook endpoint. Ensure your local server is running (e.g., `uvicorn orchestrator.src.core.api:app --port 8000`). Then run:
    ```bash
    # Ensure ngrok is running and exposing port 8000 if testing remotely
    # If running API directly on localhost:8000
    # stripe listen --forward-to localhost:8000/api/v1/monetization/webhook

    # For Realms2Riches API running via ngrok
    stripe listen --forward-to glowfly-sizeable-lazaro.ngrok-free.dev/api/v1/monetization/webhook
    ```
    The CLI will provide a webhook signing secret and forward events.
4.  **Simulate Events:** Trigger specific events to test your webhook logic:
    ```bash
    stripe trigger checkout.session.completed --api-key YOUR_STRIPE_SECRET_KEY --class checkout.session
    stripe trigger payment_intent.succeeded --api-line-items '[{"price":"price_1...", "quantity":1}]' # Example for more specific triggers
    ```

## 5. Code Implementation & Verification

### Backend (`scripts/stripe_webhook_listener.py`)
-   **Signature Verification:** The `stripe.Webhook.construct_event` function is crucial for validating that requests originate from Stripe. This is handled in the `try...except stripe.error.SignatureVerificationError` block.
-   **Event Handling:** The webhook endpoint parses the event and checks `event["type"]` to determine the appropriate action.
-   **Asynchronous Fulfillment:** Long-running tasks (like swarm provisioning or commission attribution) are handled asynchronously using `background_tasks.add_task()`.
-   **Fulfillment Logic (`fulfill_order`):** This function handles:
    *   Logging sales to the `profit_ledger`.
    *   **Affiliate Commission Attribution:** Checks `session_data.metadata.affiliate_code`, queries the `Affiliate` table, calculates commission, and records it in the `commissions` table.
    *   **Genesis Forge Provisioning:** Triggers swarm generation if `product_id` metadata indicates a genesis purchase.
    *   Updating telemetry (`revenue`, `conversions`).
    *   Logging actions to `activity_log`.
-   **Error Handling:** Robust error handling for invalid payloads, signature verification failures, and general exceptions during fulfillment.

### 6. Production Deployment Considerations
-   **HTTPS:** Always use HTTPS for your webhook endpoint in production. Ngrok provides this for local testing.
-   **Event Filtering:** Configure your Stripe webhook to send only the necessary events to reduce traffic and processing overhead.
-   **Idempotency:** Ensure your fulfillment logic is idempotent to safely handle Stripe's event retries. The use of `session_id` and logging helps prevent duplicate processing.

---
*SOP Version: 2.1 | Last Updated: March 10, 2026*
*Authored by: Realms2Riches AI Core*
