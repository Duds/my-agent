import pytest
from unittest.mock import AsyncMock, MagicMock
from core.router import ModelRouter
from core.schema import Intent
from core.adapters_base import ModelAdapter
from core.factory import AdapterFactory

@pytest.fixture
def mock_local_client():
    client = MagicMock(spec=ModelAdapter)
    client.generate = AsyncMock(return_value="Local response")
    client.get_model_info.return_value = {"id": "local-id", "name": "Local Model"}
    return client

@pytest.fixture
def mock_factory():
    factory = MagicMock(spec=AdapterFactory)
    
    # Mock a coding model
    coding_adapter = MagicMock(spec=ModelAdapter)
    coding_adapter.generate = AsyncMock(return_value="Coding response")
    coding_adapter.get_model_info.return_value = {"id": "codellama", "name": "CodeLlama"}
    
    factory.get_local_adapter.side_effect = lambda id: coding_adapter if "code" in id else None
    factory.get_remote_adapter.return_value = None
    
    return factory

@pytest.mark.asyncio
async def test_router_coding_flow(mock_local_client, mock_factory):
    router = ModelRouter(
        local_client=mock_local_client,
        adapter_factory=mock_factory,
        available_models=["codellama:7b-instruct"]
    )
    
    # "Write a python script" should classify as CODING
    result = await router.route_request("Write a python script to parse logs.")
    
    assert result["intent"] == Intent.CODING.value
    assert "codellama" in result["adapter"]
    assert result["answer"] == "Coding response"

@pytest.mark.asyncio
async def test_router_private_flow(mock_local_client, mock_factory):
    # Setup mock for private/hermes model
    private_adapter = MagicMock(spec=ModelAdapter)
    private_adapter.generate = AsyncMock(return_value="Private response")
    private_adapter.get_model_info.return_value = {"id": "hermes", "name": "Hermes"}
    
    mock_factory.get_local_adapter.side_effect = lambda id: private_adapter if "hermes" in id else None

    router = ModelRouter(
        local_client=mock_local_client,
        adapter_factory=mock_factory,
        available_models=["hermes-roleplay:latest"]
    )
    
    # Query with private keyword
    result = await router.route_request("Keep this password secret.")
    
    assert result["intent"] == Intent.PRIVATE.value
    assert result["requires_privacy"] is True
    assert "hermes" in result["adapter"]
    assert result["answer"] == "Private response"

@pytest.mark.asyncio
async def test_router_fallback_flow(mock_local_client, mock_factory):
    mock_factory.get_local_adapter.return_value = None
    mock_factory.get_remote_adapter.return_value = None
    
    router = ModelRouter(
        local_client=mock_local_client,
        adapter_factory=mock_factory,
        available_models=[]
    )
    
    # Simple query should fall back to local_client
    result = await router.route_request("Hi")
    
    assert result["intent"] == Intent.SPEED.value
    assert "local-default" in result["adapter"]
    assert result["answer"] == "Local response"
