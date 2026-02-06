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

    # Anthropic
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_max_tokens: int = 1024

    # Moonshot
    moonshot_api_key: str | None = None
    moonshot_base_url: str = "https://api.moonshot.ai/v1"
    moonshot_model: str = "moonshot-v1-8k"
    moonshot_temperature: float = 0.3

    # Security
    api_key: str | None = None
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Logging
    log_level: str = "INFO"

    def get_cors_origins_list(self) -> List[str]:
        """Return CORS origins as list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
