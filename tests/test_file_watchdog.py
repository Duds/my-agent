"""Tests for core/file_watchdog.py (PBI-041)."""

import json
import os
from unittest.mock import patch

import pytest

from core.file_watchdog import (
    _expand_paths,
    _load_watch_config,
    clear_events,
    get_events,
    _emit,
)


def test_expand_paths_expands_home():
    home = os.path.expanduser("~")
    result = _expand_paths([f"{home}/Downloads", "~/nonexistent_xyz_123"])
    assert any("Downloads" in p for p in result)
    assert not any("nonexistent_xyz_123" in p for p in result)


def test_emit_and_get_events():
    clear_events()
    _emit("/tmp/foo.txt", "created")
    _emit("/tmp/bar.txt", "modified")
    evs = get_events(limit=10)
    assert len(evs) == 2
    assert evs[0] == {"path": "/tmp/foo.txt", "event_type": "created"}
    assert evs[1] == {"path": "/tmp/bar.txt", "event_type": "modified"}
    clear_events()
    assert len(get_events()) == 0


def test_load_watch_config_file(tmp_path):
    config_path = tmp_path / "watch_config.json"
    config_path.write_text(json.dumps({"paths": ["~/Downloads"], "patterns": ["*.txt"]}))
    with patch("core.file_watchdog.settings.watch_config_path", str(config_path)), patch(
        "core.file_watchdog.settings.watch_paths", ["~/Projects"]
    ):
        paths, patterns = _load_watch_config()
    assert paths == ["~/Downloads"]
    assert patterns == ["*.txt"]


def test_load_watch_config_missing_uses_defaults():
    with patch(
        "core.file_watchdog.settings.watch_config_path", "/nonexistent/watch.json"
    ), patch("core.file_watchdog.settings.watch_paths", ["~/Downloads"]), patch(
        "core.file_watchdog.settings.watch_patterns", None
    ):
        paths, patterns = _load_watch_config()
    assert paths == ["~/Downloads"]
    assert patterns is None
