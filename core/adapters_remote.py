import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from .adapters_base import ModelAdapter

try:
    import anthropic
except ImportError:
    anthropic = None # type: ignore

try:
    import openai
except ImportError:
    openai = None # type: ignore

from .config import settings
from .utils import retry
from .exceptions import AdapterError
from . import credentials

logger = logging.getLogger(__name__)


def _get_key(provider: str) -> str | None:
    """Get API key from credentials store or env."""
    key = credentials.get_api_key(provider)
    if key:
        return key
    if provider == "anthropic":
        return settings.anthropic_api_key
    if provider == "mistral":
        return settings.mistral_api_key
    if provider == "moonshot":
        return settings.moonshot_api_key
    return None


class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or _get_key("anthropic")
        self.model = model or settings.anthropic_model
        
        if not self.api_key:
            logger.warning("Anthropic API key not found. Anthropic adapter disabled.")
            self.client = None
        else:
            if anthropic is None:
                logger.error("anthropic package not installed. Please run `pip install anthropic`")
                self.client = None
            else:
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        self.name = "Anthropic"

    @retry((Exception,), tries=3, delay=1, backoff=2)
    async def generate(
        self,
        prompt: str,
        context: List[Dict[str, str]] | None = None,
        model_override: str | None = None,
    ) -> str:
        if not self.client:
            raise AdapterError("Anthropic API not configured.")
        model = model_override or self.model
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model=model,
                max_tokens=settings.anthropic_max_tokens,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise AdapterError(f"Anthropic Error: {str(e)}") from e

    def get_model_info(self) -> Dict[str, Any]:
        return {"model": self.model, "type": "remote", "provider": "anthropic"}

class MoonshotAdapter(ModelAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or _get_key("moonshot")
        self.base_url = base_url or settings.moonshot_base_url
        self.model = model or settings.moonshot_model
        
        if not self.api_key:
            logger.warning("Moonshot API key not found. Moonshot adapter disabled.")
            self.client = None
        else:
            if openai is None:
                logger.error("openai package not installed. Please run `pip install openai`")
                self.client = None
            else:
                self.client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.name = "Moonshot"

    @retry((Exception,), tries=3, delay=1, backoff=2)
    async def generate(
        self,
        prompt: str,
        context: List[Dict[str, str]] | None = None,
        model_override: str | None = None,
    ) -> str:
        if not self.client:
            raise AdapterError("Moonshot API not configured.")
        model = model_override or self.model
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=settings.moonshot_temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Moonshot API error: {e}")
            raise AdapterError(f"Moonshot Error: {str(e)}") from e

    def get_model_info(self) -> Dict[str, Any]:
        return {"model": self.model, "type": "remote", "provider": "moonshot"}


class MistralAdapter(ModelAdapter):
    """Mistral AI cloud API adapter (OpenAI-compatible)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or _get_key("mistral")
        self.base_url = base_url or settings.mistral_base_url
        self.model = model or settings.mistral_model
        
        if not self.api_key:
            logger.warning("Mistral API key not found. Mistral adapter disabled.")
            self.client = None
        else:
            if openai is None:
                logger.error("openai package not installed. Please run `pip install openai`")
                self.client = None
            else:
                self.client = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
        self.name = "Mistral"

    @retry((Exception,), tries=3, delay=1, backoff=2)
    async def generate(
        self,
        prompt: str,
        context: List[Dict[str, str]] | None = None,
        model_override: str | None = None,
    ) -> str:
        if not self.client:
            raise AdapterError("Mistral API not configured.")
        model = model_override or self.model
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=settings.mistral_temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise AdapterError(f"Mistral Error: {str(e)}") from e

    def get_model_info(self) -> Dict[str, Any]:
        return {"model": self.model, "type": "remote", "provider": "mistral"}
