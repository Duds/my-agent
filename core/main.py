import asyncio
import logging
import os
import sys
import subprocess
import time
import httpx
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.logging_config import setup_logging

# Configure logging before other imports
setup_logging()
from fastapi import FastAPI, Header, HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, JSONResponse
from pydantic import BaseModel
import uvicorn
import json
from . import api_schemas as schemas

try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

    _http_requests_total = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
    )
    _http_request_duration_seconds = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["path"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    )
    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False

# Security scheme
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if not settings.api_key:
        return None # No auth required
    if api_key_header == settings.api_key:
        return api_key_header
    raise HTTPException(
        status_code=401,
        detail="Missing or invalid API Key",
    )

from core.adapters_local import OllamaAdapter
from core.factory import AdapterFactory
from core.router import ModelRouter
from core.security import SecurityValidator
from core.memory import MemorySystem
from core import credentials
from core.model_discovery import discover_models
from core.model_registry import get_models_for_provider
from core.doctor import get_doctor_report
from core.commands import get_commands_list

logger = logging.getLogger(__name__)

# Initialize adapters using factory
adapter_factory = AdapterFactory()
adapter_factory.initialize_remotes()

# Initialize core services
local_model = adapter_factory.get_local_adapter(settings.ollama_default_model)
security_validator = SecurityValidator(judge_adapter=local_model)
memory_system = MemorySystem(base_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))

router = ModelRouter(
    local_client=local_model,
    adapter_factory=adapter_factory,
    security_validator=security_validator,
    memory_system=memory_system,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure default routing config exists
    config_dir = os.path.dirname(settings.routing_config_path)
    config_path = settings.routing_config_path
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w") as f:
                json.dump({}, f, indent=2)
            logger.info("Created default routing config at %s", config_path)
        except Exception as e:
            logger.warning("Could not create default routing config: %s", e)

    # Ensure default MCP config exists
    mcp_path = settings.mcp_config_path
    if not os.path.exists(mcp_path):
        try:
            mcp_dir = os.path.dirname(mcp_path)
            if mcp_dir:
                os.makedirs(mcp_dir, exist_ok=True)
            default_mcp = {
                "servers": [
                    {"id": "filesystem", "name": "Filesystem", "endpoint": "stdio://fs-server", "description": "Local filesystem access"},
                    {"id": "github", "name": "GitHub", "endpoint": "stdio://gh-server", "description": "GitHub repository operations"},
                ]
            }
            with open(mcp_path, "w") as f:
                json.dump(default_mcp, f, indent=2)
            logger.info("Created default MCP config at %s", mcp_path)
        except Exception as e:
            logger.warning("Could not create default MCP config: %s", e)

    models = await OllamaAdapter.get_available_models()
    logger.info("Startup: Discovered local models: %s", models)
    router.available_models = models
    router._load_routing_config()  # Reload after models discovered
    yield


app = FastAPI(
    title="Secure Personal Agentic Platform",
    description="Privacy-first personal AI assistant with intelligent model routing",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Restrict CORS to configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request count and latency for Prometheus."""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    if _PROMETHEUS_AVAILABLE:
        path = request.url.path
        status = response.status_code
        _http_requests_total.labels(method=request.method, path=path, status=status).inc()
        _http_request_duration_seconds.labels(path=path).observe(duration)
    return response


class UserQuery(BaseModel):
    """User query payload. Per research: mode_id replaces persona_id."""

    text: str
    model_id: str | None = None
    mode_id: str | None = None
    session_id: str | None = None


@app.post(
    "/query",
    summary="Submit a query",
    response_description="Routing info and AI response",
    response_model=schemas.QueryResponse,
    dependencies=[Depends(get_api_key)],
)
async def handle_query(
    query: UserQuery,
):
    # Default to 'main' session when omitted (PBI-046)
    session_id = query.session_id if query.session_id else "main"
    try:
        routing_info = await router.route_request(
            query.text,
            model_id=query.model_id,
            mode_id=query.mode_id,
            session_id=session_id,
        )
    except Exception as e:
        logger.exception("Query failed: %s", e)
        raise HTTPException(status_code=500, detail="Query processing failed") from e
    out = {
        "status": "success",
        "routing": {
            "intent": routing_info["intent"],
            "adapter": routing_info["adapter"],
            "requires_privacy": routing_info["requires_privacy"]
        },
        "answer": routing_info["answer"],
        "security": routing_info["security"]
    }
    if routing_info.get("agent_generated"):
        out["agent_generated"] = routing_info["agent_generated"]
    return out


async def _stream_query_generator(query: UserQuery):
    """Yield SSE events for streaming query endpoint."""
    try:
        async for chunk, routing_meta in router.route_request_stream(
            query.text,
            model_id=query.model_id,
            mode_id=query.mode_id,
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield f"data: {json.dumps({'done': True, 'routing': routing_meta})}\n\n"
    except Exception as e:
        logger.exception("Stream query failed: %s", e)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.post(
    "/query/stream",
    summary="Submit a query (streaming)",
    response_description="Server-Sent Events stream of response chunks",
    dependencies=[Depends(get_api_key)],
)
async def handle_query_stream(
    query: UserQuery,
):
    """Stream response tokens for lower perceived latency (Ollama models)."""
    return StreamingResponse(
        _stream_query_generator(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.get("/health", summary="Health check")
async def health_check():
    """Liveness probe - returns 200 if service is running."""
    return {"status": "healthy", "service": "Secure Personal Agentic Platform"}


@app.get("/ready", summary="Readiness check")
async def readiness_check():
    """Readiness probe for orchestration (e.g. Kubernetes)."""
    return {"status": "ready"}


@app.get("/metrics", summary="Prometheus metrics")
async def metrics():
    """Prometheus metrics endpoint for observability."""
    if not _PROMETHEUS_AVAILABLE:
        return Response(
            content="# prometheus_client not installed\n",
            media_type="text/plain",
            status_code=503,
        )
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# --- UI API endpoints (for Command Center frontend) ---


@app.get("/api/models", summary="List all available models", response_model=schemas.ModelsResponse)
async def list_models(
    api_key: str = Depends(get_api_key),
):
    """Returns a list of all models (local and remote) available to the user."""
    from core.model_registry import get_models_for_provider
    from core.model_metadata import merge_metadata_into_model

    all_remote_adapters = adapter_factory.get_all_remote_adapters()
    remote_models = []
    for provider in ("anthropic", "mistral", "moonshot"):
        if provider not in all_remote_adapters:
            continue
        provider_display = {"anthropic": "Anthropic", "mistral": "Mistral", "moonshot": "Moonshot"}[provider]
        for m in get_models_for_provider(provider):
            model = {
                "id": m["id"],
                "name": m["name"],
                "provider": provider_display,
                "type": "commercial",
                "status": "online",
                "contextWindow": m["contextWindow"],
            }
            merge_metadata_into_model(model, m["id"], "commercial")
            remote_models.append(model)

    local_models_list = []
    for name in (router.available_models or []):
        model = {
            "id": name,
            "name": name,
            "provider": "Ollama (Local)",
            "type": "ollama",
            "status": "online",
            "contextWindow": "128k",
        }
        merge_metadata_into_model(model, name, "ollama")
        local_models_list.append(model)
    
    return {
        "remote": remote_models,
        "local": local_models_list,
        "active_local_default": settings.ollama_default_model
    }


@app.get("/api/config/routing", summary="Get task-specific routing config", dependencies=[Depends(get_api_key)])
async def get_routing_config():
    """Returns current model assignments for meta-tasks."""
    return router.routing_config


@app.post("/api/config/routing", summary="Update task-specific routing config", dependencies=[Depends(get_api_key)])
async def update_routing_config(config: Dict[str, str]):
    """Updates model assignments for meta-tasks (intent, security, pii)."""
    router.update_config(config)
    return {"status": "success", "config": router.routing_config}


# Modes (replaces personas per research). Load from config or default.
DEFAULT_MODES = [
    {"id": "general", "name": "General", "description": "General-purpose assistance", "routing": "best-fit"},
    {"id": "private", "name": "Private", "description": "Local routing only; heightened privacy", "routing": "local"},
    {"id": "focus", "name": "Focus", "description": "Focus mode; executive functioning support", "routing": "best-fit"},
    {"id": "relax", "name": "Relax", "description": "Relax mode; no nudges", "routing": "best-fit"},
]


@app.get("/api/modes", summary="List modes", response_model=list[schemas.ModeInfo], dependencies=[Depends(get_api_key)])
async def list_modes():
    """Return available modes (General, Private, Focus, Relax). Per research: Mode replaces Persona."""
    return DEFAULT_MODES.copy()


@app.get("/api/personas", summary="List agent personas (deprecated)", dependencies=[Depends(get_api_key)])
async def list_personas():
    """Deprecated: use /api/modes. Kept for backward compatibility."""
    return [
        {"id": "general", "name": "General", "description": "General-purpose", "systemPrompt": "", "icon": "Bot", "color": "hsl(217, 92%, 60%)"},
        {"id": "private", "name": "Private", "description": "Local only", "systemPrompt": "", "icon": "Lock", "color": "hsl(152, 60%, 45%)"},
    ]


# In-memory state for skills (persist to config in PBI-026)
_skills_store = [
    {"id": "web-search", "name": "Web Search", "description": "Search the web for real-time information", "enabled": True},
    {"id": "code-exec", "name": "Code Execution", "description": "Execute code in a sandboxed environment", "enabled": True},
    {"id": "file-ops", "name": "File Operations", "description": "Read, write, and manage files", "enabled": True},
    {"id": "image-gen", "name": "Image Generation", "description": "Generate images from text prompts", "enabled": False},
    {"id": "browser", "name": "Browser Control", "description": "Navigate and interact with web pages", "enabled": False},
    {"id": "memory", "name": "Long-term Memory", "description": "Persist context across conversations", "enabled": True},
]


@app.get("/api/skills", summary="List platform skills", response_model=list[schemas.SkillInfo], dependencies=[Depends(get_api_key)])
async def list_skills():
    """Return available skills (tools/capabilities)."""
    return _skills_store.copy()


class SkillPatch(BaseModel):
    """PATCH body for /api/skills/:id."""

    enabled: bool


@app.patch("/api/skills/{skill_id}", summary="Update skill enabled state", dependencies=[Depends(get_api_key)])
async def patch_skill(skill_id: str, body: SkillPatch):
    """Toggle skill enabled state. Persists in-memory (config persistence in PBI-026)."""
    for s in _skills_store:
        if s["id"] == skill_id:
            s["enabled"] = body.enabled
            return s
    raise HTTPException(status_code=404, detail="Skill not found")


def _load_mcp_servers() -> list[dict]:
    """Load MCP servers from config file."""
    path = settings.mcp_config_path
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("servers", [])
    except Exception as e:
        logger.warning("Failed to load MCP config from %s: %s", path, e)
        return []


async def _check_mcp_status(endpoint: str) -> str:
    """Check MCP server status. stdio endpoints return 'configured'; HTTP endpoints are probed."""
    if endpoint.startswith("stdio://"):
        return "configured"
    if endpoint.startswith(("http://", "https://")):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(endpoint, timeout=2.0)
                return "connected" if resp.status_code < 500 else "disconnected"
        except Exception:
            return "disconnected"
    return "configured"


@app.get("/api/mcps", summary="List MCP servers", response_model=list[schemas.MCPInfo], dependencies=[Depends(get_api_key)])
async def list_mcps():
    """Return MCP (Model Context Protocol) server connections from config."""
    servers = _load_mcp_servers()
    result = []
    for s in servers:
        sid = s.get("id", "unknown")
        status = await _check_mcp_status(s.get("endpoint", ""))
        result.append({
            "id": sid,
            "name": s.get("name", sid),
            "endpoint": s.get("endpoint", ""),
            "status": status,
            "description": s.get("description", ""),
        })
    return result


@app.get("/api/system/doctor", summary="Doctor: health and config check", dependencies=[Depends(get_api_key)])
async def doctor():
    """Read-only checks: API key, CORS, routing config, MCP config, Ollama reachability. No side effects."""
    return await get_doctor_report()


@app.get("/api/commands", summary="List chat commands", dependencies=[Depends(get_api_key)])
async def list_commands():
    """Return structured list of slash-style chat commands (PBI-049) for UI and channel implementers."""
    return get_commands_list()


@app.get("/api/system/status", summary="Get system status", dependencies=[Depends(get_api_key)])
async def get_system_status():
    """Check status of Ollama, Backend, and other components."""
    # Ollama check
    ollama_running = False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:11434/api/tags", timeout=1.0)
            ollama_running = resp.status_code == 200
    except Exception:
        ollama_running = False

    # Frontend check (best effort)
    frontend_running = False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:3000", timeout=0.5)
            frontend_running = resp.status_code == 200
    except Exception:
        frontend_running = False

    return {
        "ollama": {"status": "online" if ollama_running else "offline", "port": 11434},
        "backend": {"status": "online", "port": 8001},
        "frontend": {"status": "online" if frontend_running else "offline", "port": 3000},
    }


@app.post("/api/system/ollama/start", summary="Start Ollama daemon", dependencies=[Depends(get_api_key)])
async def start_ollama_daemon():
    """Attempt to start Ollama serve in the background."""
    try:
        # Check if already running
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:11434/api/tags", timeout=1.0)
                if resp.status_code == 200:
                    return {"status": "success", "message": "Ollama is already running"}
        except Exception:
            pass

        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"status": "success", "message": "Ollama start command issued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Ollama: {str(e)}")


@app.post("/api/system/ollama/stop", summary="Stop Ollama daemon", dependencies=[Depends(get_api_key)])
async def stop_ollama_daemon():
    """Attempt to stop Ollama (pkill). Use with caution."""
    try:
        subprocess.run(["pkill", "ollama"], check=False)
        return {"status": "success", "message": "Ollama stop command issued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop Ollama: {str(e)}")


@app.post("/api/system/backend/stop", summary="Stop backend daemon", dependencies=[Depends(get_api_key)])
async def stop_backend_daemon():
    """Gracefully shut down the backend. Client receives response before process exits."""
    async def shutdown_after_response():
        await asyncio.sleep(0.5)
        os._exit(0)

    asyncio.create_task(shutdown_after_response())
    return {"status": "success", "message": "Backend shutdown initiated"}


@app.get("/api/integrations", summary="List integrations", response_model=list[schemas.IntegrationInfo], dependencies=[Depends(get_api_key)])
async def list_integrations():
    """Return third-party integrations. Includes Google when credentials available, Telegram when token configured."""
    integrations = [
        {"id": "vercel", "name": "Vercel", "type": "Deployment", "status": "active", "description": "Deploy and manage applications"},
        {"id": "supabase", "name": "Supabase", "type": "Database", "status": "active", "description": "PostgreSQL database and auth"},
    ]
    # Telegram: status based on TELEGRAM_BOT_TOKEN (config via .env; see TELEGRAM_SETUP.md)
    _telegram_token = settings.telegram_bot_token
    _telegram_configured = bool(_telegram_token and _telegram_token != "your_telegram_bot_token_here")
    integrations.append({
        "id": "telegram",
        "name": "Telegram",
        "type": "Messaging",
        "status": "active" if _telegram_configured else "inactive",
        "description": "Chat with your agent via Telegram. Configure token in .env (see TELEGRAM_SETUP.md)",
    })
    # Wire Google adapter when credentials present (adapters/google_adapter.py)
    _google_creds = os.getenv("GOOGLE_CREDENTIALS_PATH") or os.path.join(os.path.dirname(__file__), "..", "credentials.json")
    if os.path.isfile(_google_creds):
        integrations.append({"id": "google", "name": "Google Workspace", "type": "Productivity", "status": "active", "description": "Gmail, Calendar, Drive"})
    return integrations


@app.get("/api/telegram/primary", summary="Get primary Telegram chat ID", dependencies=[Depends(get_api_key)])
async def get_telegram_primary():
    """
    Return the primary chat ID set via /setmychat or TELEGRAM_PRIMARY_CHAT_ID.
    Use this to confirm which chat the web UI will send messages to.
    """
    from core.adapters_telegram import get_primary_chat_id
    chat_id = get_primary_chat_id()
    return {"chat_id": chat_id}


@app.post("/api/telegram/send", summary="Send message to primary Telegram chat", dependencies=[Depends(get_api_key)])
async def send_telegram_to_primary(body: schemas.TelegramSendBody):
    """
    Send a message to the designated primary Telegram chat.
    Run /setmychat in your Telegram bot first to set the primary chat.
    """
    from core.adapters_telegram import send_telegram_message, get_primary_chat_id
    msg = (body.message or body.text or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Provide 'message' or 'text' in body")
    chat_id = get_primary_chat_id()
    if not chat_id:
        raise HTTPException(
            status_code=400,
            detail="No primary chat configured. Send /setmychat from your Telegram bot first.",
        )
    ok = await send_telegram_message(chat_id, msg)
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to send Telegram message")
    return {"status": "sent", "chat_id": chat_id}


@app.post("/api/channels/slack/events", summary="Slack Events API (PBI-045)")
async def slack_events(request: Request):
    """
    Receive Slack Events API payloads. No API key; verified via X-Slack-Signature.
    Inbound messages are routed through the same Router and security stack.
    """
    from core.adapters_slack import verify_slack_signature, handle_slack_event

    body = await request.body()
    signature = request.headers.get("x-slack-signature")
    timestamp = request.headers.get("x-slack-request-timestamp")
    if not verify_slack_signature(body, signature, timestamp):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    result = await handle_slack_event(payload, router)
    if result is not None:
        return JSONResponse(content=result)
    return Response(status_code=200)


# --- AI Services: connect, discover, disconnect ---

AI_PROVIDERS = ("anthropic", "mistral", "moonshot")
AI_PROVIDER_DISPLAY = {"anthropic": "Anthropic", "mistral": "Mistral", "moonshot": "Moonshot"}


class ConnectBody(BaseModel):
    """Body for POST /api/integrations/{provider}/connect."""

    api_key: str


@app.post(
    "/api/integrations/{provider}/connect",
    summary="Connect AI service with API key",
    response_model=schemas.ConnectServiceResponse,
    dependencies=[Depends(get_api_key)],
)
async def connect_ai_service(provider: str, body: ConnectBody):
    """Validate API key via discovery, save credentials, and reinitialize adapters."""
    provider = provider.lower()
    if provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    api_key = (body.api_key or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    try:
        discovered = await discover_models(provider, api_key)
    except ValueError as e:
        return {"success": False, "provider": provider, "models": [], "error": str(e)}
    except Exception as e:
        logger.exception("Connect discovery failed for %s: %s", provider, e)
        return {"success": False, "provider": provider, "models": [], "error": str(e)}

    try:
        credentials.save_api_key(provider, api_key)
    except Exception as e:
        logger.exception("Failed to save credentials for %s: %s", provider, e)
        return {"success": False, "provider": provider, "models": [], "error": str(e)}

    adapter_factory.reinitialize_remotes()
    models = get_models_for_provider(provider)
    return {
        "success": True,
        "provider": provider,
        "models": [{"id": m["id"], "name": m["name"], "contextWindow": m["contextWindow"]} for m in models],
        "error": None,
    }


@app.post(
    "/api/integrations/{provider}/discover",
    summary="Discover models (validate key without saving)",
    dependencies=[Depends(get_api_key)],
)
async def discover_ai_models(provider: str, body: ConnectBody):
    """Validate API key and return discovered models. Does not save credentials."""
    provider = provider.lower()
    if provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    api_key = (body.api_key or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    try:
        models = await discover_models(provider, api_key)
        return {"success": True, "provider": provider, "models": models}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.exception("Discover failed for %s: %s", provider, e)
        raise HTTPException(status_code=502, detail=str(e))


@app.delete(
    "/api/integrations/{provider}/connect",
    summary="Disconnect AI service",
    dependencies=[Depends(get_api_key)],
)
async def disconnect_ai_service(provider: str):
    """Remove stored API key for provider and reinitialize adapters."""
    provider = provider.lower()
    if provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    credentials.remove_api_key(provider)
    adapter_factory.reinitialize_remotes()
    return {"success": True, "provider": provider}


@app.get(
    "/api/integrations/ai-services",
    summary="List AI service connection status",
    response_model=list[schemas.AIServiceStatus],
    dependencies=[Depends(get_api_key)],
)
async def list_ai_services():
    """Return status of Anthropic, Mistral, Moonshot (connected/disconnected, model count)."""
    result = []
    for p in AI_PROVIDERS:
        connected = credentials.has_api_key(p)
        models = get_models_for_provider(p)
        result.append({
            "provider": p,
            "display_name": AI_PROVIDER_DISPLAY[p],
            "connected": connected,
            "model_count": len(models),
        })
    return result


# In-memory stores for projects and conversations (file-backed in PBI-029, PBI-012)
_projects_store: list[dict] = [
    {"id": "proj-1", "name": "Default", "color": "hsl(217, 92%, 60%)", "conversationIds": []},
]
_conversations_store: list[dict] = []
_conversation_counter = 0


def _next_conv_id() -> str:
    global _conversation_counter
    _conversation_counter += 1
    return f"conv-{_conversation_counter}"


@app.get("/api/projects", summary="List projects", response_model=list[schemas.ProjectInfo], dependencies=[Depends(get_api_key)])
async def list_projects():
    """Return projects from in-memory store."""
    return [dict(p) for p in _projects_store]


class ProjectCreate(BaseModel):
    """POST body for /api/projects."""

    name: str
    color: str = "hsl(217, 92%, 60%)"


class ProjectPatch(BaseModel):
    """PATCH body for /api/projects/:id."""

    name: str | None = None
    color: str | None = None


@app.post("/api/projects", summary="Create project", dependencies=[Depends(get_api_key)])
async def create_project(body: ProjectCreate):
    """Create a new project."""
    pid = f"proj-{len(_projects_store) + 1}"
    proj = {"id": pid, "name": body.name, "color": body.color, "conversationIds": []}
    _projects_store.append(proj)
    return proj


@app.patch("/api/projects/{project_id}", summary="Update project", dependencies=[Depends(get_api_key)])
async def patch_project(project_id: str, body: ProjectPatch):
    """Update a project."""
    for p in _projects_store:
        if p["id"] == project_id:
            if body.name is not None:
                p["name"] = body.name
            if body.color is not None:
                p["color"] = body.color
            return p
    raise HTTPException(status_code=404, detail="Project not found")


@app.get("/api/conversations", summary="List conversations", response_model=list[schemas.ConversationInfo], dependencies=[Depends(get_api_key)])
async def list_conversations():
    """Return conversations from in-memory store."""
    return [dict(c) for c in _conversations_store]


class ConversationCreate(BaseModel):
    """POST body for /api/conversations."""

    title: str = "New conversation"
    projectId: str | None = None
    modeId: str | None = None
    sessionId: str | None = None  # Default 'main' when omitted (PBI-046)


@app.get("/api/sessions", summary="List sessions", dependencies=[Depends(get_api_key)])
async def list_sessions():
    """Return first-class sessions: main plus project-scoped (PBI-046)."""
    sessions = [{"id": "main", "label": "Main"}]
    for p in _projects_store:
        sessions.append({"id": p["id"], "label": p.get("name", p["id"])})
    return sessions


@app.post("/api/conversations", summary="Create conversation", dependencies=[Depends(get_api_key)])
async def create_conversation(body: ConversationCreate):
    """Create a new conversation and optionally attach to project and session."""
    cid = _next_conv_id()
    proj_id = body.projectId or (_projects_store[0]["id"] if _projects_store else "proj-1")
    conv = {
        "id": cid,
        "title": body.title,
        "projectId": proj_id,
        "modeId": body.modeId,
        "sessionId": body.sessionId or "main",
        "messages": [],
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z",
    }
    _conversations_store.append(conv)
    for p in _projects_store:
        if p["id"] == proj_id:
            p["conversationIds"] = list(p.get("conversationIds", [])) + [cid]
            break
    return conv


class ConversationPatch(BaseModel):
    """PATCH body for /api/conversations/:id."""

    title: str | None = None
    messages: list | None = None


@app.patch("/api/conversations/{conversation_id}", summary="Update conversation", dependencies=[Depends(get_api_key)])
async def patch_conversation(conversation_id: str, body: ConversationPatch):
    """Update conversation (e.g. append messages)."""
    for c in _conversations_store:
        if c["id"] == conversation_id:
            if body.title is not None:
                c["title"] = body.title
            if body.messages is not None:
                c["messages"] = body.messages
            c["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            return c
    raise HTTPException(status_code=404, detail="Conversation not found")


def _load_agents() -> list:
    """Load agents from data/agents.json."""
    path = settings.agents_config_path
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        agents = data.get("agents", [])
        return [
            {
                "id": a.get("id", "unknown"),
                "name": a.get("name", "Unknown Agent"),
                "status": a.get("status", "idle"),
                "type": a.get("type", "internal"),
                "model": a.get("model", ""),
                "projectId": a.get("projectId"),
                "startedAt": a.get("startedAt"),
                "description": a.get("description"),
            }
            for a in agents
        ]
    except Exception as e:
        logger.warning("Failed to load agents from %s: %s", path, e)
        return []


# Placeholder for cron nextRun when missing from JSON (deterministic; do not use utcnow()).
_CRON_NEXT_RUN_UNSET = "1970-01-01T00:00:00.000Z"


def _load_cron_jobs() -> list:
    """Load cron jobs from data/cron_jobs.json."""
    path = settings.cron_jobs_config_path
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        jobs = data.get("cronJobs", [])
        return [
            {
                "id": j.get("id", "unknown"),
                "name": j.get("name", "Unnamed"),
                "schedule": j.get("schedule", ""),
                "status": j.get("status", "paused"),
                "lastRun": j.get("lastRun"),
                "nextRun": j.get("nextRun") or _CRON_NEXT_RUN_UNSET,
                "projectId": j.get("projectId"),
                "description": j.get("description", ""),
                "model": j.get("model"),
            }
            for j in jobs
        ]
    except Exception as e:
        logger.warning("Failed to load cron jobs from %s: %s", path, e)
        return []


def _load_automations() -> list:
    """Load automations from data/automations.json."""
    path = settings.automations_config_path
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        autos = data.get("automations", [])
        return [
            {
                "id": a.get("id", "unknown"),
                "name": a.get("name", "Unnamed"),
                "trigger": a.get("trigger", ""),
                "status": a.get("status", "paused"),
                "lastTriggered": a.get("lastTriggered"),
                "runsToday": a.get("runsToday", 0),
                "projectId": a.get("projectId"),
                "description": a.get("description", ""),
                "type": a.get("type", "event"),
            }
            for a in autos
        ]
    except Exception as e:
        logger.warning("Failed to load automations from %s: %s", path, e)
        return []


def _load_scripts() -> list:
    """Load scripts from data/scripts.json."""
    path = settings.scripts_config_path
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        scripts = data.get("scripts", [])
        return [
            {
                "id": s.get("id", "unknown"),
                "name": s.get("name", "Unnamed"),
                "type": s.get("type", "script"),
                "status": s.get("status", "idle"),
                "lastRun": s.get("lastRun"),
                "source": s.get("source"),
            }
            for s in scripts
        ]
    except Exception as e:
        logger.warning("Failed to load scripts from %s: %s", path, e)
        return []


def _load_execution_logs(limit: int = 100, script_id: str | None = None) -> list:
    """Load execution logs from data/execution_logs.json."""
    path = settings.execution_logs_config_path
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        logs = data.get("logs", [])
        if script_id:
            logs = [l for l in logs if l.get("scriptId") == script_id]
        return [
            {
                "id": l.get("id", "unknown"),
                "scriptId": l.get("scriptId", ""),
                "timestamp": l.get("timestamp", ""),
                "status": l.get("status", "unknown"),
                "message": l.get("message"),
                "durationMs": l.get("durationMs"),
            }
            for l in logs[-limit:]
        ][::-1]
    except Exception as e:
        logger.warning("Failed to load execution logs from %s: %s", path, e)
        return []


def _load_error_reports(limit: int = 100, script_id: str | None = None) -> list:
    """Load error reports from data/error_reports.json."""
    path = settings.error_reports_config_path
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        reports = data.get("reports", [])
        if script_id:
            reports = [r for r in reports if r.get("scriptId") == script_id]
        return [
            {
                "id": r.get("id", "unknown"),
                "scriptId": r.get("scriptId", ""),
                "timestamp": r.get("timestamp", ""),
                "message": r.get("message", ""),
                "severity": r.get("severity"),
            }
            for r in reports[-limit:]
        ][::-1]
    except Exception as e:
        logger.warning("Failed to load error reports from %s: %s", path, e)
        return []


@app.get("/api/agent-processes", summary="List agent processes", response_model=list[schemas.AgentProcessInfo], dependencies=[Depends(get_api_key)])
async def list_agent_processes():
    """Return background agent processes from data/agents.json."""
    return _load_agents()


class AgentRegisterBody(BaseModel):
    """Body for POST /api/agents/register."""

    code: str


@app.post(
    "/api/agents/register",
    summary="Register agent code from Review UI",
    dependencies=[Depends(get_api_key)],
)
async def register_agent(body: AgentRegisterBody):
    """
    Validate and register agent code (e.g. after user approves from the Review dialog).
    Returns 200 with agent metadata or 400 with validation errors.
    """
    from core.agent_generator import register_agent_code
    success, entry, error = register_agent_code(body.code)
    if not success:
        raise HTTPException(status_code=400, detail=error or "Validation failed")
    return entry


@app.get("/api/cron-jobs", summary="List cron jobs", response_model=list[schemas.CronJobInfo], dependencies=[Depends(get_api_key)])
async def list_cron_jobs():
    """Return cron jobs from data/cron_jobs.json."""
    return _load_cron_jobs()


@app.get("/api/automations", summary="List automations", response_model=list[schemas.AutomationInfo], dependencies=[Depends(get_api_key)])
async def list_automations():
    """Return automations from data/automations.json."""
    return _load_automations()


@app.get("/api/scripts", summary="List scripts", response_model=list[schemas.ScriptInfo], dependencies=[Depends(get_api_key)])
async def list_scripts():
    """Return scripts from data/scripts.json."""
    return _load_scripts()


@app.get("/api/automation-logs", summary="List execution logs", response_model=list[schemas.ExecutionLogEntry], dependencies=[Depends(get_api_key)])
async def list_automation_logs(limit: int = 100, scriptId: str | None = None):
    """Return execution logs from data/execution_logs.json."""
    return _load_execution_logs(limit=limit, script_id=scriptId)


@app.get("/api/error-reports", summary="List error reports", response_model=list[schemas.ErrorReportEntry], dependencies=[Depends(get_api_key)])
async def list_error_reports(limit: int = 100, scriptId: str | None = None):
    """Return error reports from data/error_reports.json."""
    return _load_error_reports(limit=limit, script_id=scriptId)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
