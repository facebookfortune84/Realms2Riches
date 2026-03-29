import os
from typing import List, Dict, Any, Optional

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class CampaignTemplate:
    def __init__(self, template_id: str, subject: str, body: str, days_offset: int = 0):
        self.template_id = template_id
        self.subject = subject
        self.body = body
        self.days_offset = days_offset

    def render(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Renders the template with provided context."""
        rendered_subject = self.subject
        rendered_body = self.body
        for key, value in context.items():
            rendered_subject = rendered_subject.replace(f"{{{{ {key} }}}}", str(value))
            rendered_body = rendered_body.replace(f"{{{{ {key} }}}}", str(value))
        return {"subject": rendered_subject, "html_body": rendered_body}

class OutreachCampaign:
    def __init__(self, campaign_id: str, name: str, segment_rules: Dict[str, Any], templates: List[CampaignTemplate]):
        self.campaign_id = campaign_id
        self.name = name
        self.segment_rules = segment_rules
        self.templates = templates
        self.orchestrator: Optional[Orchestrator] = None

    def set_orchestrator(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    async def _send_email_for_lead(self, lead: Dict[str, Any], template: CampaignTemplate, product: Dict[str, Any]):
        """Renders and enqueues a single email for a lead."""
        context = {
            "name": lead.get("name", lead.get("first_name", "Valued Client")),
            "email": lead["email"],
            "company": lead.get("company", "Your Company"),
            "industry": lead.get("industry", "Business"),
            "product_name": product["name"],
            "product_description": product["description"],
            "link": product["checkout_url"],
            "unsubscribe_link": f"{settings.BACKEND_URL}/api/v1/outreach/unsubscribe?email={lead['email']}" # Placeholder
        }
        rendered_email = template.render(context)
        
        campaign_item = {
            "target_email": lead["email"],
            "subject": rendered_email["subject"],
            "html_body": rendered_email["html_body"],
            "campaign_id": self.campaign_id,
            "product_id": product["id"]
        }
        
        if self.orchestrator:
            await self.orchestrator.submit_email_campaign_item(campaign_item)
        else:
            logger.error(f"Orchestrator not set for campaign {self.campaign_id}. Cannot enqueue email.")

    async def run(self):
        """Executes the campaign, identifying leads and submitting emails to the queue."""
        if not self.orchestrator:
            logger.error(f"Cannot run campaign {self.campaign_id}: Orchestrator not set.")
            return

        logger.info(f"🚀 Running outreach campaign: {self.name} (ID: {self.campaign_id})")

        # Load leads (mock for now)
        leads = [
            {"name": "Alice", "email": "alice@example.com", "company": "Tech Innovations", "industry": "Software"},
            {"name": "Bob", "email": "bob@example.com", "company": "Global Corp", "industry": "Finance"},
        ] # Replace with actual lead loading logic later

        # Load products (from MonetizationEngine)
        monetization_engine = self.orchestrator.monetization_engine # Assuming orchestrator has a monetization_engine instance
        target_product_id = self.segment_rules.get("target_product_id", "jarvis_basic")
        product = next((p for p in monetization_engine._products if p["id"] == target_product_id), None)

        if not product:
            logger.error(f"Target product {target_product_id} not found for campaign {self.campaign_id}.")
            return

        for lead in leads:
            # For simplicity, send day 0 template to all leads
            template = next((t for t in self.templates if t.days_offset == 0), None)
            if template:
                await self._send_email_for_lead(lead, template, product)
            else:
                logger.warning(f"No Day 0 template found for campaign {self.campaign_id}.")

        logger.info(f"🏁 Campaign {self.name} finished lead processing.")

# Example Campaign Definitions
async def get_outreach_campaigns(orchestrator: Orchestrator) -> List[OutreachCampaign]:
    # Ensure template directory exists
    template_dir = "data/templates/outreach"
    os.makedirs(template_dir, exist_ok=True)

    # Example template (defined inline for now, but would load from file)
    day0_template_path = os.path.join(template_dir, "sequence_a_day0.md")
    if not os.path.exists(day0_template_path):
        with open(day0_template_path, "w") as f:
            f.write("""Subject: Strategic Intelligence for {{ name }}

Hello {{ name }},

I noticed your work at {{ company }}. Our industrial AI swarm, Jarvis, has identified a potential optimization for your {{ industry }} workflow.

You can view the specific entry node here: {{ link }}

Best,
Robert DeMotto
Realms2Riches

---
Unsubscribe: {{ unsubscribe_link }}
""")
    
    with open(day0_template_path, "r") as f:
        template_content = f.read()
        subject_match = re.search(r"Subject: (.*)", template_content)
        subject = subject_match.group(1).strip() if subject_match else "Default Subject"
        body = template_content.split("---", 1)[0].strip().replace(subject_match.group(0), "").strip() if subject_match else template_content
        day0_template = CampaignTemplate("sequence_a_day0", subject, body, 0)


    campaigns = [
        OutreachCampaign(
            campaign_id="jarvis_basic_intro",
            name="Jarvis Basic Intro Sequence",
            segment_rules={"target_product_id": "jarvis_basic", "lead_source": "ycombinator_scrape"},
            templates=[day0_template]
        )
    ]

    for campaign in campaigns:
        campaign.set_orchestrator(orchestrator)
    
    return campaigns
