import json
import logging
import os
import re
import asyncio
import aiofiles
from datetime import datetime
from typing import Any, Dict, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

from .config import settings
from .exceptions import MemoryError

from .memory_vector import VectorMemory

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
        self.vector_db_path = os.path.join(base_path, "vector_memory.json")
        self.salt_path = settings.vault_salt_path
        
        os.makedirs(self.history_path, exist_ok=True)
        os.makedirs(self.vault_path, exist_ok=True)
        
        # Initialize semantic memory
        self.vector_memory = VectorMemory(storage_path=self.vector_db_path)
        
        # Vault Session Key (In-memory only)
        self.vault_fernet = None
        self.last_unlock_time = None

        # Legacy encryption (from settings) - preserved for non-vault system data if any
        self.system_fernet = None
        if settings.encryption_key:
            try:
                self.system_fernet = Fernet(settings.encryption_key.encode())
            except Exception as e:
                logger.error(f"Failed to initialize system encryption: {e}")

    def is_vault_initialized(self) -> bool:
        """Check if a salt exists (meaning a password was set)."""
        return os.path.exists(self.salt_path)

    def is_vault_locked(self) -> bool:
        """Check if the vault is currently locked (no key in memory or expired)."""
        if self.vault_fernet is None:
            return True
            
        # 6-hour autolock check (Requirement 1.4)
        if self.last_unlock_time:
            elapsed = (datetime.now() - self.last_unlock_time).total_seconds()
            if elapsed > 6 * 3600:
                logger.warning("Privacy Vault session expired (6h). Auto-locking.")
                self.lock_vault()
                return True
                
        return False

    async def unlock_vault(self, password: str) -> bool:
        """Derive key from password and unlock the vault."""
        try:
            if not self.is_vault_initialized():
                # Initial setup: create salt
                salt = os.urandom(16)
                os.makedirs(os.path.dirname(self.salt_path), exist_ok=True)
                async with aiofiles.open(self.salt_path, 'wb') as f:
                    await f.write(salt)
            else:
                async with aiofiles.open(self.salt_path, 'rb') as f:
                    salt = await f.read()

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self.vault_fernet = Fernet(key)
            self.last_unlock_time = datetime.now()
            logger.info("Privacy Vault unlocked.")
            return True
        except Exception as e:
            logger.error(f"Failed to unlock vault: {e}")
            return False

    def lock_vault(self):
        """Purge the key from memory."""
        self.vault_fernet = None
        self.last_unlock_time = None
        logger.info("Privacy Vault locked.")

    async def destroy_vault(self):
        """WIPE everything if password is lost."""
        self.lock_vault()
        if os.path.exists(self.salt_path):
            os.remove(self.salt_path)
        
        for filename in os.listdir(self.vault_path):
            if filename.endswith(".vault"):
                os.remove(os.path.join(self.vault_path, filename))
        
        logger.warning("Privacy Vault DESTROYED and RESET.")

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
            
            # Index high-quality/important turns in long-term memory automatically if enabled
            if settings.log_level == "DEBUG" or "important" in str(turn).lower():
                await self.save_to_long_term_memory(turn.get("content", ""), {"session_id": session_id, "role": turn.get("role")})

        except Exception as e:
            logger.error(f"Error saving history: {e}")
            raise MemoryError(f"Failed to save history: {e}") from e

    async def save_to_long_term_memory(self, content: str, metadata: Dict[str, Any] | None = None):
        """Save a fact or snippet to the persistent vector memory."""
        if not content or len(content) < 5:
            return
        await self.vector_memory.add_memory(content, metadata)

    async def search_long_term_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve semantically similar memories from long-term storage."""
        results = await self.vector_memory.search(query, limit=limit)
        return [
            {
                "content": entry.content,
                "metadata": entry.metadata,
                "timestamp": entry.timestamp,
                "score": score
            }
            for entry, score in results
        ]

    async def save_to_vault(self, key: str, data: Any):
        """Save sensitive data to vault, encrypted with the session-based vault_fernet."""
        if self.is_vault_locked():
            raise MemoryError("Vault is locked. Unlock it first to save data.")
            
        filepath = os.path.join(self.vault_path, f"{key}.vault")
        try:
            json_data = json.dumps(data)
            encrypted_data = self.vault_fernet.encrypt(json_data.encode())
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Error saving to vault: {e}")
            raise MemoryError(f"Failed to save to vault: {e}") from e

    async def get_from_vault(self, key: str) -> Any:
        """Retrieve data from vault, decrypting with the session-based vault_fernet."""
        if self.is_vault_locked():
            raise MemoryError("Vault is locked. Unlock it first to read data.")

        filepath = os.path.join(self.vault_path, f"{key}.vault")
        if not os.path.exists(filepath):
            return None
            
        try:
            async with aiofiles.open(filepath, 'rb') as f:
                encrypted_data = await f.read()
            decrypted_data = self.vault_fernet.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
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
