"""
Centralised configuration for the Secure Personal Agentic Platform.

Uses Pydantic BaseSettings for type-safe, validated configuration from environment variables.
"""

import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: float = 120.0
    ollama_default_model: str = "llama3:latest"
    ollama_judge_model: str = "llama3"

    # Remote Models
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_max_tokens: int = 1024

    moonshot_api_key: str | None = None
    moonshot_base_url: str = "https://api.moonshot.ai/v1"
    moonshot_model: str = "moonshot-v1-8k"
    moonshot_temperature: float = 0.3

    mistral_api_key: str | None = None
    mistral_base_url: str = "https://api.mistral.ai/v1"
    mistral_model: str = "mistral-small-latest"
    mistral_temperature: float = 0.3

    # Local Model Role Mappings
    local_judge_model: str = "llama3"
    local_privacy_model: str = "hermes-roleplay"
    local_presence_model: str = "mistral"

    # Telegram
    telegram_bot_token: str | None = None
    telegram_allowed_users: List[str] = []

    # Security
    api_key: str | None = None
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/my_agent.log"
    log_rotation: str = "midnight"
    log_backup_count: int = 30
    log_format: str = "text" # "text" or "json"

    google_credentials_path: str | None = None
    vault_path: str = "memory/vault.json"
    encryption_key: str | None = None

    # Routing Configuration
    routing_config_path: str = "data/routing_rules.json"

    # MCP (Model Context Protocol) Servers
    mcp_config_path: str = "data/mcp_servers.json"

    def get_cors_origins_list(self) -> List[str]:
        """Return CORS origins as list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
