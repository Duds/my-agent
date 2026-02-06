import logging
import os
import sys
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
    """User query payload."""

    text: str


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
        routing_info = await router.route_request(query.text)
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


@app.get("/api/personas", summary="List agent personas")
async def list_personas():
    """Return available agent personas."""
    return [
        {"id": "default", "name": "Default Assistant", "description": "General-purpose helpful assistant",
         "systemPrompt": "You are a helpful assistant.", "icon": "Bot", "color": "hsl(217, 92%, 60%)"},
        {"id": "coder", "name": "Code Architect", "description": "Expert software engineer and system designer",
         "systemPrompt": "You are an expert software engineer...", "icon": "Code", "color": "hsl(152, 60%, 45%)"},
        {"id": "analyst", "name": "Data Analyst", "description": "Data analysis and visualisation specialist",
         "systemPrompt": "You are a data analyst...", "icon": "BarChart3", "color": "hsl(38, 92%, 55%)"},
        {"id": "writer", "name": "Technical Writer", "description": "Documentation and technical writing expert",
         "systemPrompt": "You are a technical writer...", "icon": "FileText", "color": "hsl(340, 75%, 55%)"},
        {"id": "devops", "name": "DevOps Engineer", "description": "Infrastructure, CI/CD, and cloud expert",
         "systemPrompt": "You are a DevOps engineer...", "icon": "Server", "color": "hsl(280, 65%, 60%)"},
        {"id": "researcher", "name": "Research Agent", "description": "Deep research and analysis across the web",
         "systemPrompt": "You are a research agent...", "icon": "Search", "color": "hsl(200, 70%, 50%)"},
    ]


@app.get("/api/skills", summary="List platform skills")
async def list_skills():
    """Return available skills (tools/capabilities)."""
    return [
        {"id": "web-search", "name": "Web Search", "description": "Search the web for real-time information", "enabled": True},
        {"id": "code-exec", "name": "Code Execution", "description": "Execute code in a sandboxed environment", "enabled": True},
        {"id": "file-ops", "name": "File Operations", "description": "Read, write, and manage files", "enabled": True},
        {"id": "image-gen", "name": "Image Generation", "description": "Generate images from text prompts", "enabled": False},
        {"id": "browser", "name": "Browser Control", "description": "Navigate and interact with web pages", "enabled": False},
        {"id": "memory", "name": "Long-term Memory", "description": "Persist context across conversations", "enabled": True},
    ]


@app.get("/api/mcps", summary="List MCP servers")
async def list_mcps():
    """Return MCP (Model Context Protocol) server connections."""
    return [
        {"id": "filesystem", "name": "Filesystem", "endpoint": "stdio://fs-server", "status": "connected", "description": "Local filesystem access"},
        {"id": "github", "name": "GitHub", "endpoint": "stdio://gh-server", "status": "connected", "description": "GitHub repository operations"},
    ]


@app.get("/api/integrations", summary="List integrations")
async def list_integrations():
    """Return third-party integrations."""
    return [
        {"id": "vercel", "name": "Vercel", "type": "Deployment", "status": "active", "description": "Deploy and manage applications"},
        {"id": "supabase", "name": "Supabase", "type": "Database", "status": "active", "description": "PostgreSQL database and auth"},
    ]


@app.get("/api/projects", summary="List projects")
async def list_projects():
    """Return projects (placeholder until persistence layer)."""
    return [
        {"id": "proj-1", "name": "Default", "color": "hsl(217, 92%, 60%)", "conversationIds": []},
    ]


@app.get("/api/conversations", summary="List conversations")
async def list_conversations():
    """Return conversations (placeholder until persistence layer)."""
    return []


@app.get("/api/agent-processes", summary="List agent processes")
async def list_agent_processes():
    """Return background agent processes (placeholder)."""
    return []


@app.get("/api/cron-jobs", summary="List cron jobs")
async def list_cron_jobs():
    """Return cron jobs (placeholder)."""
    return []


@app.get("/api/automations", summary="List automations")
async def list_automations():
    """Return automations (placeholder)."""
    return []


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
