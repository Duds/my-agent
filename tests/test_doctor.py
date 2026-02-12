"""Tests for core.doctor: health and config checks."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock

from core.doctor import (
    _run_checks,
    _run_async_checks,
    _overall,
    get_doctor_report,
)


def test_overall_error_wins():
    """Overall status is error if any check is error."""
    assert _overall([{"status": "ok"}, {"status": "error"}]) == "error"
    assert _overall([{"status": "error"}]) == "error"


def test_overall_warn_when_no_error():
    """Overall status is warn if any check is warn and none error."""
    assert _overall([{"status": "ok"}, {"status": "warn"}]) == "warn"
    assert _overall([{"status": "warn"}]) == "warn"


def test_overall_ok_when_all_ok():
    """Overall status is ok when all checks ok."""
    assert _overall([{"status": "ok"}, {"status": "ok"}]) == "ok"
    assert _overall([]) == "ok"


def test_run_checks_api_key_set(tmp_path):
    """When API key is set, api_key check is ok."""
    routing_file = tmp_path / "routing.json"
    routing_file.write_text("{}")
    mcp_file = tmp_path / "mcp.json"
    mcp_file.write_text('{"servers": []}')
    with patch("core.doctor.settings") as mock_s:
        mock_s.api_key = "secret"
        mock_s.get_cors_origins_list.return_value = ["http://localhost:3000"]
        mock_s.routing_config_path = str(routing_file)
        mock_s.mcp_config_path = str(mcp_file)
        with patch("os.path.exists", return_value=True):
            checks = _run_checks()
    api_key_check = next(c for c in checks if c["name"] == "api_key")
    assert api_key_check["status"] == "ok"
    assert "set" in api_key_check["message"].lower()


def test_run_checks_api_key_not_set(tmp_path):
    """When API key is not set, api_key check is warn."""
    routing_file = tmp_path / "routing.json"
    routing_file.write_text("{}")
    mcp_file = tmp_path / "mcp.json"
    mcp_file.write_text('{"servers": []}')
    with patch("core.doctor.settings") as mock_s:
        mock_s.api_key = None
        mock_s.get_cors_origins_list.return_value = ["http://localhost:3000"]
        mock_s.routing_config_path = str(routing_file)
        mock_s.mcp_config_path = str(mcp_file)
        with patch("os.path.exists", return_value=True):
            checks = _run_checks()
    api_key_check = next(c for c in checks if c["name"] == "api_key")
    assert api_key_check["status"] == "warn"
    assert "not set" in api_key_check["message"].lower()


def test_run_checks_cors_empty(tmp_path):
    """When CORS origins empty, cors check is warn."""
    routing_file = tmp_path / "routing.json"
    routing_file.write_text("{}")
    mcp_file = tmp_path / "mcp.json"
    mcp_file.write_text('{"servers": []}')
    with patch("core.doctor.settings") as mock_s:
        mock_s.api_key = "x"
        mock_s.get_cors_origins_list.return_value = []
        mock_s.routing_config_path = str(routing_file)
        mock_s.mcp_config_path = str(mcp_file)
        with patch("os.path.exists", return_value=True):
            checks = _run_checks()
    cors_check = next(c for c in checks if c["name"] == "cors")
    assert cors_check["status"] == "warn"


def test_run_checks_routing_config_missing(tmp_path):
    """When routing config path does not exist, routing_config check is warn."""
    mcp_file = tmp_path / "mcp.json"
    mcp_file.write_text('{"servers": []}')
    with patch("core.doctor.settings") as mock_s:
        mock_s.api_key = "x"
        mock_s.get_cors_origins_list.return_value = ["http://localhost:3000"]
        mock_s.routing_config_path = str(tmp_path / "nonexistent_routing.json")
        mock_s.mcp_config_path = str(mcp_file)
        with patch("os.path.exists", side_effect=lambda p: p == str(mcp_file)):
            checks = _run_checks()
    routing_check = next(c for c in checks if c["name"] == "routing_config")
    assert routing_check["status"] == "warn"
    assert "does not exist" in routing_check["message"]


def test_run_checks_routing_config_invalid_json(tmp_path):
    """When routing config is invalid JSON, routing_config check is error."""
    routing_file = tmp_path / "routing.json"
    routing_file.write_text("not json {")
    mcp_file = tmp_path / "mcp_servers.json"
    mcp_file.write_text('{"servers": []}')
    with patch("core.doctor.settings") as mock_s:
        mock_s.api_key = "x"
        mock_s.get_cors_origins_list.return_value = ["http://localhost:3000"]
        mock_s.routing_config_path = str(routing_file)
        mock_s.mcp_config_path = str(mcp_file)
        with patch("os.path.exists", return_value=True):
            checks = _run_checks()
    routing_check = next(c for c in checks if c["name"] == "routing_config")
    assert routing_check["status"] == "error"
    assert "invalid" in routing_check["message"].lower() or "unreadable" in routing_check["message"].lower()


def test_run_checks_mcp_config_missing(tmp_path):
    """When MCP config path does not exist, mcp_config check is warn."""
    routing_file = tmp_path / "routing.json"
    routing_file.write_text("{}")
    with patch("core.doctor.settings") as mock_s:
        mock_s.api_key = "x"
        mock_s.get_cors_origins_list.return_value = ["http://localhost:3000"]
        mock_s.routing_config_path = str(routing_file)
        mock_s.mcp_config_path = str(tmp_path / "nonexistent_mcp.json")
        with patch("os.path.exists", side_effect=lambda p: p == str(routing_file)):
            checks = _run_checks()
    mcp_check = next(c for c in checks if c["name"] == "mcp_config")
    assert mcp_check["status"] == "warn"
    assert "does not exist" in mcp_check["message"]


def test_run_checks_mcp_config_valid(tmp_path):
    """When MCP config exists and valid, mcp_config check is ok with server count."""
    routing_file = tmp_path / "routing.json"
    routing_file.write_text("{}")
    mcp_file = tmp_path / "mcp.json"
    mcp_file.write_text('{"servers": [{"id": "a"}, {"id": "b"}]}')
    with patch("core.doctor.settings") as mock_s:
        mock_s.api_key = "x"
        mock_s.get_cors_origins_list.return_value = ["http://localhost:3000"]
        mock_s.routing_config_path = str(routing_file)
        mock_s.mcp_config_path = str(mcp_file)
        with patch("os.path.exists", return_value=True):
            checks = _run_checks()
    mcp_check = next(c for c in checks if c["name"] == "mcp_config")
    assert mcp_check["status"] == "ok"
    assert "2 server" in mcp_check["message"]


@pytest.mark.asyncio
async def test_run_async_checks_ollama_ok():
    """When Ollama returns 200, ollama check is ok."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_context = AsyncMock()
    mock_context.get = AsyncMock(return_value=mock_resp)
    with patch("core.doctor.settings") as mock_s:
        mock_s.ollama_base_url = "http://localhost:11434"
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        checks = await _run_async_checks()
    ollama_check = next(c for c in checks if c["name"] == "ollama")
    assert ollama_check["status"] == "ok"
    assert "reachable" in ollama_check["message"].lower()


@pytest.mark.asyncio
async def test_run_async_checks_ollama_non_200():
    """When Ollama returns non-200, ollama check is warn."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 503
    mock_context = AsyncMock()
    mock_context.get = AsyncMock(return_value=mock_resp)
    with patch("core.doctor.settings") as mock_s:
        mock_s.ollama_base_url = "http://localhost:11434"
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        checks = await _run_async_checks()
    ollama_check = next(c for c in checks if c["name"] == "ollama")
    assert ollama_check["status"] == "warn"
    assert "503" in ollama_check["message"]


@pytest.mark.asyncio
async def test_run_async_checks_ollama_unreachable():
    """When Ollama request raises, ollama check is error."""
    mock_context = AsyncMock()
    mock_context.get = AsyncMock(side_effect=Exception("Connection refused"))
    with patch("core.doctor.settings") as mock_s:
        mock_s.ollama_base_url = "http://localhost:11434"
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        checks = await _run_async_checks()
    ollama_check = next(c for c in checks if c["name"] == "ollama")
    assert ollama_check["status"] == "error"
    assert "not reachable" in ollama_check["message"].lower() or "Connection refused" in ollama_check["message"]


@pytest.mark.asyncio
async def test_get_doctor_report_structure():
    """get_doctor_report returns checks and overall."""
    with patch("core.doctor._run_checks", return_value=[{"name": "api_key", "status": "ok", "message": "x"}]):
        with patch("core.doctor._run_async_checks", new_callable=AsyncMock, return_value=[{"name": "ollama", "status": "ok", "message": "y"}]):
            report = await get_doctor_report()
    assert "checks" in report
    assert "overall" in report
    assert len(report["checks"]) == 2
    assert report["overall"] == "ok"
