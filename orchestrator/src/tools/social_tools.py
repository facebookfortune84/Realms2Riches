import os
import requests
from typing import Dict, Any, List, Optional
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class FacebookPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.FACEBOOK_PAGE_TOKEN
        self.page_id = settings.FACEBOOK_PAGE_ID or "me"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        message = params.get("message")
        link = params.get("link")
        media_url = params.get("media_url")
        
        if not self.access_token or self.access_token == "placeholder":
            return {"status": "skipped", "reason": "No valid FACEBOOK_PAGE_TOKEN"}

        # THE BUTTON FIX: We use /feed + link to generate a Clickable Preview Card.
        # This is the most reliable way to get a 'Buy Button' experience organically.
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
        
        payload = {
            "message": message,
            "link": link,
            "access_token": self.access_token
        }
        
        # We include picture as a hint for the card, but don't force it to avoid ownership errors.
        if media_url:
            payload["picture"] = media_url
            
        try:
            # We add the ngrok skip header in case we are pinging our own backend
            headers = {"ngrok-skip-browser-warning": "true"}
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"Facebook API Error Details: {response.status_code} - {response.text}")
                return {"status": "error", "reason": f"{response.status_code}: {response.text[:150]}"}
                
            return {"status": "success", "platform": "facebook", "id": response.json().get("id")}
        except Exception as e:
            logger.error(f"Facebook Connection Error: {e}")
            return {"status": "error", "reason": str(e)}
                
            return {"status": "success", "platform": "facebook", "id": response.json().get("id")}
        except Exception as e:
            logger.error(f"Facebook Connection Error: {e}")
            return {"status": "error", "reason": str(e)}

class LinkedInPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.author_urn = settings.LINKEDIN_PROFILE_URN or "urn:li:person:placeholder"

    def _refresh_token(self) -> bool:
        logger.info("LinkedIn: Attempting to refresh access token...")
        if not all([settings.LINKEDIN_REFRESH_TOKEN, settings.LINKEDIN_CLIENT_ID, settings.LINKEDIN_CLIENT_SECRET]):
            return False
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": settings.LINKEDIN_REFRESH_TOKEN,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET
        }
        try:
            response = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15)
            if response.status_code == 200:
                new_token = response.json().get("access_token")
                settings.LINKEDIN_ACCESS_TOKEN = new_token
                self.access_token = new_token
                return True
            return False
        except: return False

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text = params.get("message")
        link = params.get("link")
        media_url = params.get("media_url")
        if not self.access_token or self.access_token == "placeholder": return {"status": "skipped"}

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
        
        if media_url:
            payload["content"] = {"article": {"source": link or "https://frontend-two-xi-gal9lkptfi.vercel.app/", "thumbnail": media_url, "title": "🚀 SECURE YOUR SOVEREIGN LICENSE", "description": "Initialize your 1000-agent swarm today. Direct access to the Platinum Matrix."}}
        elif link:
            payload["content"] = {"article": {"source": link, "title": "⚡ INITIALIZE DEPLOYMENT", "description": "Click to acquire your Sovereign Assets and activate the swarm."}}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 401 and self._refresh_token():
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code != 201:
                logger.error(f"LinkedIn API Error Details: {response.status_code} - {response.text}")
                return {"status": "error", "reason": f"{response.status_code}: {response.text[:150]}"}
                
            return {"status": "success", "platform": "linkedin"}
        except Exception as e: return {"status": "error", "reason": str(e)}

class TwitterPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.bearer_token or self.bearer_token == "placeholder": return {"status": "skipped"}
        try:
            response = requests.post("https://api.twitter.com/2/tweets", json={"text": params.get("message")[:280]}, headers={"Authorization": f"Bearer {self.bearer_token}"}, timeout=10)
            return {"status": "success", "platform": "twitter"}
        except: return {"status": "error"}

class DiscordPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.webhook_url or self.webhook_url == "placeholder": return {"status": "skipped"}
        try:
            requests.post(self.webhook_url, json={"content": f"{params.get('message')}\n\n{params.get('link')}"}, timeout=10)
            return {"status": "success", "platform": "discord"}
        except: return {"status": "error"}

class SocialMediaMultiplexer(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.fb_tool = FacebookPostTool(ToolConfig(tool_id="fb", name="fb", description="fb", parameters_schema={}, allowed_agents=["*"]))
        self.li_tool = LinkedInPostTool(ToolConfig(tool_id="li", name="li", description="li", parameters_schema={}, allowed_agents=["*"]))
        self.tw_tool = TwitterPostTool(ToolConfig(tool_id="tw", name="tw", description="tw", parameters_schema={}, allowed_agents=["*"]))
        self.dc_tool = DiscordPostTool(ToolConfig(tool_id="dc", name="dc", description="dc", parameters_schema={}, allowed_agents=["*"]))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from orchestrator.src.validation.social_validator import SocialPostValidator
        message, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        
        is_valid, reason = SocialPostValidator.validate(message, link)
        if not is_valid:
            return {"status": "error", "error_type": "validation_fail", "reason": reason}
        
        return {
            "facebook": self.fb_tool.execute({"message": message, "link": link, "media_url": media_url}),
            "linkedin": self.li_tool.execute({"message": message, "link": link, "media_url": media_url}),
            "twitter": self.tw_tool.execute({"message": message}),
            "discord": self.dc_tool.execute({"message": message, "link": link})
        }

def get_social_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {"message": {"type": "string"}, "link": {"type": "string"}}}
    return [
        FacebookPostTool(ToolConfig(tool_id="facebook_post", name="FB", description="FB", parameters_schema=cfg, allowed_agents=["*"])),
        LinkedInPostTool(ToolConfig(tool_id="linkedin_post", name="LI", description="LI", parameters_schema=cfg, allowed_agents=["*"])),
        SocialMediaMultiplexer(ToolConfig(tool_id="social_multiplexer", name="Multiplexer", description="All channels", parameters_schema=cfg, allowed_agents=["*"]))
    ]
