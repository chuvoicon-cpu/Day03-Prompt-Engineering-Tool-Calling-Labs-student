from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class Router9Provider(OpenAIProvider):
    """9router's local OpenAI-compatible Chat Completions endpoint."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="ROUTER9_API_KEY",
            base_url=os.getenv("ROUTER9_BASE_URL", "http://localhost:20128/v1"),
            default_model="ag/gemini-3.8-flash-high",
        )
