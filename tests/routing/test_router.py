import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.router import ModelRouter, Intent

class MockClient:
    def __init__(self, name):
        self.name = name

async def test_router():
    router = ModelRouter(local_client=MockClient("Ollama"), remote_clients={
        "anthropic": MockClient("Anthropic"),
        "moonshot": MockClient("Moonshot")
    })

    test_cases = [
        ("What is the capital of France?", "speed", "moonshot"),
        ("Write a complex python script to parse logs", "coding", "anthropic"),
        ("This is my private password", "private", "local_ollama"),
        ("Let's do some erotic roleplay", "nsfw", "local_ollama"),
        ("Explain the best investment strategy for wealth", "finance", "anthropic"),
    ]

    for text, expected_intent, expected_adapter in test_cases:
        routing = await router.route_request(text)
        print(f"Testing: '{text[:30]}...'")
        assert routing['intent'] == expected_intent, f"Expected {expected_intent}, got {routing['intent']}"
        assert routing['adapter'] == expected_adapter, f"Expected {expected_adapter}, got {routing['adapter']}"
        print(f"✅ Success: {routing['intent']} -> {routing['adapter']}")

if __name__ == "__main__":
    asyncio.run(test_router())
