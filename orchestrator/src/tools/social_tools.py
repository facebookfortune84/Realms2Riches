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
        if not self.access_token or self.access_token == "placeholder":
            return {"status": "skipped", "reason": "No valid token"}

        is_video = media_url and ".mp4" in media_url.lower()
        is_raster = media_url and any(ext in media_url.lower() for ext in [".png", ".jpg", ".jpeg"])
        
        headers = {"ngrok-skip-browser-warning": "true"}
        
        if is_video:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/videos"
            payload = {"file_url": media_url, "description": f"ACQUIRE NOW: {link}\n\n{message}", "access_token": self.access_token}
        elif is_raster:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/photos"
            payload = {"url": media_url, "caption": f"ACQUIRE NOW: {link}\n\n{message}", "access_token": self.access_token}
        else:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
            payload = {"message": message, "link": link, "access_token": self.access_token}

        try:
            # INCREASED TIMEOUT to 60s for Meta media processing
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code != 200:
                return {"status": "error", "reason": f"FB API Error: {response.status_code}"}
            return {"status": "success", "platform": "facebook", "id": response.json().get("id")}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class LinkedInPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.author_urn = settings.LINKEDIN_PROFILE_URN or "urn:li:person:placeholder"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        token = self.access_token
        if not token or token == "placeholder": return {"status": "skipped"}
        
        url = "https://api.linkedin.com/rest/posts"
        # FIXED VERSION TO 202402
        headers = {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json", 
            "X-Restli-Protocol-Version": "2.0.0", 
            "LinkedIn-Version": "202402"
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
            payload["content"] = {"article": {"source": link, "title": "🚀 SECURE YOUR SOVEREIGN LICENSE"}}
            if media_url and ".svg" not in media_url.lower():
                payload["content"]["article"]["thumbnail"] = media_url

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            if response.status_code != 201: return {"status": "error", "reason": f"LI Error: {response.status_code}"}
            return {"status": "success", "platform": "linkedin"}
        except Exception as e: return {"status": "error", "reason": str(e)}

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
