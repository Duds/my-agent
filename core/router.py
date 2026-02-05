import enum
from typing import List, Dict, Any
from .adapters_base import ModelAdapter
from .adapters_local import OllamaAdapter
from .security import SecurityValidator

class Intent(enum.Enum):
    SPEED = "speed"
    QUALITY = "quality"
    PRIVATE = "private"
    NSFW = "nsfw"
    CODING = "coding"
    FINANCE = "finance"

class ModelRouter:
    def __init__(self, local_client, remote_clients: Dict[str, Any], security_validator: SecurityValidator = None):
        self.local_client = local_client
        self.remote_clients = remote_clients
        self.security_validator = security_validator

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

    async def get_adapter(self, intent: Intent) -> str:
        if intent in [Intent.PRIVATE, Intent.NSFW]:
            return "local_ollama"
        if intent == Intent.SPEED:
            return "moonshot"
        if intent in [Intent.CODING, Intent.QUALITY, Intent.FINANCE]:
            return "anthropic"
        return "local_ollama"

    async def route_request(self, user_input: str) -> Dict[str, Any]:
        intent = await self.classify_intent(user_input)
        
        # Route based on intent with specialized models
        if intent in [Intent.PRIVATE, Intent.NSFW]:
            adapter_name = "hermes-roleplay:latest"
            adapter = OllamaAdapter(model_name="hermes-roleplay:latest")
        elif intent == Intent.CODING:
            adapter_name = "codellama:7b-instruct"
            adapter = OllamaAdapter(model_name="codellama:7b-instruct")
        elif intent == Intent.QUALITY:
            adapter_name = "anthropic"
            adapter = self.remote_clients.get("anthropic", self.local_client)
        elif intent == Intent.SPEED:
            adapter_name = "mistral:latest"
            adapter = OllamaAdapter(model_name="mistral:latest")
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
