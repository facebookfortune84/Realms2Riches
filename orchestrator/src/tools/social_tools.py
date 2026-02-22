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
        
        if not self.access_token or self.access_token == "placeholder":
            return {"status": "skipped", "reason": "No valid FACEBOOK_PAGE_TOKEN"}

        url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        if link:
            payload["link"] = link
            
        try:
            # In a test environment without internet, we might want to mock this.
            # However, the user said keys are real, so we attempt the post if possible.
            # Given I am an AI, I cannot make outbound requests to FB API from this shell usually.
            # But I will write the code as if it works.
            # CHECK: If running in a restricted shell, this might fail or hang.
            # I will add a safe-guard for the 'test' environment or if request fails.
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return {"status": "success", "platform": "facebook", "id": response.json().get("id")}
        except Exception as e:
            logger.error(f"Facebook Post Error: {e}")
            return {"status": "error", "reason": str(e)}

class LinkedInPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.author_urn = settings.LINKEDIN_PROFILE_URN or "urn:li:person:placeholder"

    def _refresh_token(self) -> bool:
        """Attempts to refresh the LinkedIn access token using the refresh token."""
        logger.info("LinkedIn: Attempting to refresh access token...")
        
        if not all([settings.LINKEDIN_REFRESH_TOKEN, settings.LINKEDIN_CLIENT_ID, settings.LINKEDIN_CLIENT_SECRET]):
            logger.error("LinkedIn Refresh Error: Missing OAuth credentials (refresh_token, client_id, or client_secret).")
            return False

        url = "https://www.linkedin.com/oauth/v2/accessToken"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": settings.LINKEDIN_REFRESH_TOKEN,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                new_token = data.get("access_token")
                if new_token:
                    # Update in-memory settings
                    settings.LINKEDIN_ACCESS_TOKEN = new_token
                    self.access_token = new_token
                    logger.info("✅ LinkedIn: Access token refreshed successfully.")
                    
                    # Proactively update .env.prod if possible to persist across restarts
                    self._persist_token(new_token)
                    return True
            logger.error(f"LinkedIn Refresh Failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"LinkedIn Refresh Exception: {e}")
            return False

    def _persist_token(self, token: str):
        """Helper to write the new token back to .env.prod for persistence."""
        try:
            env_path = ".env.prod"
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    lines = f.readlines()
                with open(env_path, "w") as f:
                    for line in lines:
                        if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                            f.write(f"LINKEDIN_ACCESS_TOKEN={token}\n")
                        else:
                            f.write(line)
                logger.info("✅ LinkedIn: Token persisted to .env.prod")
        except Exception as e:
            logger.warning(f"LinkedIn: Could not persist token to file: {e}")

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text = params.get("message")
        article_url = params.get("link")
        media_url = params.get("media_url")
        
        if not self.access_token or self.access_token == "placeholder":
            return {"status": "skipped", "reason": "No valid LINKEDIN_ACCESS_TOKEN"}

        # Use the modern /posts API (Standard LinkedIn API)
        url = "https://api.linkedin.com/rest/posts"
        
        # Ensure the token doesn't have double 'Bearer'
        token = self.access_token
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202501" 
        }
        
        payload = {
            "author": self.author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        if media_url:
            # Note: For REST v2, posting a direct image URL requires a multi-step upload.
            # We'll use the 'article' format with the image URL as an illustration 
            # to ensure the post succeeds while still being visual.
            payload["content"] = {
                "article": {
                    "source": article_url or "https://realms2riches.ai",
                    "thumbnail": media_url,
                    "title": "Sovereign Intelligence Pulse",
                    "description": "Visualizing the future of agentic swarms."
                }
            }
        elif article_url:
            payload["content"] = {
                "article": {
                    "source": article_url,
                    "title": "Latest Intelligence Report",
                    "description": "Autonomous insight from the Sovereign Swarm."
                }
            }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # AUTOMATIC REFRESH LOGIC
            if response.status_code == 401 and "EXPIRED_ACCESS_TOKEN" in response.text:
                if self._refresh_token():
                    # Retry once with the new token
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code != 201:
                logger.error(f"LinkedIn API Error: {response.status_code} - {response.text}")
                return {"status": "error", "reason": f"{response.status_code}: {response.text[:100]}"}
                
            return {"status": "success", "platform": "linkedin", "id": response.headers.get("x-linkedin-id")}
        except Exception as e:
            logger.error(f"LinkedIn Connection Error: {e}")
            return {"status": "error", "reason": str(e)}

class LinkedInTokenRefreshTool(BaseTool):
    """Explicit tool for agents to trigger a token refresh."""
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.poster = LinkedInPostTool(ToolConfig(tool_id="li_temp", name="LI Temp", description="Temp", parameters_schema={}, allowed_agents=["*"]))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        success = self.poster._refresh_token()
        return {"status": "success" if success else "error", "new_token_active": success}

class TwitterPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.bearer_token = settings.TWITTER_BEARER_TOKEN

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text = params.get("message")
        if not self.bearer_token or self.bearer_token == "placeholder":
            return {"status": "skipped", "reason": "No valid TWITTER_BEARER_TOKEN"}

        url = "https://api.twitter.com/2/tweets"
        headers = {"Authorization": f"Bearer {self.bearer_token}", "Content-Type": "application/json"}
        payload = {"text": text[:280]} # Twitter limit

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return {"status": "success", "platform": "twitter", "id": response.json().get("data", {}).get("id")}
        except Exception as e:
            logger.error(f"Twitter Post Error: {e}")
            return {"status": "error", "reason": str(e)}

class DiscordPostTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        content = params.get("message")
        link = params.get("link")
        
        if not self.webhook_url or self.webhook_url == "placeholder":
            return {"status": "skipped", "reason": "No valid DISCORD_WEBHOOK_URL"}

        if link: content += f"\n\n👉 {link}"
        
        try:
            response = requests.post(self.webhook_url, json={"content": content}, timeout=10)
            response.raise_for_status()
            return {"status": "success", "platform": "discord"}
        except Exception as e:
            logger.error(f"Discord Post Error: {e}")
            return {"status": "error", "reason": str(e)}

class SocialMediaMultiplexer(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.fb_tool = FacebookPostTool(ToolConfig(tool_id="fb_post", name="FB Poster", description="Posts to FB", parameters_schema={}, allowed_agents=["*"]))
        self.li_tool = LinkedInPostTool(ToolConfig(tool_id="li_post", name="LI Poster", description="Posts to LI", parameters_schema={}, allowed_agents=["*"]))
        self.tw_tool = TwitterPostTool(ToolConfig(tool_id="tw_post", name="X Poster", description="Posts to X", parameters_schema={}, allowed_agents=["*"]))
        self.dc_tool = DiscordPostTool(ToolConfig(tool_id="dc_post", name="Discord Poster", description="Posts to Discord", parameters_schema={}, allowed_agents=["*"]))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distributes content to all configured social channels.
        """
        message = params.get("message")
        link = params.get("link")
        media_url = params.get("media_url")
        
        results = {}
        
        # Post to Facebook
        results["facebook"] = self.fb_tool.execute({"message": message, "link": link, "media_url": media_url})
        
        # Post to LinkedIn
        results["linkedin"] = self.li_tool.execute({"message": message, "link": link, "media_url": media_url})
        
        # Post to Twitter
        results["twitter"] = self.tw_tool.execute({"message": message})
        
        # Post to Discord
        results["discord"] = self.dc_tool.execute({"message": message, "link": link})
        
        return results

# Helper to register these tools
def get_social_tools() -> List[BaseTool]:
    base_config = {"type": "object", "properties": {"message": {"type": "string"}, "link": {"type": "string"}}}
    return [
        FacebookPostTool(ToolConfig(tool_id="facebook_post", name="Facebook Poster", description="Post to Facebook", parameters_schema=base_config, allowed_agents=["Global_Market_Force_1"])),
        LinkedInPostTool(ToolConfig(tool_id="linkedin_post", name="LinkedIn Poster", description="Post to LinkedIn", parameters_schema=base_config, allowed_agents=["Global_Market_Force_1"])),
        TwitterPostTool(ToolConfig(tool_id="twitter_post", name="Twitter Poster", description="Post to X", parameters_schema=base_config, allowed_agents=["Global_Market_Force_1"])),
        DiscordPostTool(ToolConfig(tool_id="discord_post", name="Discord Poster", description="Post to Discord", parameters_schema=base_config, allowed_agents=["Global_Market_Force_1"])),
        SocialMediaMultiplexer(ToolConfig(tool_id="social_multiplexer", name="Social Multiplexer", description="Post to all channels", parameters_schema=base_config, allowed_agents=["Global_Market_Force_1"]))
    ]
