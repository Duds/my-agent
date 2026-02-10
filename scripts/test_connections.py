"""Test script for verifying core adapter connections and imports."""

import asyncio
import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv

from core.adapters_remote import AnthropicAdapter, MistralAdapter, MoonshotAdapter


async def main():
    logger.debug("Main started")
    load_dotenv()
    logger.debug(".env loaded")
    logger.debug("Test finished")


if __name__ == "__main__":
    logger.debug("Starting event loop")
    asyncio.run(main())
