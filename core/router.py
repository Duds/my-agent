import enum
import logging
from typing import Any, AsyncIterator, Dict, List, Tuple

from .adapters_base import ModelAdapter
from .factory import AdapterFactory
from .security import SecurityValidator
from .memory import MemorySystem
from .exceptions import AdapterError
from .schema import Intent
from .intent_classifier import IntentClassifier
import json
import os

logger = logging.getLogger(__name__)




class ModelRouter:
    """Routes requests to appropriate adapters. Reuses adapter instances from factory."""

    def __init__(
        self,
        local_client: ModelAdapter,
        adapter_factory: AdapterFactory,
        security_validator: SecurityValidator | None = None,
        available_models: List[str] | None = None,
        memory_system: MemorySystem | None = None,
    ):
        self.local_client = local_client
        self.adapter_factory = adapter_factory
        self.security_validator = security_validator
        self.available_models = available_models or []
        self.memory_system = memory_system
        self.intent_classifier = IntentClassifier()
        self.pii_redactor = None # Initialized by set_pii_redactor
        self._load_routing_config()
        logger.info("ModelRouter initialized with %d local models and Task-Specific Routing", len(self.available_models))

    def _load_routing_config(self):
        """Loads task-specific model assignments from config."""
        from .config import settings
        self.routing_config = {}
        if os.path.exists(settings.routing_config_path):
            try:
                with open(settings.routing_config_path, "r") as f:
                    self.routing_config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load routing config: {e}")
        
        # Apply initial config
        self._apply_routing_config()

    def _apply_routing_config(self):
        """Applies task assignments to classifier and security judge."""
        # Intent Classifier
        classifier_model = self.routing_config.get("intent_classification")
        if classifier_model:
            adapter = self._resolve_model_to_adapter(classifier_model)
            self.intent_classifier.set_adapter(adapter)
        
        # Security Validator
        security_model = self.routing_config.get("security_judge")
        if security_model and self.security_validator:
            adapter = self._resolve_model_to_adapter(security_model)
            self.security_validator.set_judge_adapter(adapter)

        # PII Redactor
        pii_model = self.routing_config.get("pii_redactor")
        if pii_model:
            from .security import PIIRedactor
            adapter = self._resolve_model_to_adapter(pii_model)
            if not self.pii_redactor:
                self.pii_redactor = PIIRedactor(adapter)
            else:
                self.pii_redactor.set_adapter(adapter)

    def update_config(self, new_config: dict):
        """Updates and persists new routing configuration."""
        from .config import settings
        self.routing_config.update(new_config)
        os.makedirs(os.path.dirname(settings.routing_config_path), exist_ok=True)
        try:
            with open(settings.routing_config_path, "w") as f:
                json.dump(self.routing_config, f, indent=2)
            self._apply_routing_config()
        except Exception as e:
            logger.error(f"Failed to save routing config: {e}")

    async def classify_intent(self, user_input: str) -> Intent:
        """Enhanced intent classification using semantic similarity or LLM."""
        intent, confidence = await self.intent_classifier.classify_with_llm(user_input)
        logger.info("Classified intent: %s (confidence: %.2f)", intent.value, confidence)
        return intent

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
        
        # Load context if session_id is provided
        context = []
        if session_id and self.memory_system:
            context = await self.memory_system.get_context(session_id)

        # NSFW/PRIVATE always route to local uncensored models—ignore model_id override
        if intent in [Intent.PRIVATE, Intent.NSFW] or mode_id == "private":
            model_name = self._find_best_local_model(
                ["hermes", "dolphin", "roleplay"], default="hermes-roleplay:latest"
            )
            adapter_name = model_name
            adapter = self.adapter_factory.get_local_adapter(model_name)
            try:
                answer = await adapter.generate(user_input)
            except AdapterError as e:
                logger.error(f"Private/NSFW route failed: {e}")
                answer = f"Error generating private response: {e}"
            
            result = {
                "intent": intent.value,
                "adapter": adapter_name,
                "answer": answer,
                "model_info": adapter.get_model_info(),
                "requires_privacy": True,
                "security": {"is_safe": True},
            }
            if session_id and self.memory_system:
                await self.memory_system.save_chat_turn(session_id, {"role": "user", "content": user_input})
                await self.memory_system.save_chat_turn(session_id, {"role": "assistant", "content": answer})
            return result

        adapter = None
        adapter_name = "local-default"

        if model_id:
            adapter = self._resolve_model_to_adapter(model_id)
            adapter_name = model_id
        elif intent == Intent.CODING:
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
        
        if not adapter:
            adapter = self.local_client
            adapter_name = "local-default"

        try:
            answer = await adapter.generate(user_input)
        except AdapterError as e:
            logger.warning(f"Primary adapter {adapter_name} failed: {e}. Falling back to local.")
            adapter = self.local_client
            adapter_name = f"fallback-{adapter_name}"
            try:
                answer = await adapter.generate(user_input)
            except Exception as fe:
                logger.error(f"Fallback also failed: {fe}")
                answer = f"Sorry, both primary and fallback models failed: {e}"

        # Security check for remote models (Trust but Verify)
        security_verdict = {"is_safe": True}
        if intent not in [Intent.PRIVATE, Intent.NSFW] and self.security_validator:
            security_verdict = await self.security_validator.check_output(user_input, answer)
            if not security_verdict["is_safe"]:
                answer = f"[SECURITY BLOCK] {security_verdict['reason']}"

        # PII Redaction
        if security_verdict["is_safe"] and self.pii_redactor:
            answer = await self.pii_redactor.redact(answer)

        if session_id and self.memory_system:
            await self.memory_system.save_chat_turn(session_id, {"role": "user", "content": user_input})
            await self.memory_system.save_chat_turn(session_id, {"role": "assistant", "content": answer})

        return {
            "intent": intent.value if intent else "unknown",
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
