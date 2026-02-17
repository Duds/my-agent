import json
import logging
import os
import torch
from typing import Any, Dict, List, Tuple
from sentence_transformers import SentenceTransformer, util
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    content: str
    metadata: Dict[str, Any]
    timestamp: str

class VectorMemory:
    """Simple JSON-backed vector memory using SentenceTransformers."""
    
    def __init__(self, storage_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.storage_path = storage_path
        self.model_name = model_name
        self._model: SentenceTransformer | None = None
        self.entries: List[MemoryEntry] = []
        self.embeddings: torch.Tensor | None = None
        self._should_reload_embeddings = True
        self._load_memory_metadata()
        logger.info("VectorMemory initialized (lazy) at %s", storage_path)

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the model on first access."""
        if self._model is None:
            logger.info("Loading SentenceTransformer model: %s...", self.model_name)
            self._model = SentenceTransformer(self.model_name)
            logger.info("Model %s loaded.", self.model_name)
        return self._model

    def _load_memory_metadata(self):
        """Load entries but don't compute embeddings yet."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.entries = [MemoryEntry(**e) for e in data.get("entries", [])]
                self._should_reload_embeddings = True
            except Exception as e:
                logger.error("Failed to load vector memory metadata: %s", e)

    def _ensure_embeddings(self):
        """Compute embeddings if they are missing or if entries changed."""
        if self.embeddings is None or self._should_reload_embeddings:
            if self.entries:
                logger.info("Computing embeddings for %d entries...", len(self.entries))
                texts = [e.content for e in self.entries]
                self.embeddings = self.model.encode(texts, convert_to_tensor=True)
                logger.info("Embeddings computed.")
            self._should_reload_embeddings = False

    def _save_memory(self):
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump({"entries": [asdict(e) for e in self.entries]}, f, indent=2)
        except Exception as e:
            logger.error("Failed to save vector memory: %s", e)

    async def add_memory(self, content: str, metadata: Dict[str, Any] | None = None):
        """Adds a new memory entry and updates the index."""
        self._ensure_embeddings()
        entry = MemoryEntry(
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        self.entries.append(entry)
        
        # Incremental update would be better, but for now we re-encode
        texts = [e.content for e in self.entries]
        self.embeddings = self.model.encode(texts, convert_to_tensor=True)
        self._save_memory()

    async def search(self, query: str, limit: int = 5, min_score: float = 0.3) -> List[Tuple[MemoryEntry, float]]:
        """Searches for similar memories."""
        self._ensure_embeddings()
        if not self.entries or self.embeddings is None:
            return []
            
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]
        
        top_results = torch.topk(cos_scores, k=min(limit, len(self.entries)))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            s = score.item()
            if s >= min_score:
                results.append((self.entries[idx], s))
                
        return results
