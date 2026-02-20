from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig

class ContentTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured content for various channels.
        Input: { "channel": "blog|linkedin|twitter", "topic": "...", "tone": "..." }
        """
        channel = input_data.get("channel", "blog")
        topic = input_data.get("topic", "AI")
        tone = input_data.get("tone", "professional")
        
        # In a real system, this would call an LLM directly or via a service.
        # For now, we simulate the high-quality generation logic.
        
        if channel == "blog":
            return self._generate_blog_post(topic, tone)
        elif channel == "linkedin":
            return self._generate_linkedin_post(topic, tone)
        else:
            return {"error": f"Unsupported channel: {channel}"}

    def _generate_blog_post(self, topic: str, tone: str) -> Dict[str, Any]:
        return {
            "title": f"The Future of {topic}: A {tone} Perspective",
            "body": f"In this rapidly evolving landscape, {topic} stands at the forefront of innovation...",
            "tags": [topic, "tech", "future"],
            "seo_score": 95
        }

    def _generate_linkedin_post(self, topic: str, tone: str) -> Dict[str, Any]:
        return {
            "text": f"🚀 Just exploring {topic}! The potential is limitless. #{topic} #Innovation",
            "hashtags": ["#Tech", "#Growth"]
        }
