import logging
import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

# Configure logging before other imports
logging.basicConfig(
    level=logging.INFO if os.getenv("LOG_LEVEL", "INFO") != "DEBUG" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.adapters_local import OllamaAdapter
from core.adapters_remote import AnthropicAdapter, MoonshotAdapter
from core.config import settings
from core.router import ModelRouter
from core.security import SecurityValidator

logger = logging.getLogger(__name__)

# Initialize adapters and router BEFORE lifespan (router used in lifespan)
local_model = OllamaAdapter(model_name="llama3:latest")
security_validator = SecurityValidator(judge_adapter=local_model)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = AnthropicAdapter(api_key=anthropic_api_key) if anthropic_api_key else None

moonshot_api_key = os.getenv("MOONSHOT_API_KEY")
moonshot_client = MoonshotAdapter(api_key=moonshot_api_key) if moonshot_api_key else None

remote_clients = {}
if anthropic_client and anthropic_client.client:
    remote_clients["anthropic"] = anthropic_client
if moonshot_client and moonshot_client.client:
    remote_clients["moonshot"] = moonshot_client

router = ModelRouter(
    local_client=local_model,
    remote_clients=remote_clients,
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


def _verify_api_key(api_key: str | None) -> bool:
    """Verify API key if API_KEY env is set."""
    expected = settings.api_key
    if not expected:
        return True  # No auth required when API_KEY not set
    return api_key == expected and bool(api_key)


@app.post(
    "/query",
    summary="Submit a query",
    response_description="Routing info and AI response",
)
async def handle_query(
    query: UserQuery,
    x_api_key: str | None = Header(None, alias="X-API-Key"),
):
    if not _verify_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
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

@app.get("/health", summary="Health check")
async def health_check():
    """Liveness probe - returns 200 if service is running."""
    return {"status": "healthy", "service": "Secure Personal Agentic Platform"}


@app.get("/ready", summary="Readiness check")
async def readiness_check():
    """Readiness probe for orchestration (e.g. Kubernetes)."""
    return {"status": "ready"}


# --- UI API endpoints (for Command Center frontend) ---


@app.get("/api/models", summary="List available models")
async def list_models():
    """Return available models from router (Ollama + remote)."""
    models = []
    for m in router.available_models or []:
        models.append({
            "id": m,
            "name": m.replace(":", " ").title(),
            "provider": "ollama",
            "type": "ollama",
            "contextWindow": "32k",
            "status": "online",
        })
    # Add remote models if configured
    if "anthropic" in router.remote_clients:
        models.append({
            "id": "claude-sonnet",
            "name": "Claude Sonnet",
            "provider": "anthropic",
            "type": "commercial",
            "contextWindow": "200k",
            "status": "online",
        })
    if "moonshot" in router.remote_clients:
        models.append({
            "id": "moonshot-v1",
            "name": "Moonshot v1",
            "provider": "moonshot",
            "type": "commercial",
            "contextWindow": "8k",
            "status": "online",
        })
    return models


# Modes (replaces personas per research). Load from config or default.
DEFAULT_MODES = [
    {"id": "general", "name": "General", "description": "General-purpose assistance", "routing": "best-fit"},
    {"id": "private", "name": "Private", "description": "Local routing only; heightened privacy", "routing": "local"},
    {"id": "focus", "name": "Focus", "description": "Focus mode; executive functioning support", "routing": "best-fit"},
    {"id": "relax", "name": "Relax", "description": "Relax mode; no nudges", "routing": "best-fit"},
]


@app.get("/api/modes", summary="List modes")
async def list_modes():
    """Return available modes (General, Private, Focus, Relax). Per research: Mode replaces Persona."""
    return DEFAULT_MODES.copy()


@app.get("/api/personas", summary="List agent personas (deprecated)")
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


@app.get("/api/skills", summary="List platform skills")
async def list_skills():
    """Return available skills (tools/capabilities)."""
    return _skills_store.copy()


class SkillPatch(BaseModel):
    """PATCH body for /api/skills/:id."""

    enabled: bool


@app.patch("/api/skills/{skill_id}", summary="Update skill enabled state")
async def patch_skill(skill_id: str, body: SkillPatch):
    """Toggle skill enabled state. Persists in-memory (config persistence in PBI-026)."""
    for s in _skills_store:
        if s["id"] == skill_id:
            s["enabled"] = body.enabled
            return s
    raise HTTPException(status_code=404, detail="Skill not found")


@app.get("/api/mcps", summary="List MCP servers")
async def list_mcps():
    """Return MCP (Model Context Protocol) server connections."""
    return [
        {"id": "filesystem", "name": "Filesystem", "endpoint": "stdio://fs-server", "status": "connected", "description": "Local filesystem access"},
        {"id": "github", "name": "GitHub", "endpoint": "stdio://gh-server", "status": "connected", "description": "GitHub repository operations"},
    ]


@app.get("/api/integrations", summary="List integrations")
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


@app.get("/api/projects", summary="List projects")
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


@app.post("/api/projects", summary="Create project")
async def create_project(body: ProjectCreate):
    """Create a new project."""
    pid = f"proj-{len(_projects_store) + 1}"
    proj = {"id": pid, "name": body.name, "color": body.color, "conversationIds": []}
    _projects_store.append(proj)
    return proj


@app.patch("/api/projects/{project_id}", summary="Update project")
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


@app.get("/api/conversations", summary="List conversations")
async def list_conversations():
    """Return conversations from in-memory store."""
    return [dict(c) for c in _conversations_store]


class ConversationCreate(BaseModel):
    """POST body for /api/conversations."""

    title: str = "New conversation"
    projectId: str | None = None
    modeId: str | None = None


@app.post("/api/conversations", summary="Create conversation")
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


@app.patch("/api/conversations/{conversation_id}", summary="Update conversation")
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


@app.get("/api/agent-processes", summary="List agent processes")
async def list_agent_processes():
    """Return background agent processes. Stubbed until Automation Hub API."""
    return []  # Stub: returns empty; backend will add config-driven data in PBI-032


@app.get("/api/cron-jobs", summary="List cron jobs")
async def list_cron_jobs():
    """Return cron jobs. Stubbed until Automation Hub API."""
    return []  # Stub: returns empty; backend will add config-driven data in PBI-032


@app.get("/api/automations", summary="List automations")
async def list_automations():
    """Return automations. Stubbed until Automation Hub API."""
    return []  # Stub: returns empty; backend will add config-driven data in PBI-032


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
