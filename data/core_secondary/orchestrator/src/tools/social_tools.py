import os
import requests
import logging
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.core.config import settings

logger = logging.getLogger(__name__)

class FacebookPostTool(BaseTool):
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        message = params.get("message")
        link = params.get("link")
        
        token = settings.FACEBOOK_PAGE_ACCESS_TOKEN
        page_id = settings.FACEBOOK_PAGE_ID
        
        if not token or token == "placeholder":
            return {"status": "skipped", "reason": "No FB token"}

        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        payload = {"message": message, "access_token": token}
        if link: 
            payload["link"] = link
            # Platinum CTA Implementation
            payload["call_to_action"] = {
                "type": "SHOP_NOW",
                "value": {"link": link}
            }
        
        try:
            logger.info("Facebook Dispatching...")
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                return {"status": "success", "platform": "facebook", "id": res.json().get("id")}
            return {"status": "error", "reason": res.text}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class LinkedInPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.author_urn = settings.LINKEDIN_PROFILE_URN

    def _refresh_token(self):
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": settings.LINKEDIN_REFRESH_TOKEN,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET
        }
        try:
            res = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15)
            if res.status_code == 200:
                new_tok = res.json().get("access_token")
                settings.LINKEDIN_ACCESS_TOKEN = new_tok
                self.access_token = new_tok
                logger.info("✅ LinkedIn: Token Refreshed.")
                return True
            return False
        except Exception as e:
            logger.error(f"LinkedIn Refresh Fail: {e}")
            return False

    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        text, link = params.get("message"), params.get("link")
        token = self.access_token
        if not token or token == "placeholder": return {"status": "skipped"}
        if token.startswith("Bearer "): token = token.replace("Bearer ", "")

        url = "https://api.linkedin.com/rest/posts"
        headers = {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json", 
            "X-Restli-Protocol-Version": "2.0.0", 
            "LinkedIn-Version": "202401"
        }
        
        payload = {
            "author": self.author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": { "feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": [] },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        if link:
            payload["content"] = {
                "article": {
                    "source": link, 
                    "title": "🚀 INITIALIZE YOUR SOVEREIGN Swarm", 
                    "description": "Scale to 1000 agents immediately."
                }
            }

        try:
            logger.info("LinkedIn Dispatching...")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 401 and self._refresh_token():
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code != 201:
                return {"status": "error", "reason": response.text}
            return {"status": "success", "platform": "linkedin"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class TwitterPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.X_ACCESS_TOKEN

    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        message, link = params.get("message"), params.get("link")
        if not self.access_token or self.access_token == "placeholder":
            return {"status": "skipped"}

        url = "https://api.twitter.com/2/tweets"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        full_text = f"{message}\n\nACQUIRE: {link}" if link else message
        payload = {"text": full_text[:280]}

        try:
            logger.info("X (Twitter) Dispatching...")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                return {"status": "success", "platform": "x", "id": response.json().get("data", {}).get("id")}
            return {"status": "error", "reason": response.text}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class DiscordPostTool(BaseTool):
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        message, link = params.get("message"), params.get("link")
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url: return {"status": "skipped"}

        payload = {"content": f"{message}\n\nACQUIRE: {link}" if link else message}
        try:
            requests.post(webhook_url, json=payload, timeout=10)
            return {"status": "success", "platform": "discord"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class SocialMediaMultiplexer(BaseTool):
    """
    Industrial Viral Multiplexer.
    Ensures high-quality insights and zero 'garbage' posts.
    """
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.fb_tool = FacebookPostTool(ToolConfig(tool_id="fb_int", name="FB", description="D", parameters_schema={}, allowed_agents=["*"]))
        self.li_tool = LinkedInPostTool(ToolConfig(tool_id="li_int", name="LI", description="D", parameters_schema={}, allowed_agents=["*"]))
        self.tw_tool = TwitterPostTool(ToolConfig(tool_id="tw_int", name="X", description="D", parameters_schema={}, allowed_agents=["*"]))
        self.dc_tool = DiscordPostTool(ToolConfig(tool_id="dc_int", name="DC", description="D", parameters_schema={}, allowed_agents=["*"]))

    def execute(self, invocation: Any) -> Dict[str, Any]:
        from orchestrator.src.validation.social_validator import SocialPostValidator
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        insight = params.get("insight") or params.get("message")
        link = params.get("link", "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02")
        
        if not insight or len(insight) < 30:
            return {"status": "error", "reason": "Insight quality threshold not met (min 30 chars)."}

        is_valid, reason = SocialPostValidator.validate(insight, link)
        if not is_valid: return {"status": "error", "reason": reason}

        results = {
            "facebook": self.fb_tool.execute({"message": f"💎 SOVEREIGN INTELLIGENCE: {insight}\n\n👉 SECURE NODE: {link}"}),
            "linkedin": self.li_tool.execute({"message": f"Industrial Growth Report: {insight}\n\n#AI #SovereignMatrix\n\nLink: {link}"}),
            "twitter": self.tw_tool.execute({"message": f"🔥 {insight[:200]}... ACQUIRE: {link}"}),
            "discord": self.dc_tool.execute({"message": f"📢 **MATRIX ALERT**: {insight}\n\n{link}"})
        }
        return {"status": "success", "platforms": results}

class WordPressPostTool(BaseTool):
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        title = params.get("title", "The Future of Autonomous Revenue")
        content = params.get("content", "Synthetic agents are scaling the globe.")
        if not settings.WORDPRESS_SITE_URL: return {"status": "skipped"}

        from requests.auth import HTTPBasicAuth
        url = f"{settings.WORDPRESS_SITE_URL.rstrip('/')}/wp-json/wp/v2/posts"
        auth = HTTPBasicAuth(settings.WORDPRESS_USERNAME, settings.WORDPRESS_APPLICATION_PASSWORD)
        data = {"title": title, "content": content, "status": "publish"}
        
        try:
            res = requests.post(url, auth=auth, json=data, timeout=15)
            if res.status_code in [200, 201]:
                return {"status": "success", "post_url": res.json().get("link")}
            return {"status": "error", "reason": res.text}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class OmniChannelDistributor(BaseTool):
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        msg = params.get("message", "The Sovereign Matrix is online.")
        link = params.get("link", settings.MARKETING_SITE_URL)
        
        li = LinkedInPostTool(ToolConfig(tool_id="li_dist", name="LI", description="D", parameters_schema={}, allowed_agents=["*"]))
        fb = FacebookPostTool(ToolConfig(tool_id="fb_dist", name="FB", description="D", parameters_schema={}, allowed_agents=["*"]))
        wp = WordPressPostTool(ToolConfig(tool_id="wp_dist", name="WP", description="D", parameters_schema={}, allowed_agents=["*"]))
        
        return {
            "status": "success", 
            "channel_results": {
                "linkedin": li.execute({"message": msg, "link": link}),
                "facebook": fb.execute({"message": msg, "link": link}),
                "wordpress": wp.execute({"title": "Sovereign Bulletin", "content": f"{msg}<br><br><a href='{link}'>Read More</a>"})
            }
        }

def get_social_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {"message": {"type": "string"}, "link": {"type": "string"}}}
    return [
        FacebookPostTool(ToolConfig(tool_id="facebook_post", name="FB", description="FB", parameters_schema=cfg, allowed_agents=["*"])),
        LinkedInPostTool(ToolConfig(tool_id="linkedin_post", name="LI", description="LI", parameters_schema=cfg, allowed_agents=["*"])),
        DiscordPostTool(ToolConfig(tool_id="discord_post", name="DC", description="DC", parameters_schema=cfg, allowed_agents=["*"])),
        TwitterPostTool(ToolConfig(tool_id="twitter_post", name="X", description="X", parameters_schema=cfg, allowed_agents=["*"])),
        WordPressPostTool(ToolConfig(tool_id="wordpress_post", name="WP", description="WP", parameters_schema=cfg, allowed_agents=["*"])),
        SocialMediaMultiplexer(ToolConfig(tool_id="social_multiplexer", name="Multiplexer", description="All channels", parameters_schema=cfg, allowed_agents=["*"])),
        OmniChannelDistributor(ToolConfig(tool_id="omni_distributor", name="Omni Distributor", description="Omni Channel Post", parameters_schema=cfg, allowed_agents=["*"]))
    ]
