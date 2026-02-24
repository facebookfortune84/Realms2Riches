import os
import requests
from typing import Dict, Any, List, Optional
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class FacebookPostTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data
        message, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        token = settings.FACEBOOK_PAGE_TOKEN
        page_id = settings.FACEBOOK_PAGE_ID or "me"
        
        if not token or token == "placeholder": return {"status": "skipped"}
        
        headers = {"ngrok-skip-browser-warning": "true"}
        if media_url and ".mp4" in media_url.lower():
            url = f"https://graph.facebook.com/v19.0/{page_id}/videos"
            payload = {"file_url": media_url, "description": f"ACQUIRE NOW: {link}\n\n{message}", "access_token": token}
        elif media_url:
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            payload = {"url": media_url, "caption": f"ACQUIRE NOW: {link}\n\n{message}", "access_token": token}
        else:
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            payload = {"message": message, "link": link, "access_token": token}

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=60)
            if res.status_code != 200: return {"status": "error", "reason": f"FB {res.status_code}"}
            return {"status": "success", "platform": "facebook", "id": res.json().get("id")}
        except Exception as e: return {"status": "error", "reason": str(e)}

class LinkedInPostTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data
        text, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        token = settings.LINKEDIN_ACCESS_TOKEN
        author = settings.LINKEDIN_PROFILE_URN or "urn:li:person:placeholder"
        
        if not token or token == "placeholder": return {"status": "skipped"}
        
        url = "https://api.linkedin.com/rest/posts"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0", "LinkedIn-Version": "202404"}
        payload = {"author": author, "commentary": text, "visibility": "PUBLIC", "distribution": { "feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": [] }, "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}
        if link:
            payload["content"] = {"article": {"source": link, "title": "🚀 SECURE YOUR SOVEREIGN LICENSE"}}
            if media_url: payload["content"]["article"]["thumbnail"] = media_url
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code != 201: return {"status": "error", "reason": f"LI {res.status_code}"}
            return {"status": "success", "platform": "linkedin"}
        except Exception as e: return {"status": "error", "reason": str(e)}

class SocialMediaMultiplexer(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.fb_tool = FacebookPostTool(ToolConfig(tool_id="fb", name="fb", description="fb", parameters_schema={}, allowed_agents=["*"]))
        self.li_tool = LinkedInPostTool(ToolConfig(tool_id="li", name="li", description="li", parameters_schema={}, allowed_agents=["*"]))

    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        from orchestrator.src.validation.social_validator import SocialPostValidator
        params = invocation.input_data
        msg, link, media = params.get("message"), params.get("link"), params.get("media_url")
        
        is_valid, reason = SocialPostValidator.validate(msg, link, media)
        if not is_valid: return {"status": "error", "error_type": "validation_fail", "reason": reason}
        
        # Prioritize Facebook Dispatch First
        fb_result = self.fb_tool.execute(ToolInvocation(tool_id="fb", agent_id="sys", input_data=params))
        return {
            "facebook": fb_result,
            "linkedin": {"status": "skipped", "reason": "Facebook prioritization active - LinkedIn paused"}
        }
