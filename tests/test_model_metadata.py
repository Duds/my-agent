"""Tests for core.model_metadata."""

import pytest
from pathlib import Path
from unittest.mock import patch

from core.model_metadata import (
    get_metadata_for_model,
    merge_metadata_into_model,
    _load_metadata,
)


def test_get_metadata_for_model_commercial():
    """Commercial model_id with entry in metadata returns tags, pros, cons, benefits."""
    result = get_metadata_for_model("claude-haiku", "commercial")
    assert isinstance(result, dict)
    assert "tags" in result
    assert "pros" in result
    assert "cons" in result
    assert "benefits" in result
    assert "fast" in result.get("tags", []) or "cost-effective" in result.get("tags", [])


def test_get_metadata_for_model_commercial_unknown_returns_empty():
    """Unknown commercial model_id returns empty dict."""
    result = get_metadata_for_model("unknown-model-id", "commercial")
    assert result == {}


def test_get_metadata_for_model_ollama_pattern():
    """Ollama model matching a pattern returns metadata."""
    result = get_metadata_for_model("mistral:7b-instruct", "ollama")
    assert isinstance(result, dict)
    assert "tags" in result
    assert result.get("tags") or result.get("benefits")


def test_get_metadata_for_model_ollama_no_match_returns_empty():
    """Ollama model matching no pattern returns empty dict."""
    result = get_metadata_for_model("obscure:latest", "ollama")
    assert result == {}


def test_merge_metadata_into_model_with_metadata():
    """merge_metadata_into_model adds tags, pros, cons, benefits when metadata exists."""
    model = {"id": "claude-haiku", "name": "Claude Haiku"}
    out = merge_metadata_into_model(model, "claude-haiku", "commercial")
    assert out is model
    assert "tags" in model
    assert "pros" in model
    assert "cons" in model
    assert "benefits" in model


def test_merge_metadata_into_model_no_metadata():
    """merge_metadata_into_model sets empty lists/string when no metadata."""
    model = {"id": "unknown", "name": "Unknown"}
    out = merge_metadata_into_model(model, "unknown", "commercial")
    assert out is model
    assert model["tags"] == []
    assert model["pros"] == []
    assert model["cons"] == []
    assert model["benefits"] == ""


def test_load_metadata_when_file_missing():
    """When metadata file does not exist, _load_metadata returns empty models and patterns."""
    import core.model_metadata as mod
    orig_path = mod._METADATA_PATH
    mod._CACHE = None
    try:
        with patch.object(mod, "_METADATA_PATH", Path("/nonexistent/model_metadata.json")):
            result = _load_metadata()
        assert result["models"] == {}
        assert result["ollama_patterns"] == []
    finally:
        mod._CACHE = None
        mod._METADATA_PATH = orig_path
