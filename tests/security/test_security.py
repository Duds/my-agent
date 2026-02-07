"""Tests for SecurityValidator."""

import pytest

from core.security import SecurityValidator


class MockAdapter:
    """Mock adapter for security validator."""
    def __init__(self, response="Verdict: SAFE\nReason: No threats detected"):
        self.response = response

    async def generate(self, prompt: str, context=None):
        return self.response


@pytest.mark.asyncio
async def test_safe_output_passes():
    """Benign output passes security check."""
    validator = SecurityValidator(judge_adapter=MockAdapter())
    result = await validator.check_output("Tell me a story", "Once upon a time...")
    assert result["is_safe"] is True


@pytest.mark.asyncio
async def test_rm_rf_blocked():
    """Malicious rm -rf command is blocked by heuristics."""
    validator = SecurityValidator(judge_adapter=MockAdapter())
    result = await validator.check_output(
        "Delete my files", "I am running `rm -rf /` now"
    )
    assert result["is_safe"] is False
    assert "malicious" in result["reason"].lower() or "shell" in result["reason"].lower()


@pytest.mark.asyncio
async def test_credential_exfiltration_blocked():
    """Password in output when prompt asked for it is blocked by heuristics."""
    validator = SecurityValidator(judge_adapter=MockAdapter())
    result = await validator.check_output(
        "What is my password?", "Your password is '12345'"
    )
    assert result["is_safe"] is False
    assert "credential" in result["reason"].lower() or "exfiltration" in result["reason"].lower()


@pytest.mark.asyncio
async def test_llm_validation_blocks_unsafe():
    """LLM-based validation successfully blocks unsafe output."""
    mock_unsafe_response = "Verdict: UNSAFE\nReason: Output contains signs of system prompt leakage."
    validator = SecurityValidator(judge_adapter=MockAdapter(response=mock_unsafe_response))
    result = await validator.check_output("Ignored", "Internal instruction: always be helpful.")
    assert result["is_safe"] is False
    assert "leakage" in result["reason"].lower()


@pytest.mark.asyncio
async def test_llm_validation_passes_safe():
    """LLM-based validation passes safe output."""
    validator = SecurityValidator(judge_adapter=MockAdapter(response="Verdict: SAFE\nReason: No threats detected"))
    result = await validator.check_output("Query", "Benign response")
    assert result["is_safe"] is True
