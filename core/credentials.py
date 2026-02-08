"""
Credentials store for API keys. Supports .env and data/credentials.json.
Keys in credentials.json override env. Never log or return keys to clients.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

from .config import settings

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = Path(__file__).parent.parent / "data" / "credentials.json"

_PROVIDER_ENV_MAP = {
    "anthropic": "ANTHROPIC_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
}


def _load_credentials_file() -> dict[str, Any]:
    """Load credentials from file. Returns empty dict if missing or invalid."""
    if not CREDENTIALS_PATH.exists():
        return {}
    try:
        with open(CREDENTIALS_PATH) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("Could not load credentials file: %s", e)
        return {}


def _save_credentials_file(data: dict[str, Any]) -> None:
    """Save credentials to file."""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CREDENTIALS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_api_key(provider: str) -> str | None:
    """Get API key for provider. Checks credentials file first, then env."""
    provider = provider.lower()
    creds = _load_credentials_file()
    if provider in creds and isinstance(creds[provider], dict):
        key = creds[provider].get("api_key")
        if key and isinstance(key, str):
            return key
    if provider in creds and isinstance(creds[provider], str):
        return creds[provider]
    # Fallback to settings (env)
    if provider == "anthropic":
        return settings.anthropic_api_key
    if provider == "mistral":
        return settings.mistral_api_key
    if provider == "moonshot":
        return settings.moonshot_api_key
    return None


def save_api_key(provider: str, api_key: str) -> None:
    """Save API key for provider to credentials file."""
    provider = provider.lower()
    if provider not in _PROVIDER_ENV_MAP:
        raise ValueError(f"Unknown provider: {provider}")
    creds = _load_credentials_file()
    if provider not in creds or not isinstance(creds[provider], dict):
        creds[provider] = {}
    creds[provider]["api_key"] = api_key
    _save_credentials_file(creds)
    logger.info("Saved API key for provider %s", provider)


def remove_api_key(provider: str) -> None:
    """Remove API key for provider from credentials file."""
    provider = provider.lower()
    creds = _load_credentials_file()
    if provider in creds:
        del creds[provider]
        _save_credentials_file(creds)
        logger.info("Removed API key for provider %s", provider)


def has_api_key(provider: str) -> bool:
    """Return True if provider has a configured API key."""
    key = get_api_key(provider)
    return bool(key and key.strip() and "your_" not in key.lower() and "here" not in key.lower())
