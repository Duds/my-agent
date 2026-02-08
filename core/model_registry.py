"""
Commercial model registry: maps UI model IDs to provider and API model IDs.
Used by /api/models, router, and adapters for multi-model support per provider.
"""

from typing import Dict, List, Tuple

# (provider, api_model_id, display_name, context_window)
COMMERCIAL_MODELS: Dict[str, Tuple[str, str, str, str]] = {
    # Anthropic Claude
    "claude-haiku": ("anthropic", "claude-3-5-haiku-20241022", "Claude 3.5 Haiku", "200k"),
    "claude-sonnet": ("anthropic", "claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet", "200k"),
    "claude-opus": ("anthropic", "claude-3-opus-20240229", "Claude 3 Opus", "200k"),
    "claude-sonnet-4": ("anthropic", "claude-sonnet-4-5-20250514", "Claude Sonnet 4.5", "200k"),
    "claude-haiku-4": ("anthropic", "claude-haiku-4-5-20251015", "Claude Haiku 4.5", "200k"),
    "claude-opus-4": ("anthropic", "claude-opus-4-6", "Claude Opus 4.6", "1M"),
    # Mistral
    "mistral-small": ("mistral", "mistral-small-latest", "Mistral Small", "128k"),
    "mistral-small-3": ("mistral", "mistral-small-2506", "Mistral Small 3.2", "128k"),
    "mistral-medium": ("mistral", "mistral-medium-3-1-25-08", "Mistral Medium 3.1", "128k"),
    "mistral-large": ("mistral", "mistral-large-2512", "Mistral Large 3", "128k"),
    "mistral-large-2": ("mistral", "mistral-large-2411", "Mistral Large 2.1", "128k"),
    "devstral-2": ("mistral", "devstral-2-25-12", "Devstral 2 (Code)", "128k"),
    "codestral": ("mistral", "codestral-2508", "Codestral (Code)", "256k"),
    "magistral-medium": ("mistral", "magistral-medium-1-2-25-09", "Magistral Medium 1.2", "128k"),
    # Moonshot / Kimi
    "moonshot-v1-8k": ("moonshot", "moonshot-v1-8k", "Moonshot V1 8k", "8k"),
    "moonshot-v1-32k": ("moonshot", "moonshot-v1-32k", "Moonshot V1 32k", "32k"),
    "moonshot-v1-128k": ("moonshot", "moonshot-v1-128k", "Moonshot V1 128k", "128k"),
    "moonshot-v1": ("moonshot", "moonshot-v1-8k", "Moonshot V1", "8k"),
    "kimi-k2-turbo": ("moonshot", "kimi-k2-turbo-preview", "Kimi K2 Turbo", "128k"),
    "kimi-k2-0905": ("moonshot", "kimi-k2-0905-preview", "Kimi K2 0905", "262k"),
    "kimi-k2-0711": ("moonshot", "kimi-k2-0711-preview", "Kimi K2 0711", "128k"),
    "kimi-k2-thinking": ("moonshot", "kimi-k2-thinking", "Kimi K2 Thinking", "262k"),
    "kimi-k2.5": ("moonshot", "kimi-k2.5", "Kimi K2.5 Multimodal", "262k"),
}


def get_models_for_provider(provider: str) -> List[dict]:
    """Return list of model dicts for a provider (id, name, contextWindow)."""
    result = []
    for model_id, (p, api_id, name, ctx) in COMMERCIAL_MODELS.items():
        if p == provider:
            result.append({
                "id": model_id,
                "name": name,
                "api_model_id": api_id,
                "contextWindow": ctx,
            })
    return result


def get_provider_and_api_model(model_id: str) -> Tuple[str | None, str | None]:
    """Return (provider, api_model_id) for a model_id, or (None, None)."""
    if model_id in COMMERCIAL_MODELS:
        p, api_id, _, _ = COMMERCIAL_MODELS[model_id]
        return p, api_id
    return None, None


def get_all_provider_model_ids() -> Dict[str, List[str]]:
    """Return {provider: [model_ids]} for providers that have models."""
    by_provider: Dict[str, List[str]] = {}
    for model_id, (p, _, _, _) in COMMERCIAL_MODELS.items():
        if p not in by_provider:
            by_provider[p] = []
        by_provider[p].append(model_id)
    return by_provider
