import pytest
from core.factory import AdapterFactory
from core.adapters_local import OllamaAdapter
from core.adapters_remote import AnthropicAdapter
from core.config import settings

def test_factory_pools_local_adapters():
    factory = AdapterFactory()
    adapter1 = factory.get_local_adapter("llama3")
    adapter2 = factory.get_local_adapter("llama3")
    adapter3 = factory.get_local_adapter("mistral")

    assert adapter1 is adapter2
    assert adapter1 is not adapter3
    assert isinstance(adapter1, OllamaAdapter)
    assert adapter1.model_name == "llama3"

def test_factory_manages_remote_adapters(monkeypatch):
    # Mock settings to ensure remote adapters are "configured"
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    
    factory = AdapterFactory()
    factory.initialize_remotes()
    
    remote = factory.get_remote_adapter("anthropic")
    assert remote is not None
    assert isinstance(remote, AnthropicAdapter)
    
    # Get all remotes
    all_remotes = factory.get_all_remote_adapters()
    assert "anthropic" in all_remotes
    assert all_remotes["anthropic"] is remote

def test_factory_clear():
    factory = AdapterFactory()
    factory.get_local_adapter("llama3")
    assert "llama3" in factory._local_pool
    
    factory.clear()
    assert len(factory._local_pool) == 0
    assert not factory._initialized
