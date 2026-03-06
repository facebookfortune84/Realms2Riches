import os
import json
import logging
import requests
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SocialMediaMultiplexer(BaseTool):
    """
    Industrial Social Media Broadcast Tool.
    Fully implemented Graph/REST API calls for FB, LinkedIn, and X.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data or {}
        platform = str(params.get("platform", "facebook")).lower()
        content = params.get("content", "Sovereign Intelligence Unit Active.")
        
        # Core CTAs
        conversion_link = "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02"
        full_post = f"{content}\n\n👉 SECURE YOUR SOVEREIGN LICENSE: {conversion_link}"

        logger.info(f"Broadcast Sequence: Initiating {platform} dispatch...")

        if platform == "facebook":
            return self._dispatch_facebook(full_post)
        elif platform == "linkedin":
            return self._dispatch_linkedin(full_post)
        elif platform == "twitter" or platform == "x":
            return self._dispatch_x(full_post)
        
        return {"status": "error", "reason": f"Platform '{platform}' not yet supported in Vanguard state."}

    def _dispatch_facebook(self, message: str) -> Dict[str, Any]:
        token = os.getenv("FACEBOOK_PAGE_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        if not token or not page_id:
            return {"status": "error", "reason": "Facebook credentials missing in .env.prod"}
        
        url = f"https://graph.facebook.com/{page_id}/feed"
        try:
            res = requests.post(url, data={"message": message, "access_token": token}, timeout=10)
            if res.status_code == 200:
                return {"status": "success", "platform": "facebook", "post_id": res.json().get("id")}
            return {"status": "error", "platform": "facebook", "reason": res.text}
        except Exception as e:
            return {"status": "error", "platform": "facebook", "reason": str(e)}

    def _dispatch_linkedin(self, message: str) -> Dict[str, Any]:
        token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        person_id = os.getenv("LINKEDIN_PERSON_ID") # e.g. 'urn:li:person:XXXX'
        if not token or not person_id:
            return {"status": "error", "reason": "LinkedIn credentials missing."}

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        payload = {
            "author": person_id,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": message},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 201:
                return {"status": "success", "platform": "linkedin", "post_id": res.json().get("id")}
            return {"status": "error", "platform": "linkedin", "reason": res.text}
        except Exception as e:
            return {"status": "error", "platform": "linkedin", "reason": str(e)}

    def _dispatch_x(self, message: str) -> Dict[str, Any]:
        # Uses X API v2 (Requires OAuth 1.0a User Context or OAuth 2.0 Bearer)
        # Note: Usually requires 'tweepy' for easier handling, but we'll use direct REST
        token = os.getenv("X_ACCESS_TOKEN")
        if not token:
            return {"status": "error", "reason": "X/Twitter token missing."}
        
        url = "https://api.twitter.com/2/tweets"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        try:
            res = requests.post(url, json={"text": message}, headers=headers, timeout=10)
            if res.status_code == 201:
                return {"status": "success", "platform": "x", "post_id": res.json().get("data", {}).get("id")}
            return {"status": "error", "platform": "x", "reason": res.text}
        except Exception as e:
            return {"status": "error", "platform": "x", "reason": str(e)}

def get_social_tools() -> List[BaseTool]:
    cfg = {
        "type": "object", 
        "properties": {
            "platform": {"type": "string", "enum": ["facebook", "linkedin", "x", "twitter"]}, 
            "content": {"type": "string"}
        },
        "required": ["platform", "content"]
    }
    return [
        SocialMediaMultiplexer(ToolConfig(
            tool_id="multiplexer", 
            name="Broadcast", 
            description="High-authority omni-channel dispatch", 
            parameters_schema=cfg, 
            allowed_agents=["*"]
        ))
    ]
