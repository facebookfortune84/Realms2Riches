# Realms2Riches: Cold Outreach System Overview

This document details the architecture and usage of the Cold Outreach System (Stream 12) within Realms2Riches. The system is designed for campaign-capable, deliverability-aware, and compliant email outreach.

## 1. Outreach Configuration & Safety

All core outreach settings are centralized for easy management and robust safety.

### Configuration (`orchestrator/src/core/outreach/config.py`)
This module defines critical parameters loaded from environment variables (`.env.prod`):

```python
# orchestrator/src/core/outreach/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class OutreachSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.prod", extra="ignore")

    OUTREACH_ENABLED: bool = False  # Global ON/OFF switch for all live sending
    OUTREACH_DRY_RUN: bool = True   # If True, emails are rerouted to TEST_RECIPIENT
    DAILY_SEND_LIMIT: int = 50      # Max emails per day per SMTP account
    PER_DOMAIN_LIMIT: int = 5       # Max emails to a single domain per day
    MIN_DELAY_SECONDS: int = 60     # Min delay between emails
    MAX_DELAY_SECONDS: int = 300    # Max delay between emails (randomized)
    REDIS_URL: str = "redis://redis:6379/0" # Redis URL for ARQ queue
    OUTREACH_TEST_RECIPIENT: str = "robertdemottojr83@gmail.com" # Target for dry runs

outreach_settings = OutreachSettings()
```

### Safety Flags
- `OUTREACH_ENABLED=False`: By default, live sending is disabled. To activate, set to `True`.
- `OUTREACH_DRY_RUN=True`: By default, all sends are rerouted to `OUTREACH_TEST_RECIPIENT`. To send to actual targets, set to `False`.

## 2. Email Template System

The system uses Markdown-based templates with Jinja-like placeholders for dynamic content.

### Template Storage
Templates are stored in `data/templates/outreach/`.

### Example Template (`data/templates/outreach/sequence_a_day0.md`)
```markdown
Subject: Strategic Intelligence for {{ name }}

Hello {{ name }},

I noticed your work at {{ company }}. Our industrial AI swarm, Jarvis, has identified a potential optimization for your {{ industry }} workflow.

You can view the specific entry node here: {{ link }}

Best,
Robert DeMotto
Realms2Riches

---
Unsubscribe: {{ unsubscribe_link }}
```

### Placeholders
Templates support dynamic fields such as `{{ name }}`, `{{ company }}`, `{{ industry }}`, `{{ link }}`, and `{{ unsubscribe_link }}`.

## 3. Campaign & Sequencing Model

The system supports multi-step campaigns targeted at specific lead segments.

### Campaign Definition (`orchestrator/src/core/outreach/campaigns.py`)
Campaigns are defined as classes that combine segment rules and a sequence of templates.

```python
# orchestrator/src/core/outreach/campaigns.py (simplified)
class OutreachCampaign:
    def __init__(self, campaign_id: str, name: str, segment_rules: Dict[str, Any], templates: List[CampaignTemplate]):
        self.campaign_id = campaign_id
        self.name = name
        self.segment_rules = segment_rules
        self.templates = templates
        # ... methods for running campaign ...

# Example:
async def get_outreach_campaigns(orchestrator: Orchestrator) -> List[OutreachCampaign]:
    # ... template loading ...
    campaigns = [
        OutreachCampaign(
            campaign_id="jarvis_basic_intro",
            name="Jarvis Basic Intro Sequence",
            segment_rules={"target_product_id": "jarvis_basic", "lead_source": "ycombinator_scrape"},
            templates=[day0_template] # Multi-step sequences would have more templates
        )
    ]
    # ...
    return campaigns
```

### Campaign Execution
Campaigns are executed by calling their `run()` method, which identifies leads, renders templates, and submits emails to the ARQ queue.

## 4. Deliverability & Compliance Guardrails

### Email Validation
`SMTPOutreachTool` (`orchestrator/src/tools/smtp_tools.py`) includes basic regex validation to reject malformed email addresses before sending.

### Unsubscribe Mechanism
All emails automatically include an unsubscribe link (if not already present), pointing to a backend endpoint (`/api/v1/outreach/unsubscribe`) which should log the preference.

### DMARC/DKIM/SPF (Doc-Level)
For optimal deliverability, ensure your sending domain has:
- **SPF (Sender Policy Framework)**: A DNS TXT record listing authorized senders.
- **DKIM (DomainKeys Identified Mail)**: A digital signature to verify sender identity.
- **DMARC (Domain-based Message Authentication, Reporting & Conformance)**: A policy to tell receivers how to handle emails that fail SPF or DKIM.
*These are DNS configurations and must be set up with your domain registrar/DNS provider.*

## 5. Background Processing with arq/redis

Email sending is offloaded to a background queue using `arq` and `Redis`.

### ARQ Worker (`orchestrator/src/core/worker.py`)
The `send_email_campaign_item` function processes individual emails asynchronously.

```python
# orchestrator/src/core/worker.py (simplified)
async def send_email_campaign_item(ctx, campaign_item: dict):
    # ... logic to call SMTPOutreachTool ...
    # Handles logging, retries, and dry-run mode.
```

### Queue Monitoring
The ARQ worker provides logging for:
- Emails queued: When `orchestrator.submit_email_campaign_item()` is called.
- Emails sent/simulated/failed: Logged by `SMTPOutreachTool` and `send_email_campaign_item`.

## How to Define and Run a Campaign

1.  **Define Templates:** Create `.md` files in `data/templates/outreach/`.
2.  **Define Campaign:** Add a new `OutreachCampaign` instance in `get_outreach_campaigns()` in `orchestrator/src/core/outreach/campaigns.py`.
3.  **Run Dry Run:**
    - Ensure `OUTREACH_ENABLED=True` and `OUTREACH_DRY_RUN=True` in `.env.prod`.
    - Execute the campaign (e.g., call `campaign.run()` from a script).
    - Check logs for rerouted emails to `OUTREACH_TEST_RECIPIENT`.
4.  **Go Live Safely:**
    - Ensure `OUTREACH_ENABLED=True` and `OUTREACH_DRY_RUN=False` in `.env.prod`.
    - Double-check your `SMTP_USER` and `SMTP_PASS` are valid (App Password).
    - Run the campaign. Monitor logs closely.
