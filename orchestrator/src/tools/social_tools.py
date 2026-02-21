import requests
from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SocialTool(BaseTool):
    def __init__(self, config: ToolConfig, linkedin_token: str = None, twitter_token: str = None, facebook_token: str = None):
        super().__init__(config)
        self.linkedin_token = linkedin_token
        self.twitter_token = twitter_token
        self.facebook_token = facebook_token

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        platform = input_data.get("platform", "").lower()
        content = input_data.get("content", "")
        media_url = input_data.get("media_url", None)
        
        if platform == "linkedin":
            return self._post_linkedin(content, media_url)
        elif platform == "twitter":
            return self._post_twitter(content, media_url)
        elif platform == "facebook":
            return self._post_facebook(content, media_url)
        else:
            return {"error": "Invalid platform. Use 'linkedin', 'twitter', or 'facebook'."}

    def _post_linkedin(self, content: str, media_url: str = None):
        if not self.linkedin_token or self.linkedin_token == "placeholder":
            return {"status": "skipped", "reason": "No LinkedIn Token configured."}
            
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.linkedin_token}",
            "Content-Type": "application/json"
        }
        
        # Enhanced Payload (supports media URL via reference if extended)
        # For simplicity, we append media link to text if present
        full_content = f"{content}\n\nMedia: {media_url}" if media_url else content
        
        payload = {
            "author": "urn:li:person:UNKNOWN", 
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": full_content},
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

    def _post_twitter(self, content: str, media_url: str = None):
        if not self.twitter_token or self.twitter_token == "placeholder":
            return {"status": "skipped", "reason": "No Twitter Token configured."}
            
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {self.twitter_token}",
            "Content-Type": "application/json"
        }
        full_content = f"{content} {media_url}" if media_url else content
        try:
            resp = requests.post(url, json={"text": full_content}, headers=headers)
            if resp.status_code == 201:
                return {"status": "success", "platform": "twitter", "id": resp.json().get("data", {}).get("id")}
            return {"status": "failed", "error": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _post_facebook(self, content: str, media_url: str = None):
        if not self.facebook_token or self.facebook_token == "placeholder":
            return {"status": "skipped", "reason": "No Facebook Token configured."}
            
        # Simplified Graph API post
        # Requires 'pages_manage_posts' permission and Page ID targeting in real scenarios
        # We'll assume the token is a Page Access Token for default page
        url = "https://graph.facebook.com/v19.0/me/feed"
        params = {
            "access_token": self.facebook_token,
            "message": content
        }
        if media_url:
            params["link"] = media_url
            
        try:
            resp = requests.post(url, params=params)
            if resp.status_code == 200:
                 return {"status": "success", "platform": "facebook", "id": resp.json().get("id")}
            return {"status": "failed", "error": resp.text}
        except Exception as e:
             return {"status": "error", "message": str(e)}
