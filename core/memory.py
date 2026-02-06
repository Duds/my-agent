import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Session ID must be alphanumeric, hyphen, underscore only (prevent path traversal)
SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_session_id(session_id: str) -> bool:
    """Validate session_id to prevent path traversal attacks."""
    if not session_id or len(session_id) > 64:
        return False
    return bool(SESSION_ID_PATTERN.match(session_id))


class MemorySystem:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.history_path = os.path.join(base_path, "history")
        self.vault_path = os.path.join(base_path, "vault") # For sensitive data
        
        os.makedirs(self.history_path, exist_ok=True)
        os.makedirs(self.vault_path, exist_ok=True)

    def save_chat_turn(self, session_id: str, turn: Dict[str, Any]):
        if not _validate_session_id(session_id):
            raise ValueError(f"Invalid session_id: {session_id!r}")
        filename = f"{session_id}.json"
        filepath = os.path.join(self.history_path, filename)
        
        history = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                history = json.load(f)
        
        history.append({
            "timestamp": datetime.now().isoformat(),
            **turn
        })
        
        with open(filepath, 'w') as f:
            json.dump(history, f, indent=2)

    def save_to_vault(self, key: str, data: Any):
        # In a real implementation, this would be encrypted
        # For now, we store in a separate directory marked in rules as "Sensitive"
        filepath = os.path.join(self.vault_path, f"{key}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def get_context(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not _validate_session_id(session_id):
            return []
        filepath = os.path.join(self.history_path, f"{session_id}.json")
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r') as f:
            history = json.load(f)
            return history[-limit:]
