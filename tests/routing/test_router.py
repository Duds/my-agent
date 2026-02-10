"""Tests for ModelRouter."""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from core.router import Intent, ModelRouter
from core.factory import AdapterFactory


class MockAdapter:
    """Minimal mock adapter for testing."""

    def __init__(self, name: str = "mock"):
        self.name = name

    async def generate(self, prompt: str, context=None, model_override=None):
        return f"Mock response for: {prompt[:50]}"

    def get_model_info(self):
        return {"model": self.name, "type": "mock"}


@pytest.mark.asyncio
async def test_classify_intent_private():
    """Private keywords route to PRIVATE intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        adapter_factory=MagicMock(spec=AdapterFactory),
        available_models=["llama3:latest"],
    )
    intent = await router.classify_intent("This is my private password")
    assert intent == Intent.PRIVATE


@pytest.mark.asyncio
async def test_classify_intent_nsfw():
    """NSFW keywords route to NSFW intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        adapter_factory=MagicMock(spec=AdapterFactory),
        available_models=["llama3:latest"],
    )
    intent = await router.classify_intent("Let's do some erotic roleplay")
    assert intent == Intent.NSFW
    # Erotic-only (no "roleplay" keyword) should also route to NSFW
    intent2 = await router.classify_intent("Help me write an erotic sms message to my girlfriend")
    assert intent2 == Intent.NSFW


@pytest.mark.asyncio
async def test_classify_intent_coding():
    """Coding keywords route to CODING intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        adapter_factory=MagicMock(spec=AdapterFactory),
        available_models=["llama3:latest"],
    )
    intent = await router.classify_intent("Write a Python script")
    assert intent == Intent.CODING


@pytest.mark.asyncio
async def test_classify_intent_finance():
    """Finance keywords route to FINANCE intent."""
    router = ModelRouter(
        local_client=MockAdapter(),
        adapter_factory=MagicMock(spec=AdapterFactory),
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
        adapter_factory=MagicMock(spec=AdapterFactory),
        available_models=[],
        security_validator=None,
    )
    result = await router.route_request("Best investment strategy for wealth")
    assert result["intent"] == "finance"
    assert result["answer"] == "Mock response for: Best investment strategy for wealth"


@pytest.mark.asyncio
async def test_route_request_speed_uses_local():
    """Short prompt routes to SPEED and uses local client when no remote."""
    mock_local = MockAdapter("local-default")
    mock_factory = MagicMock(spec=AdapterFactory)
    mock_factory.get_remote_adapter.return_value = None
    mock_factory.get_local_adapter.return_value = mock_local
    router = ModelRouter(
        local_client=mock_local,
        adapter_factory=mock_factory,
        available_models=["llama3:latest"],
        security_validator=None,
    )
    result = await router.route_request("What is 2+2?")
    assert "intent" in result
    assert "answer" in result
    assert "Mock response" in result["answer"]


@pytest.mark.asyncio
async def test_route_request_create_agent_returns_generator_message():
    """CREATE_AGENT intent calls agent generator and returns its message."""
    mock_gen_adapter = MockAdapter("anthropic")
    mock_factory = MagicMock(spec=AdapterFactory)
    mock_factory.get_remote_adapter.return_value = mock_gen_adapter
    mock_factory.get_local_adapter.return_value = MockAdapter("local")

    router = ModelRouter(
        local_client=MockAdapter(),
        adapter_factory=mock_factory,
        available_models=[],
        security_validator=None,
    )

    with patch.object(router, "classify_intent", new_callable=AsyncMock, return_value=Intent.CREATE_AGENT):
        with patch("core.agent_generator.generate_and_register_agent", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = (
                True,
                "Agent 'Weather Bot' is ready for review. You can register it from the Review dialog.",
                {"code": "# generated code", "agent_id": "weather-bot", "agent_name": "Weather Bot", "valid": True},
            )
            result = await router.route_request("Create an agent to fetch weather from BOM")

    assert result["intent"] == "create_agent"
    assert result["adapter"] == "agent-generator"
    assert "Weather Bot" in result["answer"]
    assert result["requires_privacy"] is False
    assert result["security"]["is_safe"] is True
    assert result.get("agent_generated") is not None
    assert result["agent_generated"]["agent_name"] == "Weather Bot"
    mock_gen.assert_called_once_with(
        user_request="Create an agent to fetch weather from BOM",
        adapter=mock_gen_adapter,
        model_override=None,
        dry_run=True,
    )


@pytest.mark.asyncio
async def test_nsfw_ignores_model_override():
    """NSFW/erotic prompts route to hermes even when model_id is passed (privacy override)."""
    mock_hermes = MockAdapter("hermes-roleplay:latest")
    mock_hermes.generate = AsyncMock(return_value="Mock NSFW response")

    mock_factory = MagicMock(spec=AdapterFactory)
    mock_factory.get_local_adapter.return_value = mock_hermes

    router = ModelRouter(
        local_client=MockAdapter(),
        adapter_factory=mock_factory,
        available_models=["mistral:latest", "llama3:latest"],
        security_validator=None,
    )
    result = await router.route_request(
        "Help me write an erotic sms message to my girlfriend",
        model_id="mistral:latest",
    )
    assert result["intent"] == "nsfw"
    assert "hermes" in result["adapter"].lower() or "roleplay" in result["adapter"].lower()
    assert result["requires_privacy"] is True


@pytest.mark.asyncio
async def test_route_request_quality_mocked_remote():
    """QUALITY intent with mocked anthropic adapter returns remote response."""
    long_prompt = "Explain the theory of relativity in great detail and provide a comprehensive analysis."
    mock_remote = MockAdapter("anthropic")
    mock_remote.generate = AsyncMock(return_value="Detailed explanation of special and general relativity.")
    mock_factory = MagicMock(spec=AdapterFactory)
    mock_factory.get_remote_adapter.return_value = mock_remote
    mock_factory.get_local_adapter.return_value = MockAdapter("local")

    router = ModelRouter(
        local_client=MockAdapter(),
        adapter_factory=mock_factory,
        available_models=[],
        security_validator=None,
    )
    with patch.object(router, "classify_intent", new_callable=AsyncMock, return_value=Intent.QUALITY):
        result = await router.route_request(long_prompt)
    assert result["intent"] == "quality"
    assert result["adapter"] == "anthropic"
    assert "relativity" in result["answer"].lower()
    mock_remote.generate.assert_called_once()


@pytest.mark.asyncio
async def test_route_request_fallback_primary_fails_local_succeeds():
    """When primary adapter raises AdapterError, fallback to local succeeds."""
    from core.exceptions import AdapterError

    mock_remote = MockAdapter("anthropic")
    mock_remote.generate = AsyncMock(side_effect=AdapterError("API rate limit"))
    mock_local = MockAdapter("local")
    mock_local.generate = AsyncMock(return_value="Fallback response from local model")
    mock_factory = MagicMock(spec=AdapterFactory)
    mock_factory.get_remote_adapter.return_value = mock_remote
    mock_factory.get_local_adapter.return_value = mock_local

    router = ModelRouter(
        local_client=mock_local,
        adapter_factory=mock_factory,
        available_models=[],
        security_validator=None,
    )
    with patch.object(router, "classify_intent", new_callable=AsyncMock, return_value=Intent.QUALITY):
        result = await router.route_request("Explain quantum entanglement in detail.")
    assert result["intent"] == "quality"
    assert "fallback" in result["adapter"].lower()
    assert "Fallback response" in result["answer"]
    mock_local.generate.assert_called_once()
