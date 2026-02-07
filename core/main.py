import logging
import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.logging_config import setup_logging

# Configure logging before other imports
setup_logging()
from fastapi import FastAPI, Header, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

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

logger = logging.getLogger(__name__)

# Initialize adapters using factory
adapter_factory = AdapterFactory()
adapter_factory.initialize_remotes()

# Initialize core services
local_model = adapter_factory.get_local_adapter(settings.ollama_default_model)
security_validator = SecurityValidator(judge_adapter=local_model)

router = ModelRouter(
    local_client=local_model,
    adapter_factory=adapter_factory,
    security_validator=security_validator,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    models = await OllamaAdapter.get_available_models()
    logger.info("Startup: Discovered local models: %s", models)
    router.available_models = models
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
    dependencies=[Depends(get_api_key)],
)
async def handle_query(
    query: UserQuery,
):
    try:
        routing_info = await router.route_request(
            query.text,
            model_id=query.model_id,
            mode_id=query.mode_id,
            session_id=query.session_id,
        )
    except Exception as e:
        logger.exception("Query failed: %s", e)
        raise HTTPException(status_code=500, detail="Query processing failed") from e
    return {
        "status": "success",
        "routing": {
            "intent": routing_info["intent"],
            "adapter": routing_info["adapter"],
            "requires_privacy": routing_info["requires_privacy"]
        },
        "answer": routing_info["answer"],
        "security": routing_info["security"]
    }


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


# --- UI API endpoints (for Command Center frontend) ---


@app.get("/api/models", summary="List all available models")
async def list_models(
    api_key: str = Depends(get_api_key),
):
    """Returns a list of all models (local and remote) available to the user."""
    all_remote_adapters = adapter_factory.get_all_remote_adapters()
    
    remote_models = [
        {"id": "claude-sonnet", "name": "Anthropic Claude 3.5 Sonnet", "provider": "Anthropic"}
        if "anthropic" in all_remote_adapters else None,
        {"id": "mistral-small", "name": "Mistral Small", "provider": "Mistral"}
        if "mistral" in all_remote_adapters else None,
        {"id": "moonshot-v1", "name": "Moonshot V1", "provider": "Moonshot"}
        if "moonshot" in all_remote_adapters else None
    ]
    # Filter out None values
    remote_models = [m for m in remote_models if m is not None]
    
    local_models_list = [
        {"id": name, "name": name, "provider": "Ollama (Local)"}
        for name in (router.available_models or [])
    ]
    
    return {
        "remote": remote_models,
        "local": local_models_list,
        "active_local_default": settings.ollama_default_model
    }


# Modes (replaces personas per research). Load from config or default.
DEFAULT_MODES = [
    {"id": "general", "name": "General", "description": "General-purpose assistance", "routing": "best-fit"},
    {"id": "private", "name": "Private", "description": "Local routing only; heightened privacy", "routing": "local"},
    {"id": "focus", "name": "Focus", "description": "Focus mode; executive functioning support", "routing": "best-fit"},
    {"id": "relax", "name": "Relax", "description": "Relax mode; no nudges", "routing": "best-fit"},
]


@app.get("/api/modes", summary="List modes", dependencies=[Depends(get_api_key)])
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


@app.get("/api/skills", summary="List platform skills", dependencies=[Depends(get_api_key)])
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


@app.get("/api/mcps", summary="List MCP servers", dependencies=[Depends(get_api_key)])
async def list_mcps():
    """Return MCP (Model Context Protocol) server connections."""
    return [
        {"id": "filesystem", "name": "Filesystem", "endpoint": "stdio://fs-server", "status": "connected", "description": "Local filesystem access"},
        {"id": "github", "name": "GitHub", "endpoint": "stdio://gh-server", "status": "connected", "description": "GitHub repository operations"},
    ]


@app.get("/api/integrations", summary="List integrations", dependencies=[Depends(get_api_key)])
async def list_integrations():
    """Return third-party integrations. Includes Google when credentials available."""
    integrations = [
        {"id": "vercel", "name": "Vercel", "type": "Deployment", "status": "active", "description": "Deploy and manage applications"},
        {"id": "supabase", "name": "Supabase", "type": "Database", "status": "active", "description": "PostgreSQL database and auth"},
    ]
    # Wire Google adapter when credentials present (adapters/google_adapter.py)
    _google_creds = os.getenv("GOOGLE_CREDENTIALS_PATH") or os.path.join(os.path.dirname(__file__), "..", "credentials.json")
    if os.path.isfile(_google_creds):
        integrations.append({"id": "google", "name": "Google Workspace", "type": "Productivity", "status": "configured", "description": "Gmail, Calendar, Drive"})
    return integrations


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


@app.get("/api/projects", summary="List projects", dependencies=[Depends(get_api_key)])
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


@app.get("/api/conversations", summary="List conversations", dependencies=[Depends(get_api_key)])
async def list_conversations():
    """Return conversations from in-memory store."""
    return [dict(c) for c in _conversations_store]


class ConversationCreate(BaseModel):
    """POST body for /api/conversations."""

    title: str = "New conversation"
    projectId: str | None = None
    modeId: str | None = None


@app.post("/api/conversations", summary="Create conversation", dependencies=[Depends(get_api_key)])
async def create_conversation(body: ConversationCreate):
    """Create a new conversation and optionally attach to project."""
    cid = _next_conv_id()
    proj_id = body.projectId or (_projects_store[0]["id"] if _projects_store else "proj-1")
    conv = {
        "id": cid,
        "title": body.title,
        "projectId": proj_id,
        "modeId": body.modeId,
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


@app.get("/api/agent-processes", summary="List agent processes", dependencies=[Depends(get_api_key)])
async def list_agent_processes():
    """Return background agent processes. Stubbed until Automation Hub API."""
    return []  # Stub: returns empty; backend will add config-driven data in PBI-032


@app.get("/api/cron-jobs", summary="List cron jobs", dependencies=[Depends(get_api_key)])
async def list_cron_jobs():
    """Return cron jobs. Stubbed until Automation Hub API."""
    return []  # Stub: returns empty; backend will add config-driven data in PBI-032


@app.get("/api/automations", summary="List automations", dependencies=[Depends(get_api_key)])
async def list_automations():
    """Return automations. Stubbed until Automation Hub API."""
    return []  # Stub: returns empty; backend will add config-driven data in PBI-032


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
