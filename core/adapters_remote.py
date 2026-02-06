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

logger = logging.getLogger(__name__)

class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("CLAUDE_CODE_OAUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key or "your_anthropic_key_here" in self.api_key:
            logger.warning("Anthropic API key not found. Anthropic adapter disabled.")
            self.client = None
        else:
            if anthropic is None:
                logger.error("anthropic package not installed. Please run `pip install anthropic`")
                self.client = None
            else:
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        self.model = model
        self.name = "Anthropic"

    async def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        if not self.client:
            return "❌ Anthropic API not configured."
        
        try:
            # Simple message format
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"❌ Anthropic Error: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        return {"model": self.model, "type": "remote", "provider": "anthropic"}

class MoonshotAdapter(ModelAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.moonshot.ai/v1", model: str = "moonshot-v1-8k"):
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self.base_url = base_url
        if not self.api_key or "your_moonshot_key_here" in self.api_key:
            logger.warning("Moonshot API key not found. Moonshot adapter disabled.")
            self.client = None
        else:
            if openai is None:
                logger.error("openai package not installed. Please run `pip install openai`")
                self.client = None
            else:
                self.client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = model
        self.name = "Moonshot"

    async def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        if not self.client:
            return "❌ Moonshot API not configured."

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Moonshot API error: {e}")
            return f"❌ Moonshot Error: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        return {"model": self.model, "type": "remote", "provider": "moonshot"}
