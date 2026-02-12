#!/usr/bin/env python3
"""
MyAgent CLI for power users and scripting (PBI-043).

Usage:
    python -m scripts.cli query "Hello"
    python -m scripts.cli send "Reminder: meeting at 3pm"
    python -m scripts.cli doctor

Environment:
    MYAGENT_API_URL - Base URL (default: http://localhost:8001)
    MYAGENT_API_KEY - API key (or X-API-Key header)
"""

import argparse
import json
import os
import sys

import httpx


def _get_base_url() -> str:
    return os.environ.get("MYAGENT_API_URL", "http://localhost:8001")


def _get_api_key() -> str | None:
    return os.environ.get("MYAGENT_API_KEY", os.environ.get("X_API_KEY"))


def _headers() -> dict:
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    key = _get_api_key()
    if key:
        h["X-API-Key"] = key
    return h


def cmd_query(args: argparse.Namespace) -> int:
    """POST /query and print the answer."""
    base = _get_base_url().rstrip("/")
    payload = {"text": args.text}
    if args.model_id:
        payload["model_id"] = args.model_id
    if args.mode_id:
        payload["mode_id"] = args.mode_id
    if args.session_id:
        payload["session_id"] = args.session_id

    try:
        resp = httpx.post(
            f"{base}/query",
            json=payload,
            headers=_headers(),
            timeout=120.0,
        )
    except httpx.ConnectError as e:
        print(f"Error: Cannot connect to {base}. Is the backend running?", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if resp.status_code == 401:
        print("Error: Unauthorized. Set MYAGENT_API_KEY if the backend requires auth.", file=sys.stderr)
        return 1
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} {resp.text}", file=sys.stderr)
        return 1

    data = resp.json()
    answer = data.get("answer", "")
    if answer:
        print(answer)
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    """POST /api/telegram/send with message body."""
    base = _get_base_url().rstrip("/")
    payload = {"message": args.message}

    try:
        resp = httpx.post(
            f"{base}/api/telegram/send",
            json=payload,
            headers=_headers(),
            timeout=10.0,
        )
    except httpx.ConnectError as e:
        print(f"Error: Cannot connect to {base}. Is the backend running?", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if resp.status_code == 401:
        print("Error: Unauthorized. Set MYAGENT_API_KEY if the backend requires auth.", file=sys.stderr)
        return 1
    if resp.status_code == 400:
        print(f"Error: {resp.json().get('detail', resp.text)}", file=sys.stderr)
        return 1
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} {resp.text}", file=sys.stderr)
        return 1

    print("Message sent.")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """GET /api/system/doctor and print the report."""
    base = _get_base_url().rstrip("/")

    try:
        resp = httpx.get(
            f"{base}/api/system/doctor",
            headers=_headers(),
            timeout=5.0,
        )
    except httpx.ConnectError:
        print(f"Error: Cannot connect to {base}. Is the backend running?", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if resp.status_code == 401:
        print("Error: Unauthorized. Set MYAGENT_API_KEY if the backend requires auth.", file=sys.stderr)
        return 1
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} {resp.text}", file=sys.stderr)
        return 1

    data = resp.json()
    overall = data.get("overall", "ok")
    checks = data.get("checks", [])

    for c in checks:
        status = c.get("status", "?")
        name = c.get("name", "?")
        msg = c.get("message", "")
        symbol = {"ok": "✓", "warn": "⚠", "error": "✗"}.get(status, "?")
        print(f"  {symbol} {name}: {msg}")

    print(f"\nOverall: {overall}")
    return 0 if overall == "ok" else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="myagent",
        description="MyAgent CLI - query and send messages via the API.",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="API base URL (overrides MYAGENT_API_URL)",
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # query
    p_query = subparsers.add_parser("query", help="Submit a query")
    p_query.add_argument("text", help="Query text")
    p_query.add_argument("--model-id", help="Override model")
    p_query.add_argument("--mode-id", help="Override mode")
    p_query.add_argument("--session-id", help="Session ID for continuity")
    p_query.set_defaults(func=cmd_query)

    # send
    p_send = subparsers.add_parser("send", help="Send message to primary Telegram chat")
    p_send.add_argument("message", help="Message to send")
    p_send.set_defaults(func=cmd_send)

    # doctor
    p_doctor = subparsers.add_parser("doctor", help="Health and config check")
    p_doctor.set_defaults(func=cmd_doctor)

    args = parser.parse_args()
    if args.url:
        os.environ["MYAGENT_API_URL"] = args.url

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
