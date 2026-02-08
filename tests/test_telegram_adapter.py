"""Unit tests for Telegram adapter handlers and authorisation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.adapters_telegram import TelegramAdapter, PRIVATE_PREFIX


def _create_adapter_with_mocked_app(router, allowed_users=None):
    """Create TelegramAdapter with Application mocked to avoid real Telegram API setup."""
    mock_app = MagicMock()
    with patch("core.adapters_telegram.Application") as mock_app_cls:
        mock_app_cls.builder.return_value.token.return_value.build.return_value = mock_app
        with patch("core.adapters_telegram.OllamaAdapter") as mock_ollama:
            mock_ollama.return_value.generate = AsyncMock(return_value="Acknowledged!")
            adapter = TelegramAdapter(token="test-token", router=router)
            if allowed_users is not None:
                adapter.allowed_users = set(allowed_users)
            return adapter


def _make_update(user_id: int = 12345, text: str = "hello") -> MagicMock:
    """Create a mock Update with message and user."""
    update = MagicMock()
    update.effective_user.id = user_id
    update.message = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()
    update.message.chat.send_action = AsyncMock()
    return update


@pytest.fixture
def mock_router():
    """Mock ModelRouter with route_request."""
    router = MagicMock()
    router.route_request = AsyncMock(
        return_value={
            "intent": "speed",
            "adapter": "mistral",
            "answer": "Mock response",
            "model_info": {},
            "requires_privacy": False,
            "security": {"is_safe": True},
        }
    )
    return router


@pytest.fixture
def telegram_adapter(mock_router):
    """Create TelegramAdapter with empty allowlist (allow all)."""
    return _create_adapter_with_mocked_app(mock_router, allowed_users=[])


@pytest.fixture
def telegram_adapter_restricted(mock_router):
    """Create TelegramAdapter with user allowlist."""
    return _create_adapter_with_mocked_app(mock_router, allowed_users=["111", "222"])


class TestUserAuthorization:
    """Tests for _is_user_allowed and _reject_unauthorized."""

    def test_empty_allowlist_allows_all(self, telegram_adapter):
        telegram_adapter.allowed_users = set()
        assert telegram_adapter._is_user_allowed(999) is True

    def test_allowlist_permits_listed_user(self, telegram_adapter_restricted):
        assert telegram_adapter_restricted._is_user_allowed(111) is True
        assert telegram_adapter_restricted._is_user_allowed(222) is True

    def test_allowlist_rejects_unlisted_user(self, telegram_adapter_restricted):
        assert telegram_adapter_restricted._is_user_allowed(999) is False

    @pytest.mark.asyncio
    async def test_reject_unauthorized_sends_message(self, telegram_adapter_restricted):
        update = _make_update(user_id=999)
        result = await telegram_adapter_restricted._reject_unauthorized(update)
        assert result is True
        update.message.reply_text.assert_called_once()
        assert "not authorised" in update.message.reply_text.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_reject_unauthorized_allows_listed_user(self, telegram_adapter_restricted):
        update = _make_update(user_id=111)
        result = await telegram_adapter_restricted._reject_unauthorized(update)
        assert result is False
        update.message.reply_text.assert_not_called()


class TestStartCommand:
    """Tests for /start handler."""

    @pytest.mark.asyncio
    async def test_start_sends_welcome(self, telegram_adapter):
        update = _make_update(text="/start")
        await telegram_adapter.start_command(update, MagicMock())
        update.message.reply_text.assert_called_once()
        assert "Welcome" in update.message.reply_text.call_args[0][0]
        assert "Secure Personal Agentic Platform" in update.message.reply_text.call_args[0][0]


class TestStatusCommand:
    """Tests for /status handler."""

    @pytest.mark.asyncio
    async def test_status_ollama_online(self, telegram_adapter):
        update = _make_update(text="/status")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": [{"name": "llama3"}, {"name": "mistral"}]}

        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_resp)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)

        with patch("core.adapters_telegram.httpx.AsyncClient", return_value=mock_instance):
            with patch.object(telegram_adapter, "_reject_unauthorized", return_value=False):
                await telegram_adapter.status_command(update, MagicMock())

        update.message.reply_text.assert_called_once()
        msg = update.message.reply_text.call_args[0][0]
        assert "online" in msg.lower()
        assert "llama3" in msg or "mistral" in msg

    @pytest.mark.asyncio
    async def test_status_ollama_offline(self, telegram_adapter):
        update = _make_update(text="/status")
        import httpx

        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)

        with patch("core.adapters_telegram.httpx.AsyncClient", return_value=mock_instance):
            with patch.object(telegram_adapter, "_reject_unauthorized", return_value=False):
                await telegram_adapter.status_command(update, MagicMock())

        update.message.reply_text.assert_called_once()
        msg = update.message.reply_text.call_args[0][0]
        assert "offline" in msg.lower()


class TestSetMyChatCommand:
    """Tests for /setmychat handler."""

    @pytest.mark.asyncio
    async def test_setmychat_saves_chat_id(self, telegram_adapter, tmp_path):
        from core.config import settings
        with patch.object(settings, "telegram_primary_chat_file", str(tmp_path / "chat.txt")):
            update = _make_update(user_id=111, text="/setmychat")
            update.effective_chat.id = 999888777
            await telegram_adapter.setmychat_command(update, MagicMock())
        update.message.reply_text.assert_called_once()
        assert "primary" in update.message.reply_text.call_args[0][0].lower()
        assert (tmp_path / "chat.txt").read_text().strip() == "999888777"


class TestHelpCommand:
    """Tests for /help handler."""

    @pytest.mark.asyncio
    async def test_help_includes_status_and_private(self, telegram_adapter):
        update = _make_update(text="/help")
        await telegram_adapter.help_command(update, MagicMock())
        update.message.reply_text.assert_called_once()
        msg = update.message.reply_text.call_args[0][0]
        assert "/status" in msg
        assert "private" in msg.lower()


class TestHandleMessage:
    """Tests for message handler (private: prefix, routing)."""

    @pytest.mark.asyncio
    async def test_regular_message_routes_without_mode(self, telegram_adapter, mock_router):
        update = _make_update(text="What is 2+2?")
        await telegram_adapter.handle_message(update, MagicMock())
        mock_router.route_request.assert_called_once()
        call_kwargs = mock_router.route_request.call_args[1]
        assert call_kwargs.get("mode_id") is None
        assert "2+2" in mock_router.route_request.call_args[0][0]

    @pytest.mark.asyncio
    async def test_private_prefix_strips_and_passes_mode(self, telegram_adapter, mock_router):
        update = _make_update(text="private: What is my password?")
        await telegram_adapter.handle_message(update, MagicMock())
        mock_router.route_request.assert_called_once()
        call_args = mock_router.route_request.call_args
        assert call_args[0][0] == "What is my password?"
        assert call_args[1]["mode_id"] == "private"

    @pytest.mark.asyncio
    async def test_private_prefix_empty_message_returns_usage(self, telegram_adapter):
        update = _make_update(text="private:")
        await telegram_adapter.handle_message(update, MagicMock())
        assert update.message.reply_text.called
        call_args_list = update.message.reply_text.call_args_list
        msgs = [c[0][0] for c in call_args_list if c[0]]
        assert any("Usage" in msg for msg in msgs), f"Expected Usage in reply, got: {msgs}"

    @pytest.mark.asyncio
    async def test_private_prefix_case_insensitive(self, telegram_adapter, mock_router):
        update = _make_update(text="Private: secret stuff")
        await telegram_adapter.handle_message(update, MagicMock())
        mock_router.route_request.assert_called_once()
        assert mock_router.route_request.call_args[1]["mode_id"] == "private"
        assert "secret stuff" in mock_router.route_request.call_args[0][0]
