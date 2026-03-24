import asyncio
import os
import sys
import json
import random

# Ensure we can import from orchestrator
sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.tools.marketing_tools import get_marketing_tools
from orchestrator.src.tools.seo_tools import SEOTool, ToolConfig
from orchestrator.src.tools.social_tools import get_social_tools
from orchestrator.src.tools.smtp_tools import get_smtp_tools
from orchestrator.src.validation.schemas import ToolInvocation

logger = get_logger("HYPER_SCALE_MONETIZATION")

# TARGET KEYWORDS FOR SEO/CONTENT
NICHE_KEYWORDS = [
    ["AI Agents", "Automation", "Revenue"],
    ["Passive Income", "SaaS", "Stripe"],
    ["Cold Outreach", "B2B Sales", "Lead Gen"],
    ["Autonomous Swarms", "Python", "Orchestration"],
    ["Digital Marketing", "TikTok Viral", "Ad Copy"]
]

async def hyper_scale_loop():
    logger.info("🌌 INITIATING HYPER-SCALE MONETIZATION PROTOCOL 🌌")
    logger.info("Objective: Generate Content -> Publish -> Distribute -> Monetize")

    # Initialize Tools directly (Bypassing heavy orchestrator logic for raw speed if needed, 
    # but using Orchestrator is safer for state management. We'll mix them.)
    
    # 1. CONTENT FACTORY (SEO & BLOGS)
    seo_tool = SEOTool(ToolConfig(tool_id="seo_factory", name="SEO", description="SEO", parameters_schema={}, allowed_agents=["*"]))
    
    generated_blogs = []
    for keywords in NICHE_KEYWORDS:
        logger.info(f"📝 Generating Blog for: {keywords[0]}...")
        # SEOTool uses raw dict in execute() signature? Let's check. 
        # BaseTool says execute(invocation: ToolInvocation). 
        # But SEOTool might override it. Let's use raw dict if it overrides, or ToolInvocation if not.
        # Checking SEOTool implementation in previous turn... it takes `input_data: Dict[str, Any]`! 
        # It deviated from BaseTool signature. We'll use raw dict for SEO tool.
        result = seo_tool.execute({"action": "generate_and_publish", "keywords": keywords})
        
        if result.get("status") == "published":
            logger.info(f"✅ Blog Published: {result['url']}")
            generated_blogs.append(result)
        else:
            logger.error(f"❌ Blog Generation Failed: {result}")

    # 2. VIRAL MARKETING FACTORY (TikTok & Ads)
    marketing_tools = {t.config.tool_id: t for t in get_marketing_tools()}
    tiktok_gen = marketing_tools["tiktok_gen"]
    ad_gen = marketing_tools["ad_gen"]
    
    promoted_products = ["Jarvis 3.5 Enterprise", "Sovereign Brand Kit", "Elite Support Tier"]
    
    viral_scripts = []
    for prod in promoted_products:
        logger.info(f"🎥 Generating TikTok Script for: {prod}...")
        # Marketing tools expect ToolInvocation
        invoc = ToolInvocation(
            tool_id="tiktok_gen", 
            input_data={"product_name": prod}, 
            agent_id="hyper_scale_bot"
        )
        res = tiktok_gen.execute(invoc)
        if res.get("status") == "success":
            logger.info(f"✅ Script Generated for {prod}")
            viral_scripts.append(res['script'])
            
    # 3. DISTRIBUTION (Social Media)
    # Using the Orchestrator here to ensure we handle rate limits/tokens properly via the Multiplexer
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    for blog in generated_blogs:
        # Post Blog Link to Socials
        task = (
            f"Post this new blog article to LinkedIn and Facebook using 'multiplexer'. "
            f"Link: {blog['url']}. Message: 'New strategic intelligence dropped: {blog['local_path']}'."
        )
        logger.info(f"🚀 Distributing Blog: {blog['url']}")
        async for step in orchestrator.submit_task_stream(task, "distribution_swarm"):
            if step["status"] == "completed":
                logger.info("✅ Social Distribution Complete.")
            elif step["status"] == "failed":
                logger.warning(f"⚠️ Distribution Warning: {step.get('reason')}")

    # 4. DIRECT MONETIZATION (Cold Email)
    # Using scraped leads if available
    leads_path = "data/customers/leads.json"
    if os.path.exists(leads_path):
        with open(leads_path, "r") as f:
            leads = json.load(f)
            
        # Take 5 random leads to avoid spamming dev account
        target_leads = random.sample(leads, min(5, len(leads)))
        email_gen = marketing_tools["email_gen"]
        smtp_tools = {t.config.tool_id: t for t in get_smtp_tools()} 
        smtp_sender = smtp_tools["smtp_outreach"]
        
        for lead in target_leads:
            email_addr = lead.get("email") or "robert.demotto@realms2riches.com" # Fallback to user
            
            # Generate personalized content
            logger.info(f"📧 Generating Email for {email_addr}...")
            invoc_email = ToolInvocation(
                tool_id="email_gen",
                input_data={"product_name": "Jarvis 3.5", "target_audience": lead.get("name", "Founder")},
                agent_id="hyper_scale_bot"
            )
            content_res = email_gen.execute(invoc_email)
            
            if content_res.get("status") == "success":
                body = content_res["email_content"]
                # Send (SMTP tool expects ToolInvocation too? Let's check.)
                # SMTPOutreachTool.execute(invocation: ToolInvocation)
                logger.info(f"📤 Sending to {email_addr}...")
                
                invoc_smtp = ToolInvocation(
                    tool_id="smtp_outreach",
                    input_data={
                        "target_email": email_addr, 
                        "html_body": body,
                        "subject": "Strategic Partnership: Sovereign AI"
                    },
                    agent_id="hyper_scale_bot"
                )
                
                send_res = smtp_sender.execute(invoc_smtp)
                if send_res["status"] == "success":
                    logger.info("✅ Email Sent.")
                else:
                    logger.error(f"❌ Email Failed: {send_res.get('reason')}")

    logger.info("🏁 HYPER-SCALE CYCLE COMPLETE. CHECK STRIPE DASHBOARD.")

if __name__ == "__main__":
    asyncio.run(hyper_scale_loop())
