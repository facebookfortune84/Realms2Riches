# Growth Engine v5.0.0

This document describes the autonomous growth mechanisms of Realms2Riches.

## Growth Architecture
The **Sovereign Growth Engine** utilizes 3 core vectors to drive traffic, nurture leads, and generate high-converting content.

### 1. SMTP Cold Outreach
The `smtp_outreach` tool (`orchestrator/src/tools/smtp_tools.py`) allows agents to execute direct B2B outreach sequences.
- **Provider**: Gmail/SMTP (Securely configured via `.env.prod`).
- **Targeting**: Agents scrape or use the lead generation data in `data/customers/leads.json`.
- **Workflow**: `email_gen` (Content) -> `smtp_outreach` (Dispatch).

### 2. SEO Content Factory
The `seo_factory` (`orchestrator/src/core/alchemy_engine.py`) provides high-precision SEO content generation.
- **Logic**: Automated keyword identification, content outlining, and metadata generation.
- **Output**: Blog posts, feature guides, and knowledge base articles.

### 3. Social Media Multiplexer
The `social_multiplexer` (`orchestrator/src/tools/social_tools.py`) enables cross-platform social engagement.
- **Platforms**: TikTok, Facebook, LinkedIn (Integrated via specific department cells).
- **Automation**: Viral script generation (TikTok), ad copy (Facebook), and professional ROI highlighting (LinkedIn).

## Operational Monitoring
Growth activities are monitored through the `MonetizationEngine`, with artifacts and results logged to the company's lineage registry.
