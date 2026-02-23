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
        message, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        if not self.access_token or self.access_token == "placeholder": return {"status": "skipped"}

        # 1. Determine Media Type
        is_video = media_url and ".mp4" in media_url.lower()
        is_raster = media_url and (".png" in media_url.lower() or ".jpg" in media_url.lower() or ".jpeg" in media_url.lower())
        
        # 2. Select Endpoint
        if is_video:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/videos"
            payload = {"file_url": media_url, "description": f"ACQUIRE NOW: {link}\n\n{message}", "access_token": self.access_token}
        elif is_raster:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/photos"
            payload = {"url": media_url, "caption": f"ACQUIRE NOW: {link}\n\n{message}", "access_token": self.access_token}
        else:
            # Fallback to Link Card if no supported media
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
            payload = {"message": message, "link": link, "access_token": self.access_token}

        try:
            headers = {"ngrok-skip-browser-warning": "true"}
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                logger.error(f"Facebook API Error: {response.status_code} - {response.text}")
                return {"status": "error", "reason": f"{response.status_code}: {response.text[:100]}"}
            return {"status": "success", "platform": "facebook", "id": response.json().get("id") or response.json().get("post_id")}
        except Exception as e: return {"status": "error", "reason": str(e)}

class LinkedInPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.author_urn = settings.LINKEDIN_PROFILE_URN or "urn:li:person:placeholder"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        if not self.access_token or self.access_token == "placeholder": return {"status": "skipped"}
        url = "https://api.linkedin.com/rest/posts"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0", "LinkedIn-Version": "202401"}
        
        payload = {
            "author": self.author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": { "feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": [] },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        if link:
            payload["content"] = {"article": {"source": link, "title": "🚀 SECURE YOUR SOVEREIGN LICENSE"}}
            if media_url and ".svg" not in media_url.lower():
                payload["content"]["article"]["thumbnail"] = media_url

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code != 201: return {"status": "error", "reason": response.text[:100]}
            return {"status": "success", "platform": "linkedin"}
        except: return {"status": "error"}

class SocialMediaMultiplexer(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.fb_tool = FacebookPostTool(ToolConfig(tool_id="fb", name="fb", description="fb", parameters_schema={}, allowed_agents=["*"]))
        self.li_tool = LinkedInPostTool(ToolConfig(tool_id="li", name="li", description="li", parameters_schema={}, allowed_agents=["*"]))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from orchestrator.src.validation.social_validator import SocialPostValidator
        message, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        is_valid, reason = SocialPostValidator.validate(message, link)
        if not is_valid: return {"status": "error", "error_type": "validation_fail", "reason": reason}
        return {
            "facebook": self.fb_tool.execute({"message": message, "link": link, "media_url": media_url}),
            "linkedin": self.li_tool.execute({"message": message, "link": link, "media_url": media_url})
        }

def get_social_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {"message": {"type": "string"}, "link": {"type": "string"}}}
    return [
        FacebookPostTool(ToolConfig(tool_id="facebook_post", name="FB", description="FB", parameters_schema=cfg, allowed_agents=["*"])),
        LinkedInPostTool(ToolConfig(tool_id="linkedin_post", name="LI", description="LI", parameters_schema=cfg, allowed_agents=["*"])),
        SocialMediaMultiplexer(ToolConfig(tool_id="social_multiplexer", name="Multiplexer", description="All channels", parameters_schema=cfg, allowed_agents=["*"]))
    ]
