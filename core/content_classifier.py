"""
Content Classifier (PBI-042).

LLM or rule-based inspection of file contents to produce labels or
suggested destination for auto-sorting. Integrates with File Watchdog output.
"""

import logging
import os
from pathlib import Path

from .config import settings

logger = logging.getLogger(__name__)

# Rule-based extension -> category mapping (MVP)
_EXTENSION_CATEGORIES: dict[str, str] = {
    ".txt": "Documents",
    ".md": "Documents",
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".rtf": "Documents",
    ".csv": "Spreadsheets",
    ".xls": "Spreadsheets",
    ".xlsx": "Spreadsheets",
    ".json": "Data",
    ".xml": "Data",
    ".yaml": "Data",
    ".yml": "Data",
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".tsx": "Code",
    ".jsx": "Code",
    ".html": "Code",
    ".css": "Code",
    ".sh": "Code",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".mp4": "Video",
    ".mov": "Video",
    ".zip": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
}


def classify(path: str, content_snippet: str | None = None) -> dict:
    """
    Classify a file and return suggested category and destination.

    Args:
        path: File path.
        content_snippet: Optional content for LLM classification (future use).

    Returns:
        {"category": str, "suggested_destination": str | None}
    """
    if not path or not path.strip():
        return {"category": "Unknown", "suggested_destination": None}

    ext = Path(path).suffix.lower()
    category = _EXTENSION_CATEGORIES.get(ext, "Other")
    # MVP: suggest folder name from category
    suggested = f"~/Documents/{category}" if category != "Other" else None

    # Future: use content_snippet + LLM for finer classification
    if content_snippet and settings.content_classifier_model:
        # Placeholder for LLM integration
        pass

    return {
        "category": category,
        "suggested_destination": os.path.expanduser(suggested) if suggested else None,
    }
