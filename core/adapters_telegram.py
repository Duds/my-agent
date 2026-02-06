"""
Telegram adapter for the Secure Personal Agentic Platform.

Implements real Telegram bot integration with:
- Fast presence model (instant acknowledgment)
- Typing indicators
- Intent-based routing
- Session management
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

from .router import ModelRouter
from .adapters_local import OllamaAdapter

logger = logging.getLogger(__name__)


class TelegramAdapter:
    def __init__(self, token: str, router: ModelRouter):
        self.token = token
        self.router = router
        self.application = Application.builder().token(token).build()
        
        # Fast presence model for instant acknowledgment
        self.presence_model = OllamaAdapter(model_name="mistral")
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
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
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🤖 **Available Commands:**\n"
            "/start - Welcome message\n"
            "/help - This help message\n\n"
            "**How I work:**\n"
            "I analyze your message intent and route to the best model:\n"
            "• Private matters → Local only\n"
            "• Code tasks → Specialized coding models\n"
            "• Complex reasoning → High-quality APIs\n"
            "• Quick questions → Fast local models\n\n"
            "I'll always acknowledge your message instantly, "
            "even if processing takes longer!"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle incoming messages with fast presence + slow processing.
        
        This implements the "killer feature": fast UI presence while slow models work.
        """
        user_message = update.message.text
        # chat_id = update.effective_chat.id
        
        # Step 1: Instant acknowledgment with fast presence model
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            # Fast acknowledgment (< 500ms target)
            ack_prompt = f"Briefly acknowledge this request in 1 sentence: {user_message[:100]}"
            acknowledgment = await self.presence_model.generate(ack_prompt)
            await update.message.reply_text(f"⚡ {acknowledgment}")
            
            # Step 2: Route to appropriate model for full processing
            await update.message.chat.send_action(ChatAction.TYPING)
            
            routing_info = await self.router.route_request(user_message)
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
