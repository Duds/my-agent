import pytest
import os
import json
import torch
from unittest.mock import MagicMock, patch
from core.memory_vector import VectorMemory, MemoryEntry

@pytest.fixture
def mock_transformer():
    with patch('core.memory_vector.SentenceTransformer') as mock:
        instance = mock.return_value
        # Mock encode to return a random tensor of size (n, 384)
        def side_effect(texts, **kwargs):
            if isinstance(texts, str):
                return torch.randn(384)
            return torch.randn(len(texts), 384)
        instance.encode.side_effect = side_effect
        yield instance

@pytest.fixture
def vector_memory(tmp_path, mock_transformer):
    storage_path = str(tmp_path / "vector_memory.json")
    return VectorMemory(storage_path=storage_path)

@pytest.mark.asyncio
async def test_add_and_search(vector_memory):
    await vector_memory.add_memory("The quick brown fox", {"type": "animal"})
    await vector_memory.add_memory("Jumps over the lazy dog", {"type": "animal"})
    
    # Mocking similarity for testing search logic
    # Since embeddings are random, we'll just verify it returns something
    results = await vector_memory.search("fox", limit=1, min_score=-2.0)
    assert len(results) == 1
    assert isinstance(results[0][0], MemoryEntry)
    assert results[0][1] >= -1.0 # Cosine similarity range

@pytest.mark.asyncio
async def test_persistence(tmp_path, mock_transformer):
    storage_path = str(tmp_path / "persist_test.json")
    vm1 = VectorMemory(storage_path=storage_path)
    await vm1.add_memory("Persistent fact", {"id": 1})
    
    # Load into new instance
    vm2 = VectorMemory(storage_path=storage_path)
    assert len(vm2.entries) == 1
    assert vm2.entries[0].content == "Persistent fact"

@pytest.mark.asyncio
async def test_search_empty(vector_memory):
    results = await vector_memory.search("anything")
    assert results == []
