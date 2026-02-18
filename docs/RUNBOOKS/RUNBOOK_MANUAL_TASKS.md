# Manual Intervention Tasks

This runbook lists all tasks that **require manual intervention** and cannot be automated.

## REQUIRED FOR LAUNCH

### 1. Provision Production Secrets
- **Why**: Security. Secrets must never be committed to git.
- **How**:
  - Obtain real API keys for:
    - **Groq**: `GROQ_API_KEY` (Sign up at console.groq.com)
    - **Voice Providers**: `STT_API_KEY`, `TTS_API_KEY` (e.g., ElevenLabs, Deepgram)
    - **Payment**: `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`
  - Set them in your production environment (e.g., AWS Secrets Manager, GitHub Secrets, or `.env.prod` on the server).

### 2. Configure Brand Identity
- **Why**: The system generates marketing content. It needs your real brand voice.
- **How**:
  - Edit `.env` or production config:
    - `BRAND_NAME`
    - `PRODUCT_NAME`
    - `MARKETING_SITE_URL`
    - `CONTACT_EMAIL`
    - Social Handles (`SOCIAL_TWITTER_HANDLE`, etc.)
  - Run `python -m orchestrator.src.tools.marketing_check` to verify.

### 3. DNS & TLS
- **Why**: Users need a secure, custom domain.
- **How**:
  - Buy domain (e.g., via Namecheap/Route53).
  - Point A records to your Load Balancer / Server IP.
  - Generate SSL certificates (e.g., via Let's Encrypt / Certbot).

### 4. Create Production Database
- **Why**: Data persistence.
- **How**:
  - Provision a managed Postgres instance (RDS, CloudSQL, Supabase).
  - Get the connection string: `postgresql://user:pass@host:5432/db`.
  - Set `DATABASE_URL` env var.
  - Run migrations/seeding: `make seed-products`.

## OPTIONAL / POST-LAUNCH

### 1. Analytics Integration
- **Why**: Track user behavior.
- **How**: Add Google Analytics / PostHog snippets to `projects/templates/landing-page/index.html`.

### 2. Content Review
- **Why**: AI content is good, but human touch is better.
- **How**: Review drafts in `data/marketing/drafts/` before publishing.
