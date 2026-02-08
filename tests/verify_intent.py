import asyncio
import logging
from core.intent_classifier import IntentClassifier
from core.schema import Intent

logging.basicConfig(level=logging.INFO)

async def test_classification():
    classifier = IntentClassifier()
    
    test_cases = {
        "Can you help me write a rust function to parse JSON?": Intent.CODING,
        "What's the best way to invest my savings for long term?": Intent.FINANCE,
        "Please keep this note private, it contains my passwords.": Intent.PRIVATE,
        "Tell me a spicy story about a secret encounter.": Intent.NSFW,
        "Hi there, how are you?": Intent.SPEED,
        "Explain the theory of relativity in great detail with mathematical proofs.": Intent.QUALITY,
    }
    
    print("\n--- Intent Classification Test Results ---\n")
    passed = 0
    for query, expected in test_cases.items():
        intent, confidence = classifier.classify(query)
        result = "PASS" if intent == expected else "FAIL"
        if result == "PASS": passed += 1
        print(f"Query: {query}")
        print(f"Expected: {expected.value}, Got: {intent.value} (Confidence: {confidence:.2f}) -> {result}\n")
    
    print(f"Summary: {passed}/{len(test_cases)} passed.")

if __name__ == "__main__":
    asyncio.run(test_classification())
