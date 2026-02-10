"""Tests for MemorySystem."""

import pytest
from core.memory import MemorySystem
from core.exceptions import MemoryError


@pytest.fixture
def memory_system(tmp_path):
    """MemorySystem with temporary base path."""
    return MemorySystem(base_path=str(tmp_path))


@pytest.mark.asyncio
async def test_get_context_empty(memory_system):
    """get_context returns empty list for new session."""
    ctx = await memory_system.get_context("session-1")
    assert ctx == []


@pytest.mark.asyncio
async def test_save_chat_turn_and_get_context_roundtrip(memory_system):
    """save_chat_turn then get_context returns the saved messages."""
    await memory_system.save_chat_turn("session-1", {"role": "user", "content": "Hello"})
    await memory_system.save_chat_turn("session-1", {"role": "assistant", "content": "Hi there"})
    ctx = await memory_system.get_context("session-1", limit=10)
    assert len(ctx) == 2
    assert ctx[0]["role"] == "user" and ctx[0]["content"] == "Hello"
    assert ctx[1]["role"] == "assistant" and ctx[1]["content"] == "Hi there"
    assert "timestamp" in ctx[0] and "timestamp" in ctx[1]


@pytest.mark.asyncio
async def test_get_context_respects_limit(memory_system):
    """get_context returns only the last `limit` turns."""
    for i in range(5):
        await memory_system.save_chat_turn("session-1", {"role": "user", "content": f"Msg {i}"})
        await memory_system.save_chat_turn("session-1", {"role": "assistant", "content": f"Reply {i}"})
    ctx = await memory_system.get_context("session-1", limit=3)
    assert len(ctx) == 3
    assert ctx[0]["content"] == "Reply 2"
    assert ctx[-1]["content"] == "Reply 4"


@pytest.mark.asyncio
async def test_save_chat_turn_invalid_session_id(memory_system):
    """save_chat_turn raises MemoryError for invalid session_id."""
    with pytest.raises(MemoryError):
        await memory_system.save_chat_turn("invalid/session!!", {"role": "user", "content": "x"})


@pytest.mark.asyncio
async def test_get_context_invalid_session_id_returns_empty(memory_system):
    """get_context returns [] for invalid session_id."""
    ctx = await memory_system.get_context("bad/session")
    assert ctx == []


@pytest.mark.asyncio
async def test_vault_roundtrip(tmp_path):
    """save_to_vault and get_from_vault round-trip (no encryption when key unset)."""
    mem = MemorySystem(base_path=str(tmp_path))
    await mem.save_to_vault("test-key", {"secret": "value"})
    data = await mem.get_from_vault("test-key")
    assert data == {"secret": "value"}


@pytest.mark.asyncio
async def test_vault_encryption_roundtrip(tmp_path):
    """With fernet set, vault data round-trips correctly."""
    from cryptography.fernet import Fernet
    mem = MemorySystem(base_path=str(tmp_path))
    mem.fernet = Fernet(Fernet.generate_key())
    await mem.save_to_vault("enc-key", {"x": 1})
    data = await mem.get_from_vault("enc-key")
    assert data == {"x": 1}
