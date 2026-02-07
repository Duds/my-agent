"""Pytest configuration and shared fixtures."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.adapters_base import ModelAdapter
from core.factory import AdapterFactory
from core.router import ModelRouter
from core.security import SecurityValidator


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_adapter() -> ModelAdapter:
    """Create a mock adapter for testing."""
    adapter = MagicMock(spec=ModelAdapter)
    adapter.generate = AsyncMock(return_value="Mock response")
    adapter.get_model_info.return_value = {"model": "mock", "type": "test"}
    return adapter


@pytest.fixture
def mock_security_validator() -> SecurityValidator:
    """Create a mock security validator."""
    validator = MagicMock(spec=SecurityValidator)
    validator.check_output = AsyncMock(return_value={"is_safe": True, "reason": "OK"})
    return validator


@pytest.fixture
def mock_factory(mock_adapter: ModelAdapter) -> AdapterFactory:
    """Create a mock AdapterFactory."""
    factory = MagicMock(spec=AdapterFactory)
    factory.get_local_adapter.return_value = mock_adapter
    factory.get_remote_adapter.return_value = None
    return factory


@pytest.fixture
def router(mock_adapter: ModelAdapter, mock_factory: AdapterFactory, mock_security_validator: SecurityValidator) -> ModelRouter:
    """Create a ModelRouter with mock dependencies."""
    return ModelRouter(
        local_client=mock_adapter,
        adapter_factory=mock_factory,
        security_validator=mock_security_validator,
        available_models=["llama3:latest", "mistral:latest"],
    )
