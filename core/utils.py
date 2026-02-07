"""Utility functions for the MyAgent platform."""

import asyncio
import functools
import logging
import random
from typing import Any, Callable, Type, Tuple, Union

logger = logging.getLogger(__name__)

def retry(
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]],
    tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: bool = True
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        exceptions: Exception(s) to catch and retry.
        tries: Maximum number of attempts.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier.
        jitter: Whether to add random jitter to the delay.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            m_tries, m_delay = tries, delay
            while m_tries > 1:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    wait = m_delay
                    if jitter:
                        wait *= (0.5 + random.random())
                    
                    logger.warning(
                        f"Retryable error in {func.__name__}: {e}. "
                        f"Retrying in {wait:.2f}s... ({m_tries-1} attempts left)"
                    )
                    await asyncio.sleep(wait)
                    m_tries -= 1
                    m_delay *= backoff
            
            # Last attempt
            return await func(*args, **kwargs)
        return wrapper
    return decorator
