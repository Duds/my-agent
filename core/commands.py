"""
Structured chat commands for MyAgent.

Defines slash-style commands (/status, /reset, /think) for consistent behaviour
across Telegram and future channel adapters. Commands are handled before
routing to the model.
"""

from typing import Any

# Command definitions for API documentation and channel implementers
CHAT_COMMANDS = [
    {
        "name": "status",
        "description": "Check session and model status (Ollama, backend)",
        "usage": "/status",
        "channel_support": ["telegram"],
    },
    {
        "name": "reset",
        "description": "Clear conversation context and start fresh",
        "usage": "/reset",
        "channel_support": ["telegram"],
    },
    {
        "name": "think",
        "description": "Set thinking level: brief (default) or deep",
        "usage": "/think [brief|deep]",
        "channel_support": ["telegram"],
    },
    {
        "name": "start",
        "description": "Welcome message and initial setup",
        "usage": "/start",
        "channel_support": ["telegram"],
    },
    {
        "name": "help",
        "description": "List available commands and usage",
        "usage": "/help",
        "channel_support": ["telegram"],
    },
    {
        "name": "setmychat",
        "description": "Designate current chat for proactive messages",
        "usage": "/setmychat",
        "channel_support": ["telegram"],
    },
]


def get_commands_list() -> list[dict[str, Any]]:
    """Return structured list of chat commands for API and documentation."""
    return CHAT_COMMANDS.copy()
