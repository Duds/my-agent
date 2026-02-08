"""
Model metadata registry: pros, cons, benefits, and tags for informed model selection.
Merged into /api/models response so the UI can display help text and filter by tag.
"""

import json
from pathlib import Path
from typing import Any

_METADATA_PATH = Path(__file__).parent / "model_metadata.json"
_CACHE: dict[str, Any] | None = None


def _load_metadata() -> dict[str, Any]:
    """Load model metadata from JSON. Cached for performance."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not _METADATA_PATH.exists():
        _CACHE = {"models": {}, "ollama_patterns": []}
        return _CACHE
    with open(_METADATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    _CACHE = {
        "models": data.get("models", {}),
        "ollama_patterns": sorted(
            data.get("ollama_patterns", []),
            key=lambda p: len(p.get("pattern", "")),
            reverse=True,
        ),
    }
    return _CACHE


def get_metadata_for_model(model_id: str, model_type: str) -> dict[str, Any]:
    """
    Return metadata (tags, pros, cons, benefits) for a model.
    - Commercial: exact match on model_id
    - Ollama: match by pattern (most specific first)
    """
    meta = _load_metadata()
    models = meta["models"]
    patterns = meta["ollama_patterns"]

    if model_type == "commercial" and model_id in models:
        return models[model_id].copy()

    if model_type == "ollama":
        model_lower = model_id.lower()
        for entry in patterns:
            pattern = entry.get("pattern", "").lower()
            if pattern in model_lower or model_lower.startswith(pattern + ":") or model_lower.startswith(pattern + "."):
                return {
                    "tags": entry.get("tags", []),
                    "pros": entry.get("pros", []),
                    "cons": entry.get("cons", []),
                    "benefits": entry.get("benefits", ""),
                }

    return {}


def merge_metadata_into_model(
    model: dict[str, Any],
    model_id: str,
    model_type: str,
) -> dict[str, Any]:
    """Merge tags, pros, cons, benefits into a model dict. Mutates and returns."""
    md = get_metadata_for_model(model_id, model_type)
    if md:
        model["tags"] = md.get("tags", [])
        model["pros"] = md.get("pros", [])
        model["cons"] = md.get("cons", [])
        model["benefits"] = md.get("benefits", "")
    else:
        model["tags"] = []
        model["pros"] = []
        model["cons"] = []
        model["benefits"] = ""
    return model
