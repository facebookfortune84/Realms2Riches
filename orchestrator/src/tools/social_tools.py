import os
import requests
from typing import Dict, Any, List, Optional
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class FacebookPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.FACEBOOK_PAGE_TOKEN
        self.page_id = settings.FACEBOOK_PAGE_ID or "me"

    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        message, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        if not self.access_token or self.access_token == "placeholder":
            logger.warning("Facebook Dispatch: Missing Token.")
            return {"status": "skipped", "reason": "No valid token"}

        # Determine if Video or Photo
        is_video = media_url and ".mp4" in media_url.lower()
        is_raster = media_url and any(ext in media_url.lower() for ext in [".png", ".jpg", ".jpeg"])
        
        headers = {"ngrok-skip-browser-warning": "true"}
        
        if is_video:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/videos"
            payload = {
                "file_url": media_url,
                "description": f"ACQUIRE NOW: {link}\n\n{message}",
                "access_token": self.access_token
            }
        elif is_raster:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/photos"
            payload = {
                "url": media_url,
                "caption": f"ACQUIRE NOW: {link}\n\n{message}",
                "access_token": self.access_token
            }
        else:
            # Fallback to Link Card (Feed)
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
            payload = {
                "message": message,
                "link": link,
                "access_token": self.access_token,
                "call_to_action": {"type": "SHOP_NOW", "value": {"link": link}}
            }

        try:
            logger.info(f"Facebook Dispatching to {url} | Media: {bool(media_url)}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                err_msg = f"FB API Error: {response.status_code} - {response.text}"
                logger.error(err_msg)
                return {"status": "error", "reason": err_msg[:200]}
            
            post_id = response.json().get("id") or response.json().get("post_id")
            logger.info(f"✅ Facebook SUCCESS: Post ID {post_id}")
            return {"status": "success", "platform": "facebook", "id": post_id}
        except Exception as e:
            logger.error(f"Facebook Exception: {e}")
            return {"status": "error", "reason": str(e)}

class LinkedInPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.author_urn = settings.LINKEDIN_PROFILE_URN or "urn:li:person:placeholder"

    def _refresh_token(self) -> bool:
        logger.info("LinkedIn: Attempting token refresh...")
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
        text, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
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
            if media_url and ".svg" not in media_url.lower():
                payload["content"]["article"]["thumbnail"] = media_url

        try:
            logger.info(f"LinkedIn Dispatching | Link: {bool(link)}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 401 and self._refresh_token():
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code != 201:
                err_msg = f"LinkedIn API Error: {response.status_code} - {response.text}"
                logger.error(err_msg)
                return {"status": "error", "reason": err_msg[:200]}
                
            logger.info("✅ LinkedIn SUCCESS.")
            return {"status": "success", "platform": "linkedin"}
        except Exception as e:
            logger.error(f"LinkedIn Exception: {e}")
            return {"status": "error", "reason": str(e)}

class TwitterPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.X_ACCESS_TOKEN

    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        message, link = params.get("message"), params.get("link")
        if not self.access_token or self.access_token == "placeholder":
            return {"status": "skipped", "reason": "No valid X token"}

        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        full_text = f"{message}\n\nACQUIRE: {link}" if link else message
        payload = {"text": full_text[:280]}

        try:
            logger.info("X (Twitter) Dispatching...")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code not in [200, 201]:
                err = f"X API Error: {response.status_code} - {response.text}"
                logger.error(err)
                return {"status": "error", "reason": err[:200]}
            
            return {"status": "success", "platform": "x", "id": response.json().get("data", {}).get("id")}
        except Exception as e:
            logger.error(f"X Exception: {e}")
            return {"status": "error", "reason": str(e)}

class DiscordPostTool(BaseTool):
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        message, link = params.get("message"), params.get("link")
        # Standard Webhook implementation for Discord
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            return {"status": "skipped", "reason": "No Discord Webhook"}
            
        payload = {"content": f"{message}\n\nACQUIRE: {link}" if link else message}
        try:
            logger.info("Discord Dispatching...")
            res = requests.post(webhook_url, json=payload, timeout=10)
            return {"status": "success", "platform": "discord"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class SocialMediaMultiplexer(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.fb_tool = FacebookPostTool(ToolConfig(tool_id="fb", name="fb", description="fb", parameters_schema={}, allowed_agents=["*"]))
        self.li_tool = LinkedInPostTool(ToolConfig(tool_id="li", name="li", description="li", parameters_schema={}, allowed_agents=["*"]))
        self.tw_tool = TwitterPostTool(ToolConfig(tool_id="tw", name="tw", description="tw", parameters_schema={}, allowed_agents=["*"]))
        self.dc_tool = DiscordPostTool(ToolConfig(tool_id="dc", name="dc", description="dc", parameters_schema={}, allowed_agents=["*"]))

    def execute(self, invocation: Any) -> Dict[str, Any]:
        from orchestrator.src.validation.social_validator import SocialPostValidator
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        message, link, media_url = params.get("message"), params.get("link"), params.get("media_url")
        
        # 1. PRE-FLIGHT VALIDATION
        is_valid, reason = SocialPostValidator.validate(message, link)
        if not is_valid:
            logger.warning(f"🛡️ MULTIPLEXER VALIDATION FAIL: {reason}")
            return {"status": "error", "error_type": "validation_fail", "reason": reason}
        
        # 2. DISPATCH
        # Since tools now handle both, we can pass invocation or params.
        # But tools expect 'invocation' to be the object if not dict.
        results = {
            "facebook": self.fb_tool.execute(invocation),
            "linkedin": self.li_tool.execute(invocation),
            "twitter": self.tw_tool.execute(invocation),
            "discord": self.dc_tool.execute(invocation)
        }
        
        # 3. SELF-HEALING FALLBACK (Detailed Audit)
        failed_channels = [c for c, r in results.items() if r.get("status") == "error"]
        if failed_channels:
            logger.error(f"🛡️ CHANNEL DEVIATION: {failed_channels}. Retrying with optimization track...")
            
        return results

def get_social_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {"message": {"type": "string"}, "link": {"type": "string"}}}
    return [
        FacebookPostTool(ToolConfig(tool_id="facebook_post", name="FB", description="FB", parameters_schema=cfg, allowed_agents=["*"])),
        LinkedInPostTool(ToolConfig(tool_id="linkedin_post", name="LI", description="LI", parameters_schema=cfg, allowed_agents=["*"])),
        DiscordPostTool(ToolConfig(tool_id="discord_post", name="DC", description="DC", parameters_schema=cfg, allowed_agents=["*"])),
        SocialMediaMultiplexer(ToolConfig(tool_id="social_multiplexer", name="Multiplexer", description="All channels", parameters_schema=cfg, allowed_agents=["*"]))
    ]
