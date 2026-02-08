"""Tests for routing config load, apply, and 'auto' handling."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from core.router import ModelRouter
from core.adapters_base import ModelAdapter
from core.factory import AdapterFactory
from core import config as config_module


class MockAdapter:
    """Minimal mock adapter."""

    def __init__(self, name: str = "mock"):
        self.name = name

    async def generate(self, prompt: str, context=None):
        return "mock"

    def get_model_info(self):
        return {"model": self.name}


@pytest.fixture
def temp_routing_config():
    """Create a temporary routing config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "routing_rules.json"
        yield path


@pytest.fixture
def mock_factory():
    """Factory that returns mock adapters for known models."""
    factory = MagicMock(spec=AdapterFactory)
    factory.get_remote_adapter.return_value = None

    def get_local(model_id: str):
        if model_id:
            m = MockAdapter(model_id)
            m.generate = AsyncMock(return_value="ok")
            return m
        return None

    factory.get_local_adapter.side_effect = get_local
    return factory


@pytest.mark.asyncio
async def test_routing_config_auto_clears_overrides(temp_routing_config, mock_factory):
    """When config has 'auto', classifier/security/pii use defaults (no override)."""
    temp_routing_config.write_text(
        json.dumps({
            "intent_classification": "auto",
            "security_judge": "auto",
            "pii_redactor": "auto",
        })
    )

    with patch.object(config_module.settings, "routing_config_path", str(temp_routing_config)):
        router = ModelRouter(
            local_client=MockAdapter(),
            adapter_factory=mock_factory,
            security_validator=MagicMock(),
            available_models=["llama3:latest"],
        )

        # With "auto", intent classifier should use local (no LLM override)
        assert router.intent_classifier.classification_adapter is None
        # PII redactor should be cleared
        assert router.pii_redactor is None


@pytest.mark.asyncio
async def test_routing_config_valid_model_sets_pii_redactor(temp_routing_config, mock_factory):
    """When config has valid model for pii_redactor, PIIRedactor is configured."""
    temp_routing_config.write_text(
        json.dumps({"pii_redactor": "llama3:latest"})
    )

    with patch.object(config_module.settings, "routing_config_path", str(temp_routing_config)):
        router = ModelRouter(
            local_client=MockAdapter(),
            adapter_factory=mock_factory,
            security_validator=None,
            available_models=["llama3:latest"],
        )

        assert router.pii_redactor is not None
        assert router.pii_redactor.redactor_adapter is not None


@pytest.mark.asyncio
async def test_update_config_persists_and_reloads(temp_routing_config, mock_factory):
    """update_config writes to file and reapplies."""
    temp_routing_config.write_text("{}")

    with patch.object(config_module.settings, "routing_config_path", str(temp_routing_config)):
        router = ModelRouter(
            local_client=MockAdapter(),
            adapter_factory=mock_factory,
            security_validator=None,
            available_models=["llama3:latest"],
        )

        router.update_config({"intent_classification": "llama3:latest"})

        assert json.loads(temp_routing_config.read_text()) == {
            "intent_classification": "llama3:latest",
        }
