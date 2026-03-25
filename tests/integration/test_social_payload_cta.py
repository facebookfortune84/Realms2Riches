import unittest
import sys
import os
from unittest.mock import patch

sys.path.append(os.getcwd())

from orchestrator.src.tools.social_tools import FacebookPostTool, LinkedInPostTool, ToolConfig

class TestSocialPayloadCTA(unittest.TestCase):

    @patch('orchestrator.src.tools.social_tools.settings')
    def test_facebook_cta_payload(self, mock_settings):
        """Verify the Facebook payload contains the SHOP_NOW call_to_action."""
        mock_settings.FACEBOOK_PAGE_ACCESS_TOKEN = "valid_token"
        mock_settings.FACEBOOK_PAGE_ID = "123"
        
        tool = FacebookPostTool(ToolConfig(tool_id="t", name="t", description="d", parameters_schema={}, allowed_agents=["*"]))
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"id": "123"}
            
            tool.execute({"message": "Buy now", "link": "https://checkout.stripe.com/test"})
            
            # Check the actual payload sent to requests.post
            args, kwargs = mock_post.call_args
            payload = kwargs.get('json')
            
            self.assertIn("call_to_action", payload)
            self.assertEqual(payload["call_to_action"]["type"], "SHOP_NOW")
            self.assertEqual(payload["call_to_action"]["value"]["link"], "https://checkout.stripe.com/test")
            print("✅ Facebook Payload: Verified SHOP_NOW button parameters.")

    def test_linkedin_cta_payload(self):
        """Verify the LinkedIn payload uses the high-conversion article titles."""
        tool = LinkedInPostTool(ToolConfig(tool_id="t", name="t", description="d", parameters_schema={}, allowed_agents=["*"]))
        tool.access_token = "valid_token"
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            
            tool.execute({"message": "Buy now", "link": "https://checkout.stripe.com/test"})
            
            args, kwargs = mock_post.call_args
            payload = kwargs.get('json')
            
            title = payload["content"]["article"]["title"]
            self.assertIn("INITIALIZE", title)
            print(f"✅ LinkedIn Payload: Verified high-conversion title '{title}'.")

if __name__ == "__main__":
    unittest.main()
