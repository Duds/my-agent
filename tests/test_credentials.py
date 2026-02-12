"""Tests for credentials module (has_api_key, save_api_key, remove_api_key) using temp dir."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def creds_path(tmp_path):
    """Temporary credentials file path."""
    return tmp_path / "credentials.json"


@pytest.fixture
def credentials_file(creds_path):
    """Empty credentials file."""
    creds_path.write_text("{}")
    return creds_path


def test_has_api_key_false_when_empty(creds_path):
    """has_api_key returns False when no key is stored."""
    creds_path.write_text("{}")
    with patch("core.credentials.CREDENTIALS_PATH", creds_path), \
         patch("core.credentials.settings.anthropic_api_key", None), \
         patch("core.credentials.settings.mistral_api_key", None), \
         patch("core.credentials.settings.moonshot_api_key", None):
        from core.credentials import has_api_key
        assert has_api_key("anthropic") is False
        assert has_api_key("mistral") is False


def test_save_api_key_and_has_api_key(creds_path):
    """save_api_key writes to file; has_api_key returns True."""
    creds_path.parent.mkdir(parents=True, exist_ok=True)
    with patch("core.credentials.CREDENTIALS_PATH", creds_path):
        from core.credentials import save_api_key, has_api_key, get_api_key
        save_api_key("anthropic", "sk-secret-123")
        assert has_api_key("anthropic") is True
        assert get_api_key("anthropic") == "sk-secret-123"


def test_remove_api_key(creds_path):
    """remove_api_key removes provider entry from file."""
    creds_path.write_text('{"anthropic": {"api_key": "sk-old"}}')
    with patch("core.credentials.CREDENTIALS_PATH", creds_path), \
         patch("core.credentials.settings.anthropic_api_key", None), \
         patch("core.credentials.settings.mistral_api_key", None), \
         patch("core.credentials.settings.moonshot_api_key", None):
        from core.credentials import remove_api_key, has_api_key
        remove_api_key("anthropic")
        assert has_api_key("anthropic") is False
        data = json.loads(creds_path.read_text())
        assert "anthropic" not in data


def test_save_api_key_unknown_provider_raises(creds_path):
    """save_api_key raises ValueError for unknown provider."""
    creds_path.write_text("{}")
    with patch("core.credentials.CREDENTIALS_PATH", creds_path):
        from core.credentials import save_api_key
        with pytest.raises(ValueError, match="Unknown provider"):
            save_api_key("unknown-provider", "key")
