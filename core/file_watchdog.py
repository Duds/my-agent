"""
File Watchdog (PBI-041).

Monitors configurable directories for new/changed files and emits events
for downstream Content Classifier or Event Bus.
"""

import logging
import os
import json
from pathlib import Path
from typing import Callable

from .config import settings

logger = logging.getLogger(__name__)

_observer = None
_event_queue: list[dict] = []
_queue_limit = 500


def _expand_paths(paths: list[str]) -> list[str]:
    """Expand ~ in paths and filter to existing directories."""
    result = []
    for p in paths:
        expanded = os.path.expanduser(p.strip())
        if expanded and os.path.isdir(expanded):
            result.append(expanded)
        else:
            logger.debug("Watch path skipped (missing or not dir): %s", p)
    return result


def _load_watch_config() -> tuple[list[str], list[str] | None]:
    """Load watch paths from config file or use defaults."""
    path = settings.watch_config_path
    if path and os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
            paths = data.get("paths", settings.watch_paths)
            patterns = data.get("patterns", settings.watch_patterns)
            return paths, patterns
        except Exception as e:
            logger.warning("Could not load watch config %s: %s", path, e)
    return list(settings.watch_paths), settings.watch_patterns


def _emit(path: str, event_type: str):
    """Append event to queue for consumers."""
    global _event_queue
    _event_queue = (_event_queue + [{"path": path, "event_type": event_type}])[-_queue_limit:]
    logger.debug("File event: %s %s", event_type, path)


def get_events(limit: int = 100) -> list[dict]:
    """Return recent events (for API or consumers). Does not clear the queue."""
    return list(_event_queue[-limit:])


def clear_events():
    """Clear the event queue (for testing)."""
    global _event_queue
    _event_queue = []


def start_watchdog():
    """Start the file watchdog observer. Call from app lifespan."""
    global _observer
    if _observer is not None:
        return

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
    except ImportError:
        logger.warning("watchdog not installed; file watchdog disabled")
        return

    paths, patterns = _load_watch_config()
    expanded = _expand_paths(paths)
    if not expanded:
        logger.info("No valid watch paths; file watchdog disabled")
        return

    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            _emit(event.src_path, "created")

        def on_modified(self, event):
            if event.is_directory:
                return
            _emit(event.src_path, "modified")

    _observer = Observer()
    handler = Handler()
    for p in expanded:
        _observer.schedule(handler, p, recursive=False)
    _observer.start()
    logger.info("File watchdog started: %s", expanded)


def stop_watchdog():
    """Stop the file watchdog observer."""
    global _observer
    if _observer is not None:
        _observer.stop()
        _observer.join(timeout=5)
        _observer = None
        logger.info("File watchdog stopped")
