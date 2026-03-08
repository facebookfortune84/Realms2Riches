from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.core.llm_provider import llm_provider

class ContentTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured content for various channels using LLM.
        Input: { "channel": "blog|linkedin|twitter", "topic": "...", "tone": "..." }
        """
        channel = input_data.get("channel", "blog")
        topic = input_data.get("topic", "AI")
        tone = input_data.get("tone", "professional")
        
        if channel == "blog":
            return self._generate_blog_post(topic, tone)
        elif channel == "linkedin":
            return self._generate_linkedin_post(topic, tone)
        else:
            return {"error": f"Unsupported channel: {channel}"}

    def _generate_blog_post(self, topic: str, tone: str) -> Dict[str, Any]:
        prompt = (
            f"Write a comprehensive, SEO-optimized blog post about '{topic}'. "
            f"Tone: {tone}. Include a catchy title, introduction, 3 main sections with headers, "
            "and a conclusion. Format as Markdown."
        )
        try:
            content = llm_provider.generate_text(prompt)
            return {
                "title": f"The Future of {topic}", # Ideally extracted from content
                "body": content,
                "tags": [topic, "tech", "future"],
                "seo_score": 95
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_linkedin_post(self, topic: str, tone: str) -> Dict[str, Any]:
        prompt = (
            f"Write a viral LinkedIn post about '{topic}'. "
            f"Tone: {tone}. Use emojis, short paragraphs, and relevant hashtags."
        )
        try:
            content = llm_provider.generate_text(prompt)
            return {
                "text": content,
                "hashtags": ["#Tech", "#Growth"]
            }
        except Exception as e:
            return {"error": str(e)}
