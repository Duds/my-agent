"""Custom exceptions for the MyAgent platform."""

class MyAgentException(Exception):
    """Base exception for all MyAgent errors."""
    pass

class AdapterError(MyAgentException):
    """Raised when an LLM adapter fails (e.g., API error, timeout)."""
    pass

class SecurityError(MyAgentException):
    """Raised when a security validation fails or blocked."""
    pass

class MemoryError(MyAgentException):
    """Raised when memory operations (history, vault) fail."""
    pass

class ConfigError(MyAgentException):
    """Raised when configuration is invalid or missing."""
    pass

class AuthenticationError(MyAgentException):
    """Raised when API authentication fails."""
    pass
