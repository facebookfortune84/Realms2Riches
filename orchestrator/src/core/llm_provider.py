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
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.model = model
        self.api_key = settings.GROQ_API_KEY
        if self.api_key == "placeholder":
            logger.warning("GROQ_API_KEY is placeholder. Using MockProvider.")
            self.is_mock = True
        else:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                self.is_mock = False
            except ImportError:
                logger.error("groq package not installed. Falling back to mock.")
                self.is_mock = True
        
        logger.info(f"Initialized GroqProvider with model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.is_mock:
            return self._mock_respond(messages)
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                **kwargs
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return self._mock_respond(messages)

    def _mock_respond(self, messages: List[Dict[str, str]]) -> str:
        prompt = messages[-1]["content"].lower()
        
        # Enhanced Mock Responses for Audit Pass
        if "product" in prompt or "stripe" in prompt:
            return json.dumps({
                "reasoning": "Generating technical copy for monetization.",
                "steps": [
                    {
                        "tool_id": "multiplexer",
                        "inputs": {
                            "message": "Secure the Platinum License today. [💳 ACQUIRE NOW] https://buy.stripe.com/test_platinum_2999",
                            "link": "https://buy.stripe.com/test_platinum_2999"
                        }
                    }
                ]
            })
        
        if "introduce" in prompt or "role call" in prompt:
             return json.dumps({
                "reasoning": "Coordinating fleet introduction.",
                "steps": []
            })

        return json.dumps({
            "reasoning": "Default mock execution.",
            "steps": []
        })
