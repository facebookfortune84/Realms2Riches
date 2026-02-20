import requests
from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SocialTool(BaseTool):
    def __init__(self, config: ToolConfig, linkedin_token: str = None, twitter_token: str = None):
        super().__init__(config)
        self.linkedin_token = linkedin_token
        self.twitter_token = twitter_token

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        platform = input_data.get("platform", "").lower()
        content = input_data.get("content", "")
        
        if platform == "linkedin":
            return self._post_linkedin(content)
        elif platform == "twitter":
            return self._post_twitter(content)
        else:
            return {"error": "Invalid platform. Use 'linkedin' or 'twitter'."}

    def _post_linkedin(self, content: str):
        if not self.linkedin_token or self.linkedin_token == "placeholder":
            return {"status": "skipped", "reason": "No LinkedIn Token configured."}
            
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.linkedin_token}",
            "Content-Type": "application/json"
        }
        # Simplified payload (requires URN lookup in real production)
        payload = {
            "author": "urn:li:person:UNKNOWN", 
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        try:
            resp = requests.post(url, json=payload, headers=headers)
            if resp.status_code == 201:
                return {"status": "success", "platform": "linkedin", "id": resp.json().get("id")}
            return {"status": "failed", "error": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _post_twitter(self, content: str):
        if not self.twitter_token or self.twitter_token == "placeholder":
            return {"status": "skipped", "reason": "No Twitter Token configured."}
            
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {self.twitter_token}",
            "Content-Type": "application/json"
        }
        try:
            resp = requests.post(url, json={"text": content}, headers=headers)
            if resp.status_code == 201:
                return {"status": "success", "platform": "twitter", "id": resp.json().get("data", {}).get("id")}
            return {"status": "failed", "error": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
