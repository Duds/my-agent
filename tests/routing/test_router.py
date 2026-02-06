"""Tests for ModelRouter."""

import pytest

from core.router import Intent, ModelRouter


class MockAdapter:
    """Minimal mock adapter for testing."""

    def __init__(self, name: str = "mock"):
        self.name = name

    async def generate(self, prompt: str, context=None):
        return f"Mock response for: {prompt[:50]}"

    def get_model_info(self):
        return {"model": self.name, "type": "mock"}


@pytest.mark.asyncio
async def test_classify_intent_private():
    """Private keywords route to PRIVATE intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        remote_clients={},
        available_models=["llama3:latest"],
    )
    intent = await router.classify_intent("This is my private password")
    assert intent == Intent.PRIVATE


@pytest.mark.asyncio
async def test_classify_intent_nsfw():
    """NSFW keywords route to NSFW intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        remote_clients={},
        available_models=["llama3:latest"],
    )
    intent = await router.classify_intent("Let's do some erotic roleplay")
    assert intent == Intent.NSFW


@pytest.mark.asyncio
async def test_classify_intent_coding():
    """Coding keywords route to CODING intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        remote_clients={},
        available_models=["llama3:latest"],
    )
    intent = await router.classify_intent("Write a Python script")
    assert intent == Intent.CODING


@pytest.mark.asyncio
async def test_classify_intent_finance():
    """Finance keywords route to FINANCE intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        remote_clients={},
        available_models=["llama3:latest"],
    )
    intent = await router.classify_intent("Best investment strategy for wealth")
    assert intent == Intent.FINANCE


@pytest.mark.asyncio
async def test_route_request_returns_all_fields(router):
    """Route request returns intent, adapter, answer, security."""
    # Use long prompt to trigger QUALITY -> anthropic (mock)
    long_prompt = "Explain the theory of relativity in detail " * 5
    result = await router.route_request(long_prompt)
    assert "intent" in result
    assert "adapter" in result
    assert "answer" in result
    assert "security" in result
    assert "requires_privacy" in result
    assert result["answer"]


@pytest.mark.asyncio
async def test_route_request_finance_uses_local():
    """Finance intent uses local client (fallback)."""
    mock = MockAdapter("local")
    router = ModelRouter(
        local_client=mock,
        remote_clients={},
        available_models=[],
        security_validator=None,
    )
    result = await router.route_request("Best investment strategy for wealth")
    assert result["intent"] == "finance"
    assert result["answer"] == "Mock response for: Best investment strategy for wealth"
