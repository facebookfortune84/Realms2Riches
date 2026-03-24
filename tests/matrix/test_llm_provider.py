import sys
import os
sys.path.append(os.getcwd())

import json
import pytest
from orchestrator.src.core.llm_provider import GroqProvider, OpenAIProvider, get_llm_provider

def test_groq_mock_response():
    """Verify GroqProvider mock logic."""
    provider = GroqProvider()
    provider.is_mock = True
    
    # Test regular prompt
    messages = [{"role": "user", "content": "Hello"}]
    response = provider.generate_response(messages)
    data = json.loads(response)
    assert "reasoning" in data
    assert "integrity" in data["reasoning"]

    # Test monetization prompt
    messages = [{"role": "user", "content": "How do I buy a product with Stripe?"}]
    response = provider.generate_response(messages)
    data = json.loads(response)
    assert "stripe" in data["steps"][0]["inputs"]["link"]

def test_openai_mock_fallback():
    """Verify OpenAIProvider falls back to Groq mock logic when no key."""
    provider = OpenAIProvider()
    provider.is_mock = True
    
    messages = [{"role": "user", "content": "Stripe payment"}]
    response = provider.generate_response(messages)
    data = json.loads(response)
    assert "stripe" in data["steps"][0]["inputs"]["link"]

def test_get_llm_provider():
    """Verify factory method."""
    provider = get_llm_provider("groq")
    assert isinstance(provider, GroqProvider)
    
    provider = get_llm_provider("openai")
    assert isinstance(provider, OpenAIProvider)
