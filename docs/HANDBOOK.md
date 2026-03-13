# Realms2Riches: Autonomous Swarm Operator's Handbook

This modular handbook consolidates all critical architectural, operational, and marketing playbooks into a single source of truth for the Sovereign Agentic Orchestrator.

## Table of Contents
1. [Core Architecture & Governance](#core-architecture--governance)
2. [Interactive Installation & Operations Guide](#interactive-installation--operations-guide)
3. [The 13 Monetization Streams (YOLO Mode)](#the-13-monetization-streams-yolo-mode)
4. [Long-Term Scaling: The Dual-Core Strategy (Hot/Cold)](#long-term-scaling-the-dual-core-strategy-hotcold)
5. [Content, Marketing & Community](#content-marketing--community)

---

## 1. Core Architecture & Governance

The Realms2Riches platform is a highly concurrent multi-agent system defaulting to **Groq (Llama-3)** for high-speed inference.

*   **The Orchestrator:** The central nervous system (`src/core/orchestrator.py`), routing tasks to specialized departments (Architects, Frontend, Growth, Revenue).
*   **Persistence:** Hybrid SQLite (Local) / PostgreSQL (Production).
*   **Governance:** To maintain system integrity at scale, all generated code and configurations must be audited. We utilize a `hash_registry.py` script to enforce a cryptographic lock on code lineage, tagging git commits with revenue estimates to trace ROI back to specific codebase states.
*   **Validation:** A relentless execution loop ensures tasks are not merely generated but executed, monitored, and verified against real-world metrics (e.g., Stripe webhooks, live link scraping).

---

## 2. Interactive Installation & Operations Guide

To operate the swarm securely and effectively, follow this guide. **Never run the orchestrator in full production without containerization.**

### Prerequisites
*   Python 3.11+ (managed via Poetry)
*   Docker & Docker Compose
*   A Groq API Key and Stripe API Key

### Step-by-Step Installation
1.  **Clone & Isolate:**
    ```bash
    git clone https://github.com/facebookfortune84/Realms2Riches.git
    cd Realms2Riches
    cp .env.example .env
    ```
2.  **Environment Configuration:**
    Open `.env` and configure your API keys. **CRITICAL:** Ensure `GROQ_API_KEY`, `STRIPE_API_KEY`, and database credentials are set. If deploying, set `ENVIRONMENT=production`.
3.  **Bootstrap Infrastructure (PostgreSQL & Vector Store):**
    ```bash
    docker-compose up -d postgres
    ```
4.  **Install Python Dependencies:**
    ```bash
    poetry install
    ```
5.  **Initialize the Verification Scripts:**
    Before launching agents, run the system integrity checks to ensure the pipeline is clear:
    ```bash
    python scripts/test_system_integrity.py
    ```

### Daily Operations Runbook
The swarm operates autonomously but requires daily oversight:
*   **Morning Audit:** `python scripts/verify_production_capabilities.py`
*   **Monetization Run:** `python scripts/yolo_mode_monetization.py`
*   **Evening Lineage Lock:** `python scripts/hash_registry.py` (Tags git repo with daily revenue state).

---

## 3. The 13 Monetization Streams (YOLO Mode)

The core driver of the platform is the `MonetizationEngine` (`src/core/monetization/engine.py`), capable of executing 13 distinct revenue streams concurrently.

**Active Streams:**
1.  **Affiliate Arbitrage:** ClickFunnels, HighLevel.
2.  **API SaaS Billing:** Selling Jarvis 3.5 API access.
3.  **Lead Gen Broker:** Voice/Video AI leads (Pollo AI, PlayHT).
4.  **Digital Product Store:** Business Consultations, Brand Kits.
5.  **Newsletter Sponsorships:** Brand Push integrations.
6.  **Print on Demand / Automated Edits:** CapCut integrations.
7.  **Programmatic Ads:** TikTok Shop, VidIQ.
8.  **Crypto Yield Farming:** Startup Accelerator vaults.
9.  **Paid Community:** Elite Support (Stripe recurring).
10. **Data Licensing API:** Enterprise Custom Deals.
11. **SEO Traffic Engine:** Organic ranking for core products.
12. **Cold Outreach:** Pinging enterprise targets.
13. **Fast Deploy (Instant Swarm):** Selling $499 setup instances.

*To activate all streams concurrently, execute:*
`python scripts/yolo_mode_monetization.py`

---

## 4. Long-Term Scaling: The Dual-Core Strategy (Hot/Cold)

To scale from 1,000 to 100,000 parallel agents safely, the current single-threaded Python/Groq tunnel will become a bottleneck. The system must transition to a **Dual-Core (Hot/Cold) Architecture**.

### Phase 1: The "Cold" Core (Current State)
*   **Function:** Foundation, initial configuration, and steady-state asynchronous tasks (SEO generation, long-form content, scheduled tweets).
*   **Tech:** Python `asyncio`, single SQLite/Postgres DB, single Groq API key connection.
*   **Limit:** Highly susceptible to API rate limits, IP bans, and memory saturation during concurrent web scraping.

### Phase 2: The "Hot" Core (High-Velocity Expansion)
*   **Function:** Relentless, concurrent execution of high-volume tasks (Cold Outreach, real-time scraping, live customer negotiation).
*   **Architecture:**
    *   **Message Broker (Kafka/RabbitMQ):** Tasks generated by the Cold Core are pushed to a high-throughput queue.
    *   **Distributed Worker Nodes:** 1,000+ lightweight Docker containers running on cloud infrastructure (e.g., AWS Fargate, Kubernetes) pull tasks from the queue.
    *   **Rotating Proxies:** Essential for scraping and outreach to avoid IP bans.
    *   **Multi-Key Orchestration:** The orchestrator manages a pool of Groq/OpenAI keys, dynamically routing requests to avoid rate limits.
*   **The Bridge (MCP Server):** A custom Model Context Protocol (MCP) server will act as the bridge between the Cold Core (where the AI makes strategic decisions) and the Hot Core (the distributed Kubernetes cluster executing the tasks). This MCP server will allow the AI to monitor worker health, dynamically scale up nodes, and verify distributed payouts in real-time.

---

## 5. Content, Marketing & Community

The swarm autonomously generates marketing content based on the brand identity configured in `.env`.

*   **Brand Identity:** Ensure `BRAND_NAME`, `MARKETING_SITE_URL`, and social handles are accurate. The agents use these to construct the `SOCIAL_VALIDATOR` logic.
*   **Content Generation:** Managed via the `vector_store`. Ensure the `docs/CONTENT_CALENDAR.md` is populated with initial seed ideas; the swarm will take over optimization based on engagement metrics.
*   **Outreach:** Emails are managed via `docs/EMAIL_SEQUENCES.md`. The Cold Outreach stream utilizes these templates, dynamically injecting the target's personalized data retrieved via web scraping.
