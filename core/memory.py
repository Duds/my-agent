import json
import logging
import os
import re
import asyncio
import aiofiles
from datetime import datetime
from typing import Any, Dict, List
from cryptography.fernet import Fernet
from .config import settings
from .exceptions import MemoryError

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
        self.vault_path = os.path.join(base_path, "vault")
        
        os.makedirs(self.history_path, exist_ok=True)
        os.makedirs(self.vault_path, exist_ok=True)
        
        # Initialize encryption
        self.fernet = None
        if settings.encryption_key:
            try:
                self.fernet = Fernet(settings.encryption_key.encode())
            except Exception as e:
                logger.error(f"Failed to initialize encryption: {e}")
        else:
            logger.warning("No encryption key found in settings. Vault data will NOT be encrypted.")

    async def save_chat_turn(self, session_id: str, turn: Dict[str, Any]):
        if not _validate_session_id(session_id):
            raise MemoryError(f"Invalid session_id: {session_id!r}")
        filename = f"{session_id}.json"
        filepath = os.path.join(self.history_path, filename)
        
        history = []
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r') as f:
                    content = await f.read()
                    if content:
                        history = json.loads(content)
        except Exception as e:
            logger.error(f"Error reading history: {e}")
            # Continue with empty history if file is corrupt
        
        history.append({
            "timestamp": datetime.now().isoformat(),
            **turn
        })
        
        try:
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(json.dumps(history, indent=2))
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            raise MemoryError(f"Failed to save history: {e}") from e

    async def save_to_vault(self, key: str, data: Any):
        """Save sensitive data to vault, encrypted if key is available."""
        filepath = os.path.join(self.vault_path, f"{key}.vault")
        try:
            json_data = json.dumps(data)
            if self.fernet:
                encrypted_data = self.fernet.encrypt(json_data.encode())
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(encrypted_data)
            else:
                async with aiofiles.open(filepath, 'w') as f:
                    await f.write(json_data)
        except Exception as e:
            logger.error(f"Error saving to vault: {e}")
            raise MemoryError(f"Failed to save to vault: {e}") from e

    async def get_from_vault(self, key: str) -> Any:
        """Retrieve data from vault, decrypting if necessary."""
        filepath = os.path.join(self.vault_path, f"{key}.vault")
        if not os.path.exists(filepath):
            return None
            
        try:
            if self.fernet:
                async with aiofiles.open(filepath, 'rb') as f:
                    encrypted_data = await f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                return json.loads(decrypted_data)
            else:
                async with aiofiles.open(filepath, 'r') as f:
                    content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Error reading from vault: {e}")
            raise MemoryError(f"Failed to read from vault: {e}") from e

    async def get_context(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not _validate_session_id(session_id):
            return []
        filepath = os.path.join(self.history_path, f"{session_id}.json")
        if not os.path.exists(filepath):
            return []
        
        try:
            async with aiofiles.open(filepath, 'r') as f:
                content = await f.read()
                if not content:
                    return []
                history = json.loads(content)
                return history[-limit:]
        except Exception as e:
            logger.error(f"Error reading context: {e}")
            return []
