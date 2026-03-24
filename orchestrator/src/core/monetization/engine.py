import logging
import asyncio
import json
import random
import os
from typing import Dict, Any, List
from orchestrator.src.core.config import settings

logger = logging.getLogger(__name__)

# SCRAPED AFFILIATE AND MONETIZATION LINKS
AFFILIATE_LINKS = {
    "tiktok_shop": "https://thesuperlink.com/tiktokshop?ref=robertdemottojr&source=realmstoriches",
    "highlevel": "https://www.gohighlevel.com/?fp_ref=realmstoriches",
    "capcut": "https://capcutaffiliateprogram.pxf.io/realmstoriches",
    "clickfunnels": "https://www.plrfunnels.com/plr?aff=b227fabeecb5b9674bf510b0714f0569236d7bbd6ceb3c3ac3f92061ea372fab",
    "brand_push": "https://www.brandpush.co/?ref=57120",
    "pollo_ai": "https://pollo.ai/invitation-landing?invite_code=pIY2cF",
    "play_ht": "https://www.play.ht/?via=robert-demotto-jr",
    "vidiq": "https://vidiq.com/realmstoriches",
}

STRIPE_MONETIZATION = {}
try:
    with open("data/catalog/products.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)
        for p in catalog:
            link = p.get('checkout_url') or p.get('payment_link')
            if link:
                STRIPE_MONETIZATION[p['id']] = link
except Exception as e:
    logger.warning(f"Failed to load catalog for monetization: {e}")

# Fallback / Default Stripe Links if catalog load fails or keys missing
if not STRIPE_MONETIZATION:
    STRIPE_MONETIZATION = {
        "jarvis_basic": "https://buy.stripe.com/7sY7sLeY1aw1cEWcJJ8so0e",
        "jarvis_custom": "https://buy.stripe.com/eVqeVd17b5bHfR87pp8so0d",
        "jarvis_premium": "https://buy.stripe.com/28E6oHbLP33z6gyaBB8so0c",
        "business_consultation": "https://buy.stripe.com/eVqbJ13fj5bH48q9xx8so0b",
        "brand_kit": "https://buy.stripe.com/28E00jaHLgUp20i5hh8so0a",
        "elite_support": "https://buy.stripe.com/5kQ4gzcPTbA57kCcJJ8so09",
        "startup_accelerator": "https://buy.stripe.com/bJe4gz9DH33z5cu2558so08"
    }

class BaseStream:
    def __init__(self, name: str, links: List[str]):
        self.name = name
        self.links = links

    def get_real_lead(self):
        try:
            lead_path = os.path.join("data", "customers", "leads.json")
            if os.path.exists(lead_path):
                with open(lead_path, "r", encoding="utf-8") as f:
                    leads = json.load(f)
                    if leads: return random.choice(leads)
        except: pass
        return {"email": "robert.demotto@realms2riches.com", "name": "Innovation Team"}

    def generate_task(self) -> str:
        raise NotImplementedError

class AffiliateArbitrageStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Generate a viral TikTok script for ClickFunnels using the 'tiktok_gen' tool. "
            f"Product: ClickFunnels. Link: {self.links[0]}. "
            f"Then dispatch the script text to Facebook using 'multiplexer'."
        )

class APISaaSBillingStream(BaseStream):
    def generate_task(self) -> str:
        lead = self.get_real_lead()
        return (
            f"Create a high-converting email pitch for Jarvis 3.5 API access using 'email_gen'. "
            f"Target: SaaS Developers. Link: {self.links[0]}. "
            f"Use 'smtp_outreach' to send it to '{lead['email']}'."
        )

class LeadGenBrokerStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Generate an ad copy for Pollo AI using 'ad_gen'. "
            f"Focus on automated voice agents. Link: {self.links[0]}. "
            f"Post the ad headline to Facebook using 'multiplexer'."
        )

class DigitalProductStoreStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Draft a LinkedIn post promoting the Sovereign Brand Kit using 'multiplexer'. "
            f"Highlight immediate ROI. Link: {self.links[1]}."
        )

class NewsletterSponsorshipStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Draft a sponsorship proposal for the Sovereign Newsletter using 'email_gen'. "
            f"Target: AI Tool Vendors. Link: {self.links[0]}."
        )

class PrintOnDemandStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Create a TikTok script for CapCut templates using 'tiktok_gen'. "
            f"Focus on viral editing. Link: {self.links[0]}."
        )

class ProgrammaticAdsStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Generate programmatic ad copy for VidIQ using 'ad_gen'. "
            f"Target: YouTubers. Link: {self.links[1]}."
        )

class CryptoYieldFarmingStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Analyze current yield farming rates (simulated) and post a 'Crypto Alert' to Facebook using 'multiplexer'. "
            f"Link to Accelerator: {self.links[0]}."
        )

class PaidCommunityStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Draft an exclusive invitation email for the Elite Support tier using 'email_gen'. "
            f"Link: {self.links[0]}."
        )

class DataLicensingAPIStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Draft an enterprise licensing proposal using 'email_gen'. "
            f"Target: Fortune 500 CTOs. Link: {self.links[0]}."
        )

class SEOTrafficStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Generate an SEO blog post outline for 'Autonomous Revenue Agents' using 'seo_factory'. "
            f"Link: {self.links[0]}."
        )

class ColdOutreachStream(BaseStream):
    def generate_task(self) -> str:
        lead = self.get_real_lead()
        return (
            f"Execute a cold outreach sequence for Jarvis Custom Enterprise using 'smtp_outreach'. "
            f"Target: {lead['email']} ({lead['name']}). Link: {self.links[0]}."
        )

class FastDeployMonetizationStream(BaseStream):
    def generate_task(self) -> str:
        return (
            f"Create a 'Launch in 5 Minutes' ad campaign for the Startup Accelerator using 'ad_gen'. "
            f"Link: {self.links[0]}."
        )

class MonetizationEngine:
    def __init__(self):
        self._products = []
        self._load_catalog()
        self.streams = [
            AffiliateArbitrageStream("AffiliateArbitrage", [AFFILIATE_LINKS["clickfunnels"]]),
            APISaaSBillingStream("APISaaSBilling", [STRIPE_MONETIZATION.get("jarvis_basic", "")]),
            LeadGenBrokerStream("LeadGenBroker", [AFFILIATE_LINKS["pollo_ai"]]),
            DigitalProductStoreStream("DigitalProductStore", [STRIPE_MONETIZATION.get("business_consultation", ""), STRIPE_MONETIZATION.get("brand_kit", "")]),
            NewsletterSponsorshipStream("NewsletterSponsorship", [AFFILIATE_LINKS["brand_push"]]),
            PrintOnDemandStream("PrintOnDemand", [AFFILIATE_LINKS["capcut"]]),
            ProgrammaticAdsStream("ProgrammaticAds", [AFFILIATE_LINKS["tiktok_shop"], AFFILIATE_LINKS["vidiq"]]),
            CryptoYieldFarmingStream("CryptoYieldFarming", [STRIPE_MONETIZATION.get("startup_accelerator", "")]),
            PaidCommunityStream("PaidCommunity", [STRIPE_MONETIZATION.get("elite_support", "")]),
            DataLicensingAPIStream("DataLicensingAPI", [STRIPE_MONETIZATION.get("jarvis_custom", "")]),
            SEOTrafficStream("SEOTraffic", [STRIPE_MONETIZATION.get("jarvis_basic", "")]),
            ColdOutreachStream("ColdOutreach", [STRIPE_MONETIZATION.get("jarvis_custom", "")]),
            FastDeployMonetizationStream("FastDeploy", [STRIPE_MONETIZATION.get("startup_accelerator", "")])
        ]

    def _load_catalog(self):
        try:
            with open("data/catalog/products.json", "r", encoding="utf-8") as f:
                self._products = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load catalog for recommendations: {e}")
            self._products = []

    def get_products_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        return [p for p in self._products if p.get("funnel_stage") == stage]

    def get_recommendations(self, product_id: str) -> Dict[str, List[Dict[str, Any]]]:
        current = next((p for p in self._products if p["id"] == product_id), None)
        if not current:
            return {"upsells": [], "cross_sells": []}
        
        upsells = [p for p in self._products if p["id"] in current.get("upsell_to", [])]
        cross_sells = [p for p in self._products if p["id"] in current.get("cross_sell_with", [])]
        
        return {"upsells": upsells, "cross_sells": cross_sells}

    def get_entry_offers(self) -> List[Dict[str, Any]]:
        return [p for p in self._products if p.get("primary_entry_offer")]

    async def run_all_streams(self, orchestrator) -> List[Dict[str, Any]]:
        logger.info("⚡ INITIATING 13-VECTOR MONETIZATION BLITZ ⚡")
        results = []
        
        # Dispatch ALL streams to the orchestrator for real execution
        for stream in self.streams:
            task_desc = stream.generate_task()
            logger.info(f"🚀 Dispatching Stream: {stream.name} -> {task_desc[:50]}...")
            
            try:
                final_res = None
                async for step in orchestrator.submit_task_stream(task_desc, f"stream_{stream.name}"):
                    if step["status"] == "completed":
                        final_res = step["result"]
                        logger.info(f"✅ Stream {stream.name} Executed Successfully.")
                    elif step["status"] == "failed":
                        logger.error(f"❌ Stream {stream.name} Failed: {step['reason']}")
                        final_res = {"error": step["reason"]}
                
                results.append({
                    "stream": stream.name,
                    "status": "success" if final_res and "error" not in final_res else "failed",
                    "result": final_res
                })
            except Exception as e:
                logger.error(f"Stream {stream.name} Exception: {e}")
                results.append({"stream": stream.name, "status": "error", "reason": str(e)})
                
        logger.info("🏁 MONETIZATION CYCLE COMPLETE.")
        return results

monetization_engine = MonetizationEngine()
