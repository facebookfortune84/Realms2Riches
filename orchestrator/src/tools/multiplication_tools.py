import os
import json
import logging
import base64
import re
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class OutreachSwarmTool(BaseTool):
    """
    Industrial Outreach Monetization Tool.
    Uses Gmail API for high-deliverability and Oracle prompts for elite copywriting.
    """
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.creds_file = "data/auth/gmail_credentials.json"
        self.token_file = "data/auth/gmail_token.json"
        os.makedirs("data/auth", exist_ok=True)

    def _get_gmail_service(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        # INDUSTRIAL UPGRADE: Requesting full modify access to enable the Nurturer/Closer
        scopes = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        creds = None
        
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, scopes)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.creds_file):
                    raise Exception(f"Industrial Error: {self.creds_file} missing. Get it from Google Cloud Console.")
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data
        target_email = params.get("target_email")
        # FORCE VALIDATION: No placeholders allowed.
        if not target_email or "@" not in str(target_email) or "." not in str(target_email) or len(str(target_email)) < 5:
            logger.error(f"🛑 REJECTING INVALID EMAIL: {target_email}")
            return {"status": "error", "reason": f"Invalid email format: {target_email}"}
        
        target_name = params.get("target_name", "Entrepreneur")
        product_key = params.get("product_key", "jarvis_premium")
        
        product_map = {
            "jarvis_basic": {"name": "Jarvis 3.5 Basic", "link": "https://buy.stripe.com/dRm00jg25aw120i5hh8so00", "price": "$29.99/mo"},
            "jarvis_custom": {"name": "Jarvis 3.5 Custom", "link": "https://buy.stripe.com/6oUeVdcPTeMheN46ll8so01", "price": "Custom"},
            "jarvis_premium": {"name": "Jarvis 3.5 Premium", "link": "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02", "price": "$199.99/mo"},
            "digital_domination": {"name": "Digital Domination Package", "link": "https://buy.stripe.com/eVqeVd17b5bHfR87pp8so0d", "price": "$4,499.00"},
            "startup_accelerator": {"name": "Startup Accelerator Bundle", "link": "https://buy.stripe.com/28E6oHbLP33z6gyaBB8so0c", "price": "$1,999.00"},
            "consultation": {"name": "Business Management Consultation", "link": "https://buy.stripe.com/00w8wP7vzcE97kC3998so03", "price": "$300.00"}
        }
        
        product = product_map.get(product_key, product_map["jarvis_premium"])
        conversion_link = product["link"]
        product_name = product["name"]
        
        subject = f"Strategic Revenue Intelligence for {target_name}"
        
        # Oracle-style Elite HTML Copy
        html_body = f"""
        <html>
        <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #663399; margin-bottom: 5px;">Realms2Riches</h1>
                <p style="font-style: italic; color: #666; margin-top: 0;">Autonomous Revenue Operations</p>
            </div>
            
            <p>Hi {target_name},</p>
            <p>I noticed your recent growth and identified a significant opportunity to optimize your revenue infrastructure using high-density autonomous AI swarms.</p>
            <p>We are currently deploying <strong>Jarvis 3.5</strong> units for leaders who require zero-latency execution across SEO, lead generation, and automated conversion sharding.</p>
            
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h3 style="color: #663399; margin-top: 0;">The {product_name} Advantage:</h3>
                <ul style="padding-left: 20px;">
                    <li><strong>Autonomous Market Dominance:</strong> Scaling technical authority 24/7.</li>
                    <li><strong>Precision Lead Capture:</strong> Playwright-driven extraction of high-intent buyers.</li>
                    <li><strong>Integrated Conversion Loops:</strong> Seamless Stripe-hosted checkout and fulfillment.</li>
                </ul>
            </div>

            <p style="text-align: center; margin-top: 35px; margin-bottom: 35px;">
                <a href="{conversion_link}" 
                   style="background-color: #663399; color: white; padding: 15px 35px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.1em; box-shadow: 0 4px 15px rgba(102, 51, 153, 0.3);">
                   SECURE YOUR SOVEREIGN LICENSE
                </a>
            </p>
            
            <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="font-size: 0.9em; color: #777;">
                <strong>Robert DeMotto</strong><br>
                Principal Architect | Realms2Riches<br>
                <a href="mailto:robert.demotto@realmstoriches.xyz" style="color: #663399; text-decoration: none;">robert.demotto@realmstoriches.xyz</a>
            </p>
        </body>
        </html>
        """

        try:
            # Validate Email Format before sending
            if not target_email or not re.match(r"[^@]+@[^@]+\.[^@]+", target_email):
                logger.warning(f"Invalid target email detected: {target_email}. Skipping.")
                return {"status": "error", "reason": f"Invalid email format: {target_email}"}

            service = self._get_gmail_service()
            
            message = MIMEText(html_body, 'html')
            message['to'] = target_email
            message['from'] = f"Robert DeMotto - Realms2Riches <{settings.SMTP_USER}>"
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            logger.info(f"Industrial Dispatch: Sending Oracle Pitch ({product_name}) to {target_email} via Gmail API")
            
            send_res = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
            
            return {
                "status": "success", 
                "action": "industrial_outreach_dispatched", 
                "method": "gmail_api",
                "message_id": send_res.get("id"),
                "target": target_email,
                "product": product_name
            }
        except Exception as e:
            logger.error(f"Industrial Outreach Failed: {e}")
            return {"status": "error", "reason": f"Industrial Error: {str(e)}"}

class SEOContentFactoryTool(BaseTool):
    """
    Sovereign SEO Factory.
    Implements technical authority generation.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data
        topic, keywords = params.get("topic"), params.get("keywords", [])
        
        slug = f"technical-breakdown-{topic.lower().replace(' ', '-')}"
        path = f"data/blog/{slug}.md"
        
        content = f"""# {topic}
Technical Authority generated by Sovereign Intelligence Network.

### Executive Overview
This document outlines the strategic deployment of agentic swarms within the {topic} sector to dominate search intent and capture high-density lead volume.

### Core Implementation Nodes
- **Node A:** Scalable vector sharding for high-fidelity memory retrieval.
- **Node B:** Autonomous lead capture via Playwright-driven browser agents targeting {topic} stakeholders.
- **Node C:** High-conversion conversion loops integrated with Stripe financial protocols.

### Strategic Directive
Deploying Jarvis 3.5 autonomous units allows for the total automation of top-of-funnel content production, ensuring that search authority is established within sub-5 minute windows across global indices.

[🛒 SECURE YOUR SOVEREIGN LICENSE](https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02)
"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "success", "blog_path": path, "slug": slug}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

def get_multiplication_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {
        "target_email": {"type": "string"},
        "target_name": {"type": "string"},
        "product_key": {"type": "string", "enum": ["jarvis_basic", "jarvis_custom", "jarvis_premium", "digital_domination", "startup_accelerator", "consultation"]}
    }}
    return [
        OutreachSwarmTool(ToolConfig(tool_id="outreach", name="Outreach", description="Industrial Outreach Funnel", parameters_schema=cfg, allowed_agents=["*"])),
        SEOContentFactoryTool(ToolConfig(tool_id="seo_factory", name="SEO", description="Mass Organic Funnel", parameters_schema=cfg, allowed_agents=["*"]))
    ]
