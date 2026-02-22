import unittest
from unittest.mock import MagicMock, patch
import os
import json
from orchestrator.src.tools.social_tools import FacebookPostTool, LinkedInPostTool, SocialMediaMultiplexer
from orchestrator.src.tools.marketing_check import check_marketing_readiness
from orchestrator.src.core.alchemy_engine import generate_autonomous_blog_post

class TestSocialMonetization(unittest.TestCase):
    
    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.tool_id = "test_tool"

    @patch('orchestrator.src.tools.social_tools.settings')
    @patch('requests.post')
    def test_facebook_post(self, mock_post, mock_settings):
        # Setup
        mock_settings.FACEBOOK_ACCESS_TOKEN = "test_token"
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "12345_67890"}
        
        tool = FacebookPostTool(self.mock_config)
        result = tool.execute({"message": "Hello World", "link": "https://example.com"})
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["platform"], "facebook")
        
    @patch('orchestrator.src.tools.social_tools.settings')
    @patch('requests.post')
    def test_linkedin_post(self, mock_post, mock_settings):
        # Setup
        mock_settings.LINKEDIN_ACCESS_TOKEN = "test_token"
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "urn:li:share:123"}
        
        tool = LinkedInPostTool(self.mock_config)
        result = tool.execute({"message": "Hello LinkedIn", "link": "https://example.com"})
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["platform"], "linkedin")

    @patch('orchestrator.src.tools.social_tools.settings')
    @patch('requests.post')
    def test_multiplexer(self, mock_post, mock_settings):
        # Setup
        mock_settings.FACEBOOK_ACCESS_TOKEN = "test_token"
        mock_settings.LINKEDIN_ACCESS_TOKEN = "test_token"
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "123"}
        
        tool = SocialMediaMultiplexer(self.mock_config)
        results = tool.execute({"message": "Multi-post", "link": "https://example.com"})
        
        self.assertIn("facebook", results)
        self.assertIn("linkedin", results)
        self.assertEqual(results["facebook"]["status"], "success")
        self.assertEqual(results["linkedin"]["status"], "success")

    @patch('orchestrator.src.tools.marketing_check.settings')
    def test_marketing_readiness_pass(self, mock_settings):
        # Setup valid config
        mock_config = MagicMock()
        mock_config.brand_name = "Realms 2 Riches"
        mock_config.website_url = "https://realms2riches.ai"
        mock_config.twitter_handle = "realms2riches"
        mock_settings.marketing_config = mock_config
        
        # Test
        result = check_marketing_readiness()
        self.assertTrue(result)

    def test_blog_links_injection(self):
        # Generate a blog post
        slug = generate_autonomous_blog_post({"agent_id": "TEST_AGENT", "reasoning": "Test reasoning"})
        
        # Read the file
        with open(f"data/blog/{slug}.md", "r") as f:
            content = f.read()
            
        # Verify links exist
        self.assertIn("Direct Acquisition Channels", content)
        self.assertIn("Sovereign Platinum", content) # From product list
        self.assertIn("checkout_url", content) # Should contain the link
        self.assertIn("price_1Pqrs", content) # Or at least the ID if constructed, but we put full URL in products.json

if __name__ == '__main__':
    unittest.main()
