from __future__ import annotations

from providers import make_provider
from providers.router9_provider import Router9Provider


def test_make_provider_supports_9router(monkeypatch) -> None:
    monkeypatch.setenv("ROUTER9_BASE_URL", "http://localhost:20128/v1")
    provider = make_provider("9router")

    assert isinstance(provider, Router9Provider)
    assert provider.base_url == "http://localhost:20128/v1"
    assert provider.api_key_env == "ROUTER9_API_KEY"

