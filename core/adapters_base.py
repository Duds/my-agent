from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ModelAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass
