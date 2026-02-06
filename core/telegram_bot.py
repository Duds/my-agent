"""
Telegram bot entry point.

Run this to start the Telegram bot:
    PYTHONPATH=. python3 core/telegram_bot.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.adapters_telegram import TelegramAdapter
from core.adapters_remote import AnthropicAdapter, MoonshotAdapter
from core.router import ModelRouter
from core.adapters_local import OllamaAdapter
from core.security import SecurityValidator

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token or telegram_token == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file!")
        logger.error("Please get a token from @BotFather and add it to .env")
        sys.exit(1)
    
    # Initialize models and router
    logger.info("Initializing models...")
    local_model = OllamaAdapter(model_name="llama3")
    security_validator = SecurityValidator(judge_adapter=local_model)
    
    # Remote Adapters
    anthropic_adapter = AnthropicAdapter()
    moonshot_adapter = MoonshotAdapter()
    
    router = ModelRouter(
        local_client=local_model,
        remote_clients={
            "anthropic": anthropic_adapter,
            "moonshot": moonshot_adapter
        },
        security_validator=security_validator
    )
    
    # Create and run Telegram bot
    logger.info("Starting Telegram bot...")
    telegram_bot = TelegramAdapter(token=telegram_token, router=router)
    telegram_bot.run()

if __name__ == "__main__":
    main()
