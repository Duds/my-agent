"""
Context Poller Service (PBI-056).

Background daemon that detects active window/process contexts on macOS
and feeds the ContextDisplay component via GET /api/context.

Uses osascript (zero extra dependencies) on macOS; returns null on other platforms.
"""

import asyncio
import logging
import platform
import subprocess

logger = logging.getLogger(__name__)

_current_context: dict = {
    "activeWindow": None,
    "currentActivity": None,
}


def _get_active_window_macos() -> str | None:
    """Get the frontmost application name on macOS using osascript."""
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get name of first process whose frontmost is true',
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug("Context poller osascript failed: %s", e)
    return None


def poll_once() -> dict:
    """Poll current context once. Returns cached structure."""
    global _current_context
    if platform.system() != "Darwin":
        _current_context = {"activeWindow": None, "currentActivity": None}
        return _current_context

    app_name = _get_active_window_macos()
    _current_context = {
        "activeWindow": app_name,
        "currentActivity": app_name,  # MVP: same as window; can add classifier later
    }
    return _current_context


def get_context() -> dict:
    """Return cached context (non-blocking)."""
    return dict(_current_context)


async def run_poller_loop(interval: float, enabled: bool):
    """Background asyncio task that polls at interval."""
    if not enabled or platform.system() != "Darwin":
        logger.info("Context poller disabled or not on macOS")
        return

    logger.info("Context poller started (interval=%.1fs)", interval)
    while True:
        try:
            poll_once()
        except Exception as e:
            logger.warning("Context poll error: %s", e)
        await asyncio.sleep(interval)


async def context_poller(interval: float, enabled: bool):
    """Thin wrapper for lifespan; catches cancellation on shutdown."""
    try:
        await run_poller_loop(interval, enabled)
    except asyncio.CancelledError:
        logger.info("Context poller stopped")
