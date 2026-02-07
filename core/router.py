import enum
import logging
from typing import Any, AsyncIterator, Dict, List, Tuple

from .adapters_base import ModelAdapter
from .factory import AdapterFactory
from .security import SecurityValidator

logger = logging.getLogger(__name__)


class Intent(enum.Enum):
    SPEED = "speed"
    QUALITY = "quality"
    PRIVATE = "private"
    NSFW = "nsfw"
    CODING = "coding"
    FINANCE = "finance"

class ModelRouter:
    """Routes requests to appropriate adapters. Reuses adapter instances from factory."""

    def __init__(
        self,
        local_client: ModelAdapter,
        adapter_factory: AdapterFactory,
        security_validator: SecurityValidator | None = None,
        available_models: List[str] | None = None,
    ):
        self.local_client = local_client
        self.adapter_factory = adapter_factory
        self.security_validator = security_validator
        self.available_models = available_models or []
        logger.info("ModelRouter initialized with %d local models", len(self.available_models))

    async def classify_intent(self, user_input: str) -> Intent:
        # Initial implementation uses simple keyword matching or a cheap local model
        input_lower = user_input.lower()
        if any(w in input_lower for w in ["secret", "private", "personal", "password"]):
            return Intent.PRIVATE
        nsfw_keywords = [
            "roleplay", "nsfw", "erp", "erotic", "sexual", "intimate", "sexy", "flirty",
            "pussy", "cunt", "cock", "dick", "vagina", "penis", "orgasm", "foreplay",
        ]
        if any(w in input_lower for w in nsfw_keywords):
            return Intent.NSFW
        if any(w in input_lower for w in ["code", "python", "script", "test"]):
            return Intent.CODING
        if any(w in input_lower for w in ["money", "stock", "invest", "wealth", "budget"]):
            return Intent.FINANCE
        return Intent.QUALITY if len(user_input) > 100 else Intent.SPEED

    def _find_best_local_model(self, keywords: List[str], default: str) -> str:
        """Finds the first available model matching any keyword, or returns default."""
        for kw in keywords:
            for model in self.available_models:
                if kw in model.lower():
                    return model
        return default

    def _resolve_model_to_adapter(self, model_id: str) -> "ModelAdapter | None":
        """Resolve model_id to adapter (Ollama or remote)."""
        # Try remote first
        remote_adapter = self.adapter_factory.get_remote_adapter(model_id)
        if remote_adapter:
            return remote_adapter
        
        # Legacy mapping for Sonnet/Moonshot explicitly
        if model_id in ("claude-sonnet", "anthropic"):
            return self.adapter_factory.get_remote_adapter("anthropic")
        if model_id in ("moonshot-v1", "moonshot"):
            return self.adapter_factory.get_remote_adapter("moonshot")
        if model_id in ("mistral-small", "mistral"):
            return self.adapter_factory.get_remote_adapter("mistral")

        # Fallback to local
        return self.adapter_factory.get_local_adapter(model_id)

    async def route_request(
        self,
        user_input: str,
        model_id: str | None = None,
        mode_id: str | None = None,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        intent = await self.classify_intent(user_input)

        # NSFW/PRIVATE always route to local uncensored models—ignore model_id override
        if intent in [Intent.PRIVATE, Intent.NSFW] or mode_id == "private":
            model_name = self._find_best_local_model(
                ["hermes", "dolphin", "roleplay"], default="hermes-roleplay:latest"
            )
            adapter_name = model_name
            adapter = self.adapter_factory.get_local_adapter(model_name)
            answer = await adapter.generate(user_input)
            return {
                "intent": intent.value,
                "adapter": adapter_name,
                "answer": answer,
                "model_info": adapter.get_model_info(),
                "requires_privacy": True,
                "security": {"is_safe": True},
            }

        if model_id:
            adapter = self._resolve_model_to_adapter(model_id)
            if adapter:
                answer = await adapter.generate(user_input)
                security_verdict = {"is_safe": True}
                
                all_remotes = self.adapter_factory.get_all_remote_adapters()
                is_remote = any(provider in model_id.lower() for provider in all_remotes.keys())
                
                if self.security_validator and not is_remote:
                    security_verdict = await self.security_validator.check_output(user_input, answer)
                if not security_verdict["is_safe"]:
                    answer = f"[SECURITY BLOCK] {security_verdict['reason']}"
                return {
                    "intent": "manual",
                    "adapter": model_id,
                    "answer": answer,
                    "model_info": adapter.get_model_info(),
                    "requires_privacy": False,
                    "security": security_verdict,
                }

        if intent == Intent.CODING:
            model_name = self._find_best_local_model(
                ["deepseek-coder", "codellama", "qwen-coder", "code"],
                default="codellama:7b-instruct",
            )
            adapter_name = model_name
            adapter = self.adapter_factory.get_local_adapter(model_name)

        elif intent == Intent.QUALITY:
            anthropic_adapter = self.adapter_factory.get_remote_adapter("anthropic")
            if anthropic_adapter and mode_id != "private":
                adapter_name = "anthropic"
                adapter = anthropic_adapter
            else:
                model_name = self._find_best_local_model(
                    ["hermes", "llama3", "mistral", "mixtral", "gemma"], default="hermes-roleplay:latest"
                )
                adapter_name = model_name
                adapter = self.adapter_factory.get_local_adapter(model_name)

        elif intent == Intent.SPEED:
            mistral_adapter = self.adapter_factory.get_remote_adapter("mistral")
            if mistral_adapter and mode_id != "private":
                adapter_name = "mistral"
                adapter = mistral_adapter
            else:
                model_name = self._find_best_local_model(
                    ["mistral", "gemma", "phi", "tiny", "llama3"], default="mistral:latest"
                )
                adapter_name = model_name
                adapter = self.adapter_factory.get_local_adapter(model_name)

        else:
            adapter_name = "local-default"
            adapter = self.local_client
        
        # Actually generate the response
        answer = await adapter.generate(user_input)

        # Security check for remote models (Trust but Verify)
        security_verdict = {"is_safe": True}
        if intent not in [Intent.PRIVATE, Intent.NSFW] and self.security_validator:
            security_verdict = await self.security_validator.check_output(user_input, answer)
            if not security_verdict["is_safe"]:
                answer = f"[SECURITY BLOCK] {security_verdict['reason']}"

        return {
            "intent": intent.value,
            "adapter": adapter_name,
            "answer": answer,
            "model_info": adapter.get_model_info(),
            "requires_privacy": intent in [Intent.PRIVATE, Intent.NSFW],
            "security": security_verdict
        }

    async def route_request_stream(
        self,
        user_input: str,
        model_id: str | None = None,
        mode_id: str | None = None,
    ) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        """
        Stream response chunks for Ollama models. Yields (chunk, metadata).
        """
        adapter: ModelAdapter | None = None
        adapter_name: str = ""
        routing_meta: Dict[str, Any] = {}

        intent = await self.classify_intent(user_input)

        # NSFW/PRIVATE always route to local uncensored models—ignore model_id override
        if intent in [Intent.PRIVATE, Intent.NSFW] or mode_id == "private":
            model_name = self._find_best_local_model(
                ["hermes", "dolphin", "roleplay"], default="hermes-roleplay:latest"
            )
            adapter_name = model_name
            adapter = self.adapter_factory.get_local_adapter(model_name)
            routing_meta = {
                "intent": intent.value,
                "adapter": adapter_name,
                "requires_privacy": True,
            }
        elif model_id:
            adapter = self._resolve_model_to_adapter(model_id)
            adapter_name = model_id
            routing_meta = {
                "intent": "manual",
                "adapter": adapter_name,
                "requires_privacy": False,
            }
        else:
            if intent == Intent.CODING:
                model_name = self._find_best_local_model(
                    ["deepseek-coder", "codellama", "qwen-coder", "code"],
                    default="codellama:7b-instruct",
                )
                adapter_name = model_name
                adapter = self.adapter_factory.get_local_adapter(model_name)
            elif intent == Intent.QUALITY:
                anthropic_adapter = self.adapter_factory.get_remote_adapter("anthropic")
                mistral_adapter = self.adapter_factory.get_remote_adapter("mistral")
                if anthropic_adapter and mode_id != "private":
                    adapter_name = "anthropic"
                    adapter = anthropic_adapter
                elif mistral_adapter and mode_id != "private":
                    adapter_name = "mistral"
                    adapter = mistral_adapter
                else:
                    model_name = self._find_best_local_model(
                        ["hermes", "llama3", "mistral", "mixtral", "gemma"], default="hermes-roleplay:latest"
                    )
                    adapter_name = model_name
                    adapter = self.adapter_factory.get_local_adapter(model_name)
            elif intent == Intent.SPEED:
                mistral_adapter = self.adapter_factory.get_remote_adapter("mistral")
                if mistral_adapter and mode_id != "private":
                    adapter_name = "mistral"
                    adapter = mistral_adapter
                else:
                    model_name = self._find_best_local_model(
                        ["mistral", "gemma", "phi", "tiny", "llama3"], default="mistral:latest"
                    )
                    adapter_name = model_name
                    adapter = self.adapter_factory.get_local_adapter(model_name)
            else:
                adapter_name = "local-default"
                adapter = self.local_client

            routing_meta = {
                "intent": intent.value,
                "adapter": adapter_name,
                "requires_privacy": intent in [Intent.PRIVATE, Intent.NSFW],
            }

        if not adapter:
            yield ("[ERROR] No adapter available", routing_meta)
            return

        from .adapters_local import OllamaAdapter
        if isinstance(adapter, OllamaAdapter) and hasattr(adapter, "generate_stream"):
            async for chunk in adapter.generate_stream(user_input):
                yield (chunk, routing_meta)
        else:
            answer = await adapter.generate(user_input)
            yield (answer, routing_meta)
