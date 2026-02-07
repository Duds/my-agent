"""
Telegram bot entry point.

Run this to start the Telegram bot:
    PYTHONPATH=. python3 core/telegram_bot.py
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.logging_config import setup_logging
from core.adapters_telegram import TelegramAdapter
from core.factory import AdapterFactory
from core.router import ModelRouter
from core.security import SecurityValidator

# Configure logging before other imports
setup_logging()
logger = logging.getLogger(__name__)

def main():
    telegram_token = settings.telegram_bot_token
    if not telegram_token or telegram_token == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_BOT_TOKEN not found in configuration!")
        logger.error("Please get a token from @BotFather and add it to .env")
        sys.exit(1)
    
    # Initialize factory and remotes
    logger.info("Initializing models through factory...")
    adapter_factory = AdapterFactory()
    adapter_factory.initialize_remotes()
    
    local_model = adapter_factory.get_local_adapter(settings.ollama_default_model)
    security_validator = SecurityValidator(judge_adapter=local_model)
    
    router = ModelRouter(
        local_client=local_model,
        adapter_factory=adapter_factory,
        security_validator=security_validator
    )
    
    # Create and run Telegram bot
    logger.info("Starting Telegram bot service...")
    telegram_bot = TelegramAdapter(token=telegram_token, router=router)
    telegram_bot.run()

if __name__ == "__main__":
    main()
