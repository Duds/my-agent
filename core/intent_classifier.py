import logging
import torch
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer, util
from .schema import Intent

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Classifies user intent using semantic similarity with sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.classification_adapter = None
        # Predefined exemplars for each intent
        self.exemplars: Dict[Intent, List[str]] = {
            Intent.PRIVATE: [
                "show me my private keys",
                "what is my password",
                "save this secret note",
                "personal information and identity",
                "this is for my eyes only",
                "private data storage",
                "keep this confidential",
                "protect my secrets"
            ],
            Intent.NSFW: [
                "erotic roleplay and stories",
                "suggestive and intimate content",
                "unfiltered chat and characters",
                "sexy and flirty interaction",
                "explicit adult content",
                "provocative roleplay",
                "spicy encounter",
                "dirty talk"
            ],
            Intent.CODING: [
                "write a python script for automation",
                "debug this code snippet",
                "how to use react hooks in a component",
                "unit test for this specific function",
                "refactor this javascript module",
                "software development and programming",
                "write a rust function",
                "fix this bug",
                "programming help"
            ],
            Intent.FINANCE: [
                "track my monthly budget and spending",
                "stock market trends and analysis",
                "is this a good investment choice",
                "how much money do I have in accounts",
                "cryptocurrency price updates",
                "financial planning and taxes",
                "invest my savings"
            ],
            Intent.QUALITY: [
                "explain in great detail",
                "provide a comprehensive analysis",
                "mathematical proofs and complex logic",
                "deep dive into this topic",
                "thorough and high quality response"
            ]
        }
        
        # Pre-compute embeddings for exemplars
        self.exemplar_embeddings = {}
        for intent, texts in self.exemplars.items():
            self.exemplar_embeddings[intent] = self.model.encode(texts, convert_to_tensor=True)
            
        logger.info("IntentClassifier initialized with model: %s", model_name)

    def set_adapter(self, adapter):
        """Sets the LLM adapter for classification."""
        self.classification_adapter = adapter
        if adapter:
            logger.info("IntentClassifier now using LLM adapter for classification")
        else:
            logger.info("IntentClassifier reverted to local semantic classification")

    async def classify_with_llm(self, user_input: str) -> Tuple[Intent, float]:
        """Uses an LLM to classify intent for better accuracy/offloading."""
        if not self.classification_adapter:
            return self.classify(user_input)

        prompt = f"""
        Classify the following user input into exactly one of these categories:
        - PRIVATE: Request for secrets, passwords, or personal data storage.
        - NSFW: Erotic roleplay, suggestive content, or adult themes.
        - CODING: Programming help, debugging, or script writing.
        - FINANCE: Budgeting, investments, or financial planning.
        - QUALITY: Requests for deep analysis, long explanations, or complex logic.
        - SPEED: Simple questions or brief requests.

        USER INPUT: {user_input}

        Respond ONLY with the category name.
        """
        try:
            response = await self.classification_adapter.generate(prompt)
            result = response.strip().upper()
            for intent in Intent:
                if intent.value.upper() in result:
                    return intent, 0.95
            return Intent.SPEED, 0.5
        except Exception as e:
            logger.error(f"LLM Classification failed: {e}. Falling back to local.")
            return self.classify(user_input)

    def classify(self, user_input: str, threshold: float = 0.4) -> Tuple[Intent, float]:
        """Classifies user input into an Intent and returns confidence score."""
        if not user_input.strip():
            return Intent.SPEED, 1.0

        # Encode user input
        input_embedding = self.model.encode(user_input, convert_to_tensor=True)
        
        best_intent = None
        max_score = -1.0
        
        for intent, embeddings in self.exemplar_embeddings.items():
            # Compute cosine similarity between input and all exemplars for this intent
            cos_scores = util.cos_sim(input_embedding, embeddings)[0]
            # Take the maximum similarity score for this intent
            intent_score = torch.max(cos_scores).item()
            
            if intent_score > max_score:
                max_score = intent_score
                best_intent = intent
        
        # If confidence is too low, fall back to basic heuristics (SPEED or QUALITY)
        if max_score < threshold:
            logger.debug("Low confidence (%.2f) for intent classification. Falling back to length-based heuristic.", max_score)
            if len(user_input) > 200:
                return Intent.QUALITY, 0.5
            return Intent.SPEED, 0.5
            
        return best_intent, max_score
