import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from ..core.router import ModelRouter

class TelegramAdapter:
    def __init__(self, token: str, router: ModelRouter):
        self.token = token
        self.router = router
        self.application = ApplicationBuilder().token(token).build()
        
        # Add handlers
        self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        chat_id = update.effective_chat.id
        
        # Determine routing
        routing_info = await self.router.route_request(user_text)
        
        # Send thinking message
        # In a real impl, we'd call the actual model here
        response_text = f"Intent: {routing_info['intent']}\nAdapter: {routing_info['adapter']}\n\n[System]: Routing verified. I am processing your request securely."
        
        await context.bot.send_message(chat_id=chat_id, text=response_text)

    def run(self):
        print("Starting Telegram Bot (Polling mode)...")
        self.application.run_polling()
