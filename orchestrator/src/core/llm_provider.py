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
            raise e
