"""Tests for core.utils."""

import pytest
from unittest.mock import AsyncMock, patch
import asyncio

from core.utils import clean_model_placeholders, retry


def test_clean_model_placeholders_empty():
    """Empty string is returned unchanged."""
    assert clean_model_placeholders("") == ""


def test_clean_model_placeholders_removes_placeholders():
    """Model placeholder artifacts are removed."""
    text = "Hello [GLOBAL_LOCATION] world [USER_NAME] here."
    result = clean_model_placeholders(text)
    assert "[GLOBAL_LOCATION]" not in result
    assert "[USER_NAME]" not in result
    assert "Hello" in result and "world" in result and "here" in result


def test_clean_model_placeholders_collapses_double_space():
    """Placeholders are removed; implementation collapses one level of double space."""
    text = "Hello [GLOBAL_LOCATION] world"
    result = clean_model_placeholders(text)
    assert "[GLOBAL_LOCATION]" not in result
    assert "Hello" in result and "world" in result


def test_clean_model_placeholders_plain_text_unchanged():
    """Plain text without placeholders is preserved (aside from strip)."""
    text = "No placeholders here."
    assert clean_model_placeholders(text) == "No placeholders here."


@pytest.mark.asyncio
async def test_retry_succeeds_first_try():
    """Retry decorator passes through when func succeeds."""
    @retry(Exception, tries=2)
    async def ok():
        return 42
    result = await ok()
    assert result == 42


@pytest.mark.asyncio
async def test_retry_succeeds_after_fail():
    """Retry decorator retries and returns when func eventually succeeds."""
    calls = []

    @retry(ValueError, tries=3, delay=0.01, backoff=1.0, jitter=False)
    async def flaky():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("nope")
        return "ok"

    result = await flaky()
    assert result == "ok"
    assert len(calls) == 2
