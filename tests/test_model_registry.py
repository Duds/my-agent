"""Tests for core.model_registry."""

from core.model_registry import (
    get_models_for_provider,
    get_provider_and_api_model,
    get_all_provider_model_ids,
    COMMERCIAL_MODELS,
)


def test_get_models_for_provider_anthropic():
    """get_models_for_provider returns list of model dicts for anthropic."""
    result = get_models_for_provider("anthropic")
    assert isinstance(result, list)
    assert len(result) >= 1
    for m in result:
        assert "id" in m and "name" in m and "contextWindow" in m
        assert m["id"] in COMMERCIAL_MODELS


def test_get_models_for_provider_mistral():
    """get_models_for_provider returns models for mistral."""
    result = get_models_for_provider("mistral")
    assert isinstance(result, list)
    assert any(m["id"] == "mistral-small" for m in result)


def test_get_models_for_provider_empty():
    """get_models_for_provider returns [] for unknown provider."""
    result = get_models_for_provider("unknown-provider")
    assert result == []


def test_get_provider_and_api_model_known():
    """get_provider_and_api_model returns (provider, api_id) for known model."""
    provider, api_id = get_provider_and_api_model("claude-haiku")
    assert provider == "anthropic"
    assert "claude" in (api_id or "").lower()


def test_get_provider_and_api_model_unknown():
    """get_provider_and_api_model returns (None, None) for unknown model."""
    assert get_provider_and_api_model("unknown-model") == (None, None)


def test_get_all_provider_model_ids():
    """get_all_provider_model_ids returns dict of provider -> list of model ids."""
    result = get_all_provider_model_ids()
    assert isinstance(result, dict)
    assert "anthropic" in result
    assert "mistral" in result
    assert "moonshot" in result
    assert isinstance(result["anthropic"], list)
    assert "claude-haiku" in result["anthropic"]
