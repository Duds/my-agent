"""
Model discovery from commercial API providers.
Validates API keys and fetches available models.
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def discover_anthropic(api_key: str) -> list[dict[str, str]]:
    """Discover models from Anthropic API. Returns {id, name, contextWindow}."""
    models: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            for m in data.get("data", []):
                mid = m.get("id") or ""
                name = m.get("display_name") or mid
                models.append({"id": mid, "name": name, "contextWindow": "200k"})
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key")
        raise
    except Exception as e:
        logger.exception("Anthropic discovery failed: %s", e)
        raise
    return models


async def discover_mistral(api_key: str) -> list[dict[str, str]]:
    """Discover models from Mistral API. Returns {id, name, contextWindow}."""
    models: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.mistral.ai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
            for m in data.get("data", []):
                mid = m.get("id") or ""
                name = m.get("object", m.get("id", mid))
                if isinstance(name, dict):
                    name = mid
                models.append({"id": mid, "name": str(name), "contextWindow": "128k"})
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key")
        raise
    except Exception as e:
        logger.exception("Mistral discovery failed: %s", e)
        raise
    return models


async def discover_moonshot(api_key: str) -> list[dict[str, str]]:
    """Discover models from Moonshot API (OpenAI-compatible)."""
    models: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.moonshot.ai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
            for m in data.get("data", []):
                mid = m.get("id") or ""
                name = m.get("id", mid)
                models.append({"id": mid, "name": str(name), "contextWindow": "128k"})
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key")
        raise
    except Exception as e:
        logger.exception("Moonshot discovery failed: %s", e)
        raise
    return models


async def discover_openai(api_key: str) -> list[dict[str, str]]:
    """Discover models from OpenAI API. Returns {id, name, contextWindow}."""
    models: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
            # Only include common chat/text models to avoid clutter
            for m in data.get("data", []):
                mid = m.get("id") or ""
                if any(x in mid for x in ["gpt-4", "gpt-3.5"]):
                    models.append({"id": mid, "name": mid, "contextWindow": "128k"})
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key")
        raise
    except Exception as e:
        logger.exception("OpenAI discovery failed: %s", e)
        raise
    return models


async def discover_google(api_key: str) -> list[dict[str, str]]:
    """Discover models from Google Gemini API."""
    models: list[dict[str, str]] = []
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # list_models is synchronous in the current version of the SDK
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                mid = m.name.replace("models/", "")
                models.append({"id": mid, "name": m.display_name, "contextWindow": "1M"})
    except Exception as e:
        if "API_KEY_INVALID" in str(e) or "401" in str(e):
            raise ValueError("Invalid API key")
        logger.exception("Google discovery failed: %s", e)
        raise
    return models


async def discover_models(provider: str, api_key: str) -> list[dict[str, str]]:
    """Discover models for a provider. Validates key and returns model list."""
    provider = provider.lower()
    if provider == "anthropic":
        return await discover_anthropic(api_key)
    if provider == "mistral":
        return await discover_mistral(api_key)
    if provider == "moonshot":
        return await discover_moonshot(api_key)
    if provider == "openai":
        return await discover_openai(api_key)
    if provider == "google":
        return await discover_google(api_key)
    raise ValueError(f"Unknown provider: {provider}")
