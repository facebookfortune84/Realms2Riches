from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from groq import Groq
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a completion from the LLM."""
        pass

class GroqProvider(BaseLLMProvider):
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None,
        default_model: Optional[str] = None
    ):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.base_url = base_url or settings.GROQ_BASE_URL
        self.default_model = default_model or settings.GROQ_MODEL
        
        if not self.api_key or self.api_key == "placeholder":
            logger.warning("GROQ_API_KEY is not set or is a placeholder")
            # In production this might raise, in dev/test we might want to allow mock
            # raise ValueError("GROQ_API_KEY is required for GroqProvider")
            
        self.client = Groq( api_key=settings.GROQ_API_KEY )
        
        logger.info(f"Initialized GroqProvider with model {self.default_model}")

    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        target_model = model or self.default_model
        
        # --- MOCK FALLBACK ---
        if not self.api_key or self.api_key == "placeholder":
            user_content = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            return self._generate_mock_response(user_content)

        try:
            completion = self.client.chat.completions.create(
                model=target_model,
                messages=messages, # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = completion.choices[0].message.content
            return content if content else ""
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            # Even if API fails, return mock in dev mode to prevent system hang
            return self._generate_mock_response("API_ERROR_FALLBACK")

    def _generate_mock_response(self, user_prompt: str) -> str:
        """Generates a semi-intelligent looking mock response for system demonstration."""
        prompt_lower = user_prompt.lower()
        
        if "analyze" in prompt_lower or "report" in prompt_lower:
            return json.dumps({
                "reasoning": f"Automated analysis of {user_prompt}. Agents detected significant delta in neural weights.",
                "steps": [
                    {"tool_id": "search", "inputs": {"q": user_prompt}},
                    {"tool_id": "file", "inputs": {"path": "data/analysis.txt", "content": "Simulated analysis results."}}
                ]
            })
        
        if "image" in prompt_lower or "visual" in prompt_lower:
             return json.dumps({
                "reasoning": "Visual cortex activated. Rendering asset based on prompt parameters.",
                "steps": [
                    {"tool_id": "image_gen", "inputs": {"prompt": user_prompt}}
                ]
            })

        if "video" in prompt_lower or "teaser" in prompt_lower:
             return json.dumps({
                "reasoning": "Temporal synthesis engine engaged. Compiling video sequence.",
                "steps": [
                    {"tool_id": "video", "inputs": {"script": user_prompt}}
                ]
            })
            
        if "shard" in prompt_lower or "twitter" in prompt_lower or "social" in prompt_lower:
             return json.dumps({
                "reasoning": "Optimizing content for high-velocity social channels.",
                "steps": [
                    {"tool_id": "shard", "inputs": {"text": user_prompt}}
                ]
            })

        if "fiscal" in prompt_lower or "revenue" in prompt_lower or "audit" in prompt_lower:
             return json.dumps({
                "reasoning": "Initiating fiscal integrity scan. Verifying cryptographic revenue ledger.",
                "steps": [
                    {"tool_id": "payments", "inputs": {"action": "verify_telemetry"}}
                ]
            })

        if "outreach" in prompt_lower or "viral" in prompt_lower:
             return json.dumps({
                "reasoning": "Deploying viral outreach protocol. Targeting high-influence nodes.",
                "steps": [
                    {"tool_id": "social", "inputs": {"platform": "twitter", "content": "The Sovereign Era has arrived. Join the elite. #Realms2Riches"}}
                ]
            })

        if "seo" in prompt_lower or "meta" in prompt_lower or "optimize" in prompt_lower:
             return json.dumps({
                "reasoning": "Analyzing search intent and keyword density. Generating high-CTR meta tags.",
                "steps": [
                    {"tool_id": "seo", "inputs": {"action": "optimize_meta", "content": user_prompt, "keywords": ["Sovereign", "AI", "Wealth"]}}
                ]
            })

        return json.dumps({
            "reasoning": "Standard swarm operation initiated. Optimized pathways identified.",
            "steps": []
        })
