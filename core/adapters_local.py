import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from .adapters_base import ModelAdapter

from .config import settings

logger = logging.getLogger(__name__)


class OllamaAdapter(ModelAdapter):
    def __init__(self, model_name: str, base_url: Optional[str] = None):
        self.model_name = model_name
        self.base_url = base_url or settings.ollama_base_url

    async def generate(
        self,
        prompt: str,
        context: List[Dict[str, str]] | None = None,
        model_override: str | None = None,
    ) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.headers.get("Content-Type") == "application/json" else {}
            error_msg = error_data.get("error", str(e))
            return f"[LOCAL ERROR] {error_msg}"
        except httpx.ConnectError:
            return "[LOCAL ERROR] Could not connect to Ollama (Connection Refused). Is ollama serve running?"
        except httpx.TimeoutException:
            return f"[LOCAL ERROR] Ollama timed out after 120s while loading {self.model_name}. Check local resources."
        except Exception as e:
            return f"[LOCAL ERROR] Unexpected error: {type(e).__name__}: {str(e)}"

    async def generate_stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream tokens from Ollama for lower perceived latency."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    buffer = ""
                    async for chunk in response.aiter_text():
                        buffer += chunk
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                data = json.loads(line)
                                content = data.get("response", "")
                                if content:
                                    yield content
                                if data.get("done"):
                                    return
                            except json.JSONDecodeError:
                                continue
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.headers.get("Content-Type") == "application/json" else {}
            error_msg = error_data.get("error", str(e))
            yield f"[LOCAL ERROR] {error_msg}"
        except httpx.ConnectError:
            yield "[LOCAL ERROR] Could not connect to Ollama (Connection Refused). Is ollama serve running?"
        except httpx.TimeoutException:
            yield f"[LOCAL ERROR] Ollama timed out after 120s while loading {self.model_name}. Check local resources."
        except Exception as e:
            yield f"[LOCAL ERROR] Unexpected error: {type(e).__name__}: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        return {"model": self.model_name, "type": "local"}

    @staticmethod
    async def get_available_models(base_url: Optional[str] = None) -> List[str]:
        """Fetch list of available local models from Ollama."""
        url = f"{base_url or settings.ollama_base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    # Extract model names (e.g., 'llama3:latest')
                    return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.warning("Could not fetch available models: %s", e)
        return []
