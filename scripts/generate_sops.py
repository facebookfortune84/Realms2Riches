import os

sops = {
    # MONETIZATION STREAMS (13)
    "MON_001_AFFILIATE_ARBITRAGE": "Procedure for scraping TikTok Shop and ClickFunnels links and generating viral bridge pages.",
    "MON_002_API_SAAS_BILLING": "Standard for provisioning API keys and setting up Stripe metered billing.",
    "MON_003_LEAD_GEN_BROKER": "Workflow for extracting B2B leads and selling them to verified high-ticket partners.",
    "MON_004_DIGITAL_PRODUCT_STORE": "Protocol for generating and listing Brand Kits and Strategy Guides on the Sovereign Store.",
    "MON_005_NEWSLETTER_SPONSORSHIP": "Guidelines for pitching newsletter ad slots to AI vendors and SaaS founders.",
    "MON_006_PRINT_ON_DEMAND": "Workflow for generating AI art and listing it on integrated POD platforms.",
    "MON_007_PROGRAMMATIC_ADS": "Standard for ad-injection into auto-generated SEO blog posts.",
    "MON_008_CRYPTO_YIELD_FARMING": "Safety protocol for analyzing DeFi rates and posting risk-adjusted alerts.",
    "MON_009_PAID_COMMUNITY": "Onboarding flow for Discord/Telegram premium community members.",
    "MON_010_DATA_LICENSING": "Drafting enterprise agreements for RAG-memory datasets.",
    "MON_011_SEO_TRAFFIC": "Daily generation of 5 high-intent blog posts with ad-conversion hooks.",
    "MON_012_COLD_OUTREACH": "Execution of high-deliverability SMTP sequences using Oracle personas.",
    "MON_013_FAST_DEPLOY": "Protocol for spinning up new niche monetization sites in under 5 minutes.",

    # CONTENT & MARKETING (10)
    "MKT_001_TIKTOK_VIRALITY": "Hook-Value-CTA framework for sub-60 second short form video scripts.",
    "MKT_002_LINKEDIN_AUTHORITY": "Structure for technical long-form posts to drive enterprise leads.",
    "MKT_003_EMAIL_COPYWRITING": "Principles of the Jarvis 3.5 conversion-sharding email template.",
    "MKT_004_AD_COPY_PPC": "A/B testing guidelines for high-CTR Facebook and Google ad headlines.",
    "MKT_005_SEO_KEYWORD_RESEARCH": "Identifying low-difficulty, high-intent keywords for immediate ranking.",
    "MKT_006_IMAGE_GEN_PROMPTING": "Standardizing Flux/Midjourney prompts for consistent brand aesthetic.",
    "MKT_007_VIDEO_EDITING_DIRECTION": "Scene-by-scene instructions for autonomous video assembly.",
    "MKT_008_SOCIAL_MEDIA_BROADCAST": "Multiplexer schedule for omni-channel presence (FB, X, LinkedIn).",
    "MKT_009_LEAD_NURTURE_SEQUENCE": "7-day auto-responder logic for email subscribers.",
    "MKT_010_BRAND_VOICE_ALIGNMENT": "Ensuring all content sounds like the Sovereign Architect persona.",

    # TECHNICAL & MAINTENANCE (10)
    "TEC_001_DB_SCHEMA_MIGRATION": "Safely applying SQL patches via the Self-Healing service.",
    "TEC_002_DEPENDENCY_AUDIT": "Weekly scan of requirements.txt for vulnerabilities and updates.",
    "TEC_003_LOG_ROTATION": "Pruning swarm_activity.log once it exceeds 100MB threshold.",
    "TEC_004_RAG_MEMORY_INDEXING": "Cleaning and re-embedding sovereign_memory.json every 24 hours.",
    "TEC_005_DOCKER_CONTAINER_UPKEEP": "Pruning orphaned images and volumes to maintain disk health.",
    "TEC_006_API_KEY_ROTATION": "Safety protocol for rotating Stripe and Groq keys without downtime.",
    "TEC_007_ERROR_HANDLING_HARDENING": "Wrapping tool calls in Pydantic-validated try/except blocks.",
    "TEC_008_CODE_COMPILATION_TEST": "Running compileall before every Vanguard deployment.",
    "TEC_009_SUBMODULE_SYNC": "Aligning primary core with core_secondary assets.",
    "TEC_010_TELEMETRY_DASHBOARD": "Aggregating latency and wage metrics for the weekly audit.",

    # STRATEGY & GOVERNANCE (7)
    "GOV_001_TICKET_ISSUANCE": "Standard for generating verifiable work orders for all swarm tasks.",
    "GOV_002_PERSONA_RESONANCE": "How agents autonomously select the most effective Oracle persona.",
    "GOV_003_REVENUE_RECONCILIATION": "Syncing Stripe event logs with internal SQLStore records.",
    "GOV_004_AUTONOMOUS_BACKLOG": "Algorithm for filling idle time with high-priority maintenance.",
    "GOV_005_TASK_PRIORITIZATION": "Logic for assigning Critical/High priority tags based on ROI.",
    "GOV_006_AGENT_ONBOARDING": "Steps for tax ID issuance and wage tier assignment.",
    "GOV_007_LINEAGE_SIGNATURE": "Cryptographic signing of all agent-generated artifacts.",

    # SECURITY & INTEGRITY (10)
    "SEC_001_SECRET_PROTECTION": "Ban on logging or committing .env variables or API keys.",
    "SEC_002_SANDBOX_ENFORCEMENT": "Mandatory use of Docker for untested agent-generated code.",
    "SEC_003_PHISHING_DEFENSE": "Verifying sender reputation before processing incoming webhook payloads.",
    "SEC_004_IP_REPUTATION_MANAGEMENT": "Monitoring SMTP relay health to prevent blacklisting.",
    "SEC_005_DATA_PRIVACY_GDPR": "Handling PII (Emails/Names) according to global standards.",
    "SEC_006_INJECTION_PREVENTION": "Sanitizing LLM outputs before passing them to shell or DB tools.",
    "SEC_007_RATE_LIMITING_SMTP": "Strict 50-email-per-hour limit to maintain Gmail standing.",
    "SEC_008_STASIS_BRANCH_LOCK": "No-manual-edit policy for the archival stasis branch.",
    "SEC_009_VIRTUAL_ENV_ISOLATION": "Ensuring all swarm nodes run in dedicated venvs.",
    "SEC_010_AUDIT_TRAIL_INTEGRITY": "Protecting activity logs from unauthorized modification."
}

os.makedirs("data/oracle/sop", exist_ok=True)

for code, desc in sops.items():
    file_path = f"data/oracle/sop/{code}.md"
    content = f"# SOP: {code.replace('_', ' ')}\n**Description:** {desc}\n\n## Mandatory Procedures\n1. Initialize Oracle Persona.\n2. Fetch relevant data from RAG memory.\n3. Execute with high-precision tool usage.\n4. Log artifacts to Lineage Registry.\n5. Mark ticket as RESOLVED.\n"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(sops)} SOPs in data/oracle/sop/")
