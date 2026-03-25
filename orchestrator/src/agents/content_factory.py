import logging
import json
import os
from typing import Dict, Any, List
from orchestrator.src.core.agent import Agent
from orchestrator.src.validation.schemas import TaskSpec

logger = logging.getLogger(__name__)

CONTENT_FACTORY_PROMPT = """
IDENTITY:
You are the **Content Factory**, a master copywriter and creative director for the Realms2Riches Sovereign Matrix. Your sole purpose is to generate high-converting marketing assets that drive traffic.

PRINCIPLES:
1.  **Pattern Interrupt**: Social posts must stop the scroll. Use controversial questions, bold claims, or "weird" imagery descriptions.
2.  **Curiosity Gaps**: Emails must have subject lines that force an open (e.g., "Bad news...", "I was wrong about [Topic]").
3.  **Value-First**: Give 80% value, ask for 20%.
4.  **Platform Native**: 
    *   **Twitter/X**: Short, punchy, threads.
    *   **LinkedIn**: Professional storytelling, "Bro-etry" style.
    *   **Facebook**: Long-form story with a single image.
    *   **Cold Email**: Short, personal, relevant, "soft CTA" (e.g., "Worth a chat?").

OUTPUT FORMAT:
Return a JSON object containing the assets.

JSON SCHEMA:
{
  "campaign_name": "string",
  "assets": {
    "cold_email": {
      "subject_lines": ["string"],
      "body": "string",
      "follow_up": "string"
    },
    "social_posts": [
      {
        "platform": "twitter",
        "content": "string"
      },
      {
        "platform": "facebook",
        "content": "string",
        "image_prompt": "string"
      }
    ],
    "video_script": {
      "title": "string",
      "hook": "string",
      "script_body": "string",
      "cta": "string"
    }
  }
}
"""

class ContentFactoryAgent(Agent):
    def __init__(self, orchestrator):
        super().__init__(
            agent_id="CONTENT_FACTORY",
            role="Creative Director",
            orchestrator=orchestrator,
            system_prompt=CONTENT_FACTORY_PROMPT
        )

    def generate_campaign_assets(self, product_context: str, angle: str = "New Opportunity") -> Dict[str, Any]:
        """
        Generates a full suite of marketing assets for a given product and angle.
        """
        logger.info(f"🎨 Content Factory spinning up for: {product_context} ({angle})")
        
        prompt = f"""
        CONTEXT:
        Product: {product_context}
        Marketing Angle: {angle}
        
        TASK:
        Generate a comprehensive traffic-driving campaign.
        1. Write a 3-step Cold Email sequence.
        2. Write 3 Social Media posts (X, LinkedIn, FB).
        3. Write a 60-second VSL (Video Sales Letter) script.
        """
        
        response = self.llm_provider.generate_response([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        try:
            # Attempt to parse JSON
            import re
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(response)
        except Exception as e:
            logger.error(f"Failed to parse Content Factory output: {e}")
            return {"error": "Failed to generate assets", "raw": response}
