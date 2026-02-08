"""
Telegram adapter for the Secure Personal Agentic Platform.

Implements real Telegram bot integration with:
- Fast presence model (instant acknowledgment)
- Typing indicators
- Intent-based routing
- User authorization (optional allowlist)
- /status, /start, /help commands
- private: prefix for forced local-only routing
- /setmychat: designate current chat for proactive messages
"""

import logging
import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

from .config import settings
from .router import ModelRouter
from .adapters_local import OllamaAdapter

logger = logging.getLogger(__name__)

PRIVATE_PREFIX = "private:"
TELEGRAM_API_BASE = "https://api.telegram.org"


async def send_telegram_message(chat_id: str, text: str, token: str | None = None) -> bool:
    """
    Send a message to a Telegram chat via the Bot API.
    Works standalone (e.g. from FastAPI) without the bot process running.
    """
    from .config import settings
    tok = token or settings.telegram_bot_token
    if not tok or tok == "your_telegram_bot_token_here":
        logger.warning("No Telegram bot token configured")
        return False
    url = f"{TELEGRAM_API_BASE}/bot{tok}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text})
            if resp.status_code != 200:
                logger.error(f"Telegram API error: {resp.status_code} {resp.text}")
                return False
            return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def get_primary_chat_id() -> str | None:
    """Return primary chat ID from config or file."""
    from .config import settings
    if settings.telegram_primary_chat_id:
        return settings.telegram_primary_chat_id
    path = settings.telegram_primary_chat_file
    if os.path.exists(path):
        try:
            with open(path) as f:
                return f.read().strip() or None
        except OSError:
            pass
    return None


class TelegramAdapter:
    def __init__(self, token: str, router: ModelRouter):
        self.token = token
        self.router = router
        self.application = Application.builder().token(token).build()
        self.allowed_users = set(settings.telegram_allowed_users or [])

        # Fast presence model for instant acknowledgment
        self.presence_model = OllamaAdapter(model_name=settings.local_presence_model)

        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("setmychat", self.setmychat_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def _is_user_allowed(self, user_id: int) -> bool:
        """Check if user is allowed. Empty allowlist = allow all."""
        if not self.allowed_users:
            return True
        return str(user_id) in self.allowed_users

    async def _reject_unauthorized(self, update: Update) -> bool:
        """If user not allowed, send message and return True. Otherwise return False."""
        if not self._is_user_allowed(update.effective_user.id):
            await update.message.reply_text(
                "You are not authorised to use this bot. Contact the administrator."
            )
            return True
        return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if await self._reject_unauthorized(update):
            return
        welcome_message = (
            "🦞 Welcome to your Secure Personal Agentic Platform!\n\n"
            "I'm your private AI assistant with intelligent routing:\n"
            "• 🔒 Private/NSFW → Local models (hermes-roleplay)\n"
            "• 💻 Coding → CodeLlama or Anthropic\n"
            "• 💰 Finance → Manual approval required\n"
            "• ⚡ Speed → Fast local models\n"
            "• 🎯 Quality → Anthropic Claude\n\n"
            "Just send me a message and I'll route it intelligently!"
        )
        await update.message.reply_text(welcome_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - check if local models (Ollama) are active."""
        if await self._reject_unauthorized(update):
            return
        ollama_url = settings.ollama_base_url or "http://localhost:11434"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{ollama_url}/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    names = [m.get("name", "?") for m in models[:5]]
                    msg = (
                        "Local models (Ollama): online\n"
                        f"Available: {', '.join(names) or 'none'}"
                    )
                else:
                    msg = f"Ollama returned status {resp.status_code}"
        except httpx.ConnectError:
            msg = "Local models (Ollama): offline. Run `ollama serve` to start."
        except Exception as e:
            msg = f"Status check failed: {e}"
        await update.message.reply_text(msg)

    async def setmychat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Designate this chat as the primary chat for proactive messages."""
        if await self._reject_unauthorized(update):
            return
        chat_id = str(update.effective_chat.id)
        path = settings.telegram_primary_chat_file
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        try:
            with open(path, "w") as f:
                f.write(chat_id)
            await update.message.reply_text(
                f"✓ This chat is now your primary chat for proactive messages.\n"
                f"Chat ID: {chat_id}"
            )
        except OSError as e:
            logger.error(f"Could not save primary chat: {e}")
            await update.message.reply_text(f"Could not save: {e}")

    async def send_to_primary_chat(self, text: str) -> bool:
        """Send a message to the primary chat. Returns True if sent, False otherwise."""
        chat_id = get_primary_chat_id()
        if not chat_id:
            logger.warning("No primary chat configured. Send /setmychat from Telegram first.")
            return False
        return await send_telegram_message(chat_id, text, self.token)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if await self._reject_unauthorized(update):
            return
        help_message = (
            "🤖 *Available Commands:*\n"
            "/start - Welcome message\n"
            "/help - This help message\n"
            "/status - Check if local models (Ollama) are active\n"
            "/setmychat - Designate this chat for proactive messages\n\n"
            "*How I work:*\n"
            "I analyze your message intent and route to the best model:\n"
            "• Private matters → Local only\n"
            "• Code tasks → Specialized coding models\n"
            "• Complex reasoning → High-quality APIs\n"
            "• Quick questions → Fast local models\n\n"
            "Prefix `private:` to force local-only routing.\n\n"
            "I'll always acknowledge your message instantly, "
            "even if processing takes longer!"
        )
        await update.message.reply_text(help_message, parse_mode="Markdown")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle incoming messages with fast presence + slow processing.

        This implements the "killer feature": fast UI presence while slow models work.
        Supports `private:` prefix to force local-only routing.
        """
        if await self._reject_unauthorized(update):
            return

        user_message = update.message.text
        mode_id = None
        text_to_route = user_message

        if user_message.strip().lower().startswith(PRIVATE_PREFIX):
            mode_id = "private"
            text_to_route = user_message[len(PRIVATE_PREFIX) :].strip()
            if not text_to_route:
                await update.message.reply_text(
                    "Usage: private: <your message>. Example: private: What's my password?"
                )
                return

        # Step 1: Instant acknowledgment with fast presence model
        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Fast acknowledgment (< 500ms target)
            ack_prompt = f"Briefly acknowledge this request in 1 sentence: {text_to_route[:100]}"
            acknowledgment = await self.presence_model.generate(ack_prompt)
            await update.message.reply_text(f"⚡ {acknowledgment}")

            # Step 2: Route to appropriate model for full processing
            await update.message.chat.send_action(ChatAction.TYPING)

            routing_info = await self.router.route_request(
                text_to_route, mode_id=mode_id
            )
            intent = routing_info['intent']
            adapter_name = routing_info['adapter']
            
            # Show routing info (for transparency)
            routing_msg = f"🎯 Routing: {intent} → {adapter_name}"
            await update.message.reply_text(routing_msg)
            
            # Step 3: Get full response from routed model
            # This is already handled by route_request in our current architecture
            response = routing_info['answer']
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                f"❌ Sorry, I encountered an error: {str(e)}"
            )
    
    def run(self):
        """Start the Telegram bot"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def run_async(self):
        """Start the bot asynchronously (for integration with other services)"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
