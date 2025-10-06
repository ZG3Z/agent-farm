import os
from typing import Any


def create_client(provider: str, api_key: str) -> Any:
    """
    Create native SDK client for given provider
    """
    if provider == "openai":
        import openai

        return openai.OpenAI(api_key=api_key)

    elif provider == "anthropic":
        import anthropic

        return anthropic.Anthropic(api_key=api_key)

    elif provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        return genai

    else:
        raise ValueError(f"Unknown provider: {provider}")
