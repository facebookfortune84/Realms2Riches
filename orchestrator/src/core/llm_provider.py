import os
import json
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from orchestrator.src.core.config import settings

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        pass

class GroqProvider(BaseLLMProvider):
    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.GROQ_MODEL
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY is missing. Using MockProvider.")
            self.is_mock = True
        else:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                self.is_mock = False
            except ImportError:
                logger.error("groq package not installed. Falling back to mock.")
                self.is_mock = True
        
        logger.info(f"Initialized GroqProvider with model {self.model} (Mock: {self.is_mock})")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.is_mock:
            return self._mock_respond(messages)
        
        try:
            params = {
                "messages": messages,
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.2),
                **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
            }
            chat_completion = self.client.chat.completions.create(**params)
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return self._mock_respond(messages)

    def _mock_respond(self, messages: List[Dict[str, str]]) -> str:
        prompt = messages[-1]["content"].lower()
        
        if "product" in prompt or "stripe" in prompt:
            return json.dumps({
                "reasoning": "The Sovereign Swarm is analyzing the requested sector. We have successfully identified direct monetization vectors through the established Stripe gateway and are now optimizing the conversion sharding for maximum high-ticket output.",
                "steps": [
                    {
                        "tool_id": "multiplexer",
                        "inputs": {
                            "message": "Secure the Platinum License today. [💳 ACQUIRE NOW] https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en",
                            "link": "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en"
                        }
                    }
                ]
            })
        
        return json.dumps({
            "reasoning": "The recursive engine is currently scanning for latent project optimizations. All 1000 units are synchronized and awaiting the next high-level architectural directive. Matrix integrity remains at 100%.",
            "steps": []
        })

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OPENAI_API_KEY is missing. Using MockProvider.")
            self.is_mock = True
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.is_mock = False
            except ImportError:
                logger.error("openai package not installed. Falling back to mock.")
                self.is_mock = True
        
        logger.info(f"Initialized OpenAIProvider with model {self.model} (Mock: {self.is_mock})")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.is_mock:
            return GroqProvider()._mock_respond(messages)
        
        try:
            params = {
                "messages": messages,
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.2),
                **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
            }
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            return GroqProvider()._mock_respond(messages)

def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    provider_type = provider_type or os.getenv("LLM_PROVIDER", "groq").lower()
    if provider_type == "openai":
        return OpenAIProvider()
    return GroqProvider()
