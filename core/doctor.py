"""
Doctor: read-only health and config checks for deployment verification.

Supports Trust but Verify: API key, CORS, routing config, MCP config,
and Ollama reachability. No side effects.
"""

import json
import logging
import os
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

CheckStatus = str  # "ok" | "warn" | "error"


def _run_checks() -> list[dict[str, Any]]:
    """Run all doctor checks. Read-only; no side effects."""
    checks: list[dict[str, Any]] = []

    # 1. API key
    if settings.api_key:
        checks.append({
            "name": "api_key",
            "status": "ok",
            "message": "API key is set (auth required).",
        })
    else:
        checks.append({
            "name": "api_key",
            "status": "warn",
            "message": "API key is not set; API is open to unauthenticated access.",
        })

    # 2. CORS origins
    origins = settings.get_cors_origins_list()
    if origins:
        checks.append({
            "name": "cors",
            "status": "ok",
            "message": f"CORS origins configured: {', '.join(origins)}",
        })
    else:
        checks.append({
            "name": "cors",
            "status": "warn",
            "message": "No CORS origins configured; cross-origin requests may be blocked.",
        })

    # 3. Routing config path exists and valid JSON
    path = settings.routing_config_path
    if not path:
        checks.append({
            "name": "routing_config",
            "status": "error",
            "message": "routing_config_path is not set.",
        })
    elif not os.path.exists(path):
        checks.append({
            "name": "routing_config",
            "status": "warn",
            "message": f"Routing config file does not exist: {path}",
        })
    else:
        try:
            with open(path) as f:
                json.load(f)
            checks.append({
                "name": "routing_config",
                "status": "ok",
                "message": f"Routing config exists and is valid JSON: {path}",
            })
        except (json.JSONDecodeError, OSError) as e:
            checks.append({
                "name": "routing_config",
                "status": "error",
                "message": f"Routing config invalid or unreadable: {e}",
            })

    # 4. MCP config exists
    mcp_path = settings.mcp_config_path
    if not mcp_path:
        checks.append({
            "name": "mcp_config",
            "status": "warn",
            "message": "mcp_config_path is not set.",
        })
    elif not os.path.exists(mcp_path):
        checks.append({
            "name": "mcp_config",
            "status": "warn",
            "message": f"MCP config file does not exist: {mcp_path}",
        })
    else:
        try:
            with open(mcp_path) as f:
                data = json.load(f)
            servers = data.get("servers", [])
            checks.append({
                "name": "mcp_config",
                "status": "ok",
                "message": f"MCP config exists with {len(servers)} server(s): {mcp_path}",
            })
        except (json.JSONDecodeError, OSError) as e:
            checks.append({
                "name": "mcp_config",
                "status": "error",
                "message": f"MCP config invalid or unreadable: {e}",
            })

    return checks


async def _run_async_checks() -> list[dict[str, Any]]:
    """Run async checks (Ollama, optional MCP HTTP probes)."""
    checks: list[dict[str, Any]] = []

    # 5. Ollama reachability
    base = settings.ollama_base_url.rstrip("/")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base}/api/tags", timeout=2.0)
            if resp.status_code == 200:
                checks.append({
                    "name": "ollama",
                    "status": "ok",
                    "message": f"Ollama reachable at {base}",
                })
            else:
                checks.append({
                    "name": "ollama",
                    "status": "warn",
                    "message": f"Ollama at {base} returned status {resp.status_code}",
                })
    except Exception as e:
        checks.append({
            "name": "ollama",
            "status": "error",
            "message": f"Ollama not reachable at {base}: {e}",
        })

    return checks


def _overall(checks: list[dict[str, Any]]) -> str:
    """Compute overall status: error > warn > ok."""
    statuses = [c["status"] for c in checks]
    if "error" in statuses:
        return "error"
    if "warn" in statuses:
        return "warn"
    return "ok"


async def get_doctor_report() -> dict[str, Any]:
    """
    Run all doctor checks and return a structured report.
    Read-only; no side effects.
    """
    checks = _run_checks()
    async_checks = await _run_async_checks()
    all_checks = checks + async_checks
    return {
        "checks": all_checks,
        "overall": _overall(all_checks),
    }
