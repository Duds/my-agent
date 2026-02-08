from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ModelAdapter(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        model_override: Optional[str] = None,
    ) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass
