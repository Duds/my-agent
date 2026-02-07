import enum
import logging
from typing import Any, Dict, List

from .adapters_base import ModelAdapter
from .adapters_local import OllamaAdapter
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
    """Routes requests to appropriate adapters. Reuses adapter instances from pool."""

    def __init__(
        self,
        local_client: ModelAdapter,
        remote_clients: Dict[str, ModelAdapter],
        security_validator: SecurityValidator | None = None,
        available_models: List[str] | None = None,
    ):
        self.local_client = local_client
        self.remote_clients = remote_clients
        self.security_validator = security_validator
        self.available_models = available_models or []
        # Adapter pool: reuse OllamaAdapter instances by model_name
        self._local_adapter_pool: Dict[str, OllamaAdapter] = {}
        logger.info("ModelRouter initialized with %d local models", len(self.available_models))

    async def classify_intent(self, user_input: str) -> Intent:
        # Initial implementation uses simple keyword matching or a cheap local model
        # In a full implementation, this would be a separate (local) call
        input_lower = user_input.lower()
        if any(w in input_lower for w in ["secret", "private", "personal", "password"]):
            return Intent.PRIVATE
        if any(w in input_lower for w in ["roleplay", "nsfw", "erp"]):
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

    def _get_local_adapter(self, model_name: str) -> OllamaAdapter:
        """Get or create cached OllamaAdapter for model_name."""
        if model_name not in self._local_adapter_pool:
            self._local_adapter_pool[model_name] = OllamaAdapter(model_name=model_name)
        return self._local_adapter_pool[model_name]

    def _resolve_model_to_adapter(self, model_id: str) -> "ModelAdapter | None":
        """Resolve model_id to adapter (Ollama or remote)."""
        if model_id in ("claude-sonnet", "anthropic") and "anthropic" in self.remote_clients:
            return self.remote_clients["anthropic"]
        if model_id in ("moonshot-v1", "moonshot") and "moonshot" in self.remote_clients:
            return self.remote_clients["moonshot"]
        # Ollama model
        if model_id in (self.available_models or []):
            return self._get_local_adapter(model_id)
        return self._get_local_adapter(model_id)

    async def route_request(
        self,
        user_input: str,
        model_id: str | None = None,
        mode_id: str | None = None,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        # Manual override: when model_id provided, bypass intent routing
        if model_id:
            adapter = self._resolve_model_to_adapter(model_id)
            if adapter:
                answer = await adapter.generate(user_input)
                security_verdict = {"is_safe": True}
                if self.security_validator and "anthropic" not in str(model_id) and "moonshot" not in str(model_id):
                    security_verdict = await self.security_validator.check_output(user_input, answer)
                    if not security_verdict["is_safe"]:
                        answer = f"[SECURITY BLOCK] {security_verdict['reason']}"
                return {
                    "intent": "manual",
                    "adapter": model_id,
                    "answer": answer,
                    "model_info": adapter.get_model_info() if hasattr(adapter, "get_model_info") else {"type": "unknown"},
                    "requires_privacy": mode_id == "private" if mode_id else False,
                    "security": security_verdict,
                }

        intent = await self.classify_intent(user_input)

        # Route based on intent with specialized models (reuse adapters from pool)
        if intent in [Intent.PRIVATE, Intent.NSFW]:
            model_name = self._find_best_local_model(
                ["hermes", "dolphin", "roleplay"], default="hermes-roleplay:latest"
            )
            adapter_name = model_name
            adapter = self._get_local_adapter(model_name)

        elif intent == Intent.CODING:
            model_name = self._find_best_local_model(
                ["deepseek-coder", "codellama", "qwen-coder", "code"],
                default="codellama:7b-instruct",
            )
            adapter_name = model_name
            adapter = self._get_local_adapter(model_name)

        elif intent == Intent.QUALITY:
            if "anthropic" in self.remote_clients:
                adapter_name = "anthropic"
                adapter = self.remote_clients["anthropic"]
            else:
                model_name = self._find_best_local_model(
                    ["llama3", "mistral", "mixtral", "gemma"], default="llama3:latest"
                )
                adapter_name = model_name
                adapter = self._get_local_adapter(model_name)

        elif intent == Intent.SPEED:
            model_name = self._find_best_local_model(
                ["mistral", "gemma", "phi", "tiny", "llama3"], default="mistral:latest"
            )
            adapter_name = model_name
            adapter = self._get_local_adapter(model_name)

        else:
            adapter_name = "llama3:latest"
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
            "model_info": adapter.get_model_info() if hasattr(adapter, 'get_model_info') else {"type": "unknown"},
            "requires_privacy": intent in [Intent.PRIVATE, Intent.NSFW],
            "security": security_verdict
        }
