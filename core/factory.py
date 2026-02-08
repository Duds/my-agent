import logging
from typing import Dict, Optional, List

from .adapters_base import ModelAdapter
from .adapters_local import OllamaAdapter
from .adapters_remote import AnthropicAdapter, MistralAdapter, MoonshotAdapter
from .config import settings
from . import credentials

logger = logging.getLogger(__name__)


def _get_provider_key(provider: str) -> str | None:
    """Get API key for provider (credentials file or env)."""
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


class AdapterFactory:
    """
    Central factory for managing model adapter instances.
    Ensures that adapters are reused when possible, reducing resource overhead.
    """

    def __init__(self):
        self._local_pool: Dict[str, OllamaAdapter] = {}
        self._remote_instances: Dict[str, ModelAdapter] = {}
        self._initialized = False

    def initialize_remotes(self):
        """Pre-initialize remote adapters if API keys are present."""
        if self._initialized:
            return

        if _get_provider_key("anthropic"):
            adapter = AnthropicAdapter()
            if adapter.client:
                self._remote_instances["anthropic"] = adapter
                logger.debug("Anthropic adapter initialized in factory")

        if _get_provider_key("mistral"):
            adapter = MistralAdapter()
            if adapter.client:
                self._remote_instances["mistral"] = adapter
                logger.debug("Mistral adapter initialized in factory")

        if _get_provider_key("moonshot"):
            adapter = MoonshotAdapter()
            if adapter.client:
                self._remote_instances["moonshot"] = adapter
                logger.debug("Moonshot adapter initialized in factory")

        self._initialized = True

    def reinitialize_remotes(self):
        """Re-initialize remote adapters (e.g. after credentials change)."""
        self._remote_instances.clear()
        self._initialized = False
        self.initialize_remotes()

    def get_local_adapter(self, model_name: str) -> OllamaAdapter:
        """Get or create a pooled OllamaAdapter for the given model_name."""
        if model_name not in self._local_pool:
            logger.debug(f"Creating new OllamaAdapter for {model_name}")
            self._local_pool[model_name] = OllamaAdapter(model_name=model_name)
        return self._local_pool[model_name]

    def get_remote_adapter(self, provider: str) -> Optional[ModelAdapter]:
        """Get a registered remote adapter by provider name."""
        return self._remote_instances.get(provider.lower())

    def get_all_remote_adapters(self) -> Dict[str, ModelAdapter]:
        """Return all available remote adapter instances."""
        return self._remote_instances.copy()

    def clear(self):
        """Clear all pooled instances (useful for testing)."""
        self._local_pool.clear()
        self._remote_instances.clear()
        self._initialized = False
