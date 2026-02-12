"""
Slack channel adapter for the Secure Personal Agentic Platform (PBI-045).

Inbound messages are routed through the same Router and security stack as Telegram.
Uses Slack Events API (HTTP endpoint); verify request signature and post replies via Slack API.
"""

import hashlib
import hmac
import logging
import asyncio
from typing import Any, Dict, Optional

import httpx

from .config import settings
from .router import ModelRouter

logger = logging.getLogger(__name__)

SLACK_API_BASE = "https://slack.com/api"


def verify_slack_signature(body: bytes, signature: Optional[str], timestamp: Optional[str] = None) -> bool:
    """Verify X-Slack-Signature: v0=<hmac_sha256 of 'v0:' + timestamp + ':' + raw_body>."""
    if not settings.slack_signing_secret or not signature or not signature.startswith("v0="):
        return False
    ts = timestamp or ""
    raw = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else body
    sig_basestring = f"v0:{ts}:{raw}"
    expected = "v0=" + hmac.new(
        settings.slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def post_slack_message(channel: str, text: str, thread_ts: Optional[str] = None) -> bool:
    """Post a message to a Slack channel (and optional thread)."""
    token = settings.slack_bot_token
    if not token or token == "your_slack_bot_token":
        logger.warning("Slack bot token not configured")
        return False
    url = f"{SLACK_API_BASE}/chat.postMessage"
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                timeout=10.0,
            )
            if resp.status_code != 200:
                logger.error("Slack API error: %s %s", resp.status_code, resp.text)
                return False
            data = resp.json()
            if not data.get("ok"):
                logger.error("Slack API not ok: %s", data)
                return False
            return True
    except Exception as e:
        logger.exception("Failed to post Slack message: %s", e)
        return False


async def handle_slack_event(payload: Dict[str, Any], router: ModelRouter) -> Dict[str, Any] | None:
    """
    Handle a Slack Events API payload. Returns response dict for HTTP (e.g. challenge)
    or None if 200 OK is enough (event processed or ignored).
    """
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge", "")}

    if payload.get("type") != "event_callback":
        return None

    event = payload.get("event", {})
    if event.get("type") != "message":
        return None
    # Skip bot messages and message subtypes (edits, etc.)
    if event.get("bot_id") or event.get("subtype"):
        return None
    text = (event.get("text") or "").strip()
    if not text:
        return None

    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    user_id = event.get("user", "")

    async def process_and_reply() -> None:
        try:
            routing_info = await router.route_request(text, mode_id=None)
            answer = routing_info.get("answer", "No response.")
            await post_slack_message(channel_id, answer, thread_ts=thread_ts)
        except Exception as e:
            logger.exception("Slack route/reply failed: %s", e)
            await post_slack_message(
                channel_id,
                f"Sorry, I encountered an error: {e}",
                thread_ts=thread_ts,
            )

    # Run in background so we can return 200 quickly to Slack
    asyncio.create_task(process_and_reply())
    return None
