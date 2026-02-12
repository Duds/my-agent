import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from core.main import app
from core.config import settings

client = TestClient(app)

@pytest.fixture
def api_key():
    """Ensure an API key is set for testing."""
    original_key = settings.api_key
    settings.api_key = "test-secret-key"
    yield "test-secret-key"
    settings.api_key = original_key

def test_health_check_public():
    """Health check should remain public."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ready_check_public():
    """Readiness check should remain public."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_metrics_endpoint():
    """Prometheus metrics endpoint should return 200 with text/plain."""
    response = client.get("/metrics")
    assert response.status_code in (200, 503)
    if response.status_code == 200:
        assert "http_requests_total" in response.text or "python" in response.text


def test_commands_endpoint(api_key):
    """GET /api/commands returns structured chat commands (PBI-049)."""
    response = client.get(
        "/api/commands",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [c["name"] for c in data]
    assert "status" in names
    assert "reset" in names
    assert "think" in names
    for c in data:
        assert "name" in c
        assert "description" in c
        assert "usage" in c


def test_doctor_endpoint(api_key):
    """GET /api/system/doctor returns structured config and connectivity checks (PBI-044)."""
    response = client.get(
        "/api/system/doctor",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert "checks" in data
    assert "overall" in data
    assert data["overall"] in ("ok", "warn", "error")
    assert isinstance(data["checks"], list)
    names = [c["name"] for c in data["checks"]]
    assert "api_key" in names
    assert "cors" in names
    assert "routing_config" in names
    assert "mcp_config" in names
    assert "ollama" in names
    for c in data["checks"]:
        assert c["status"] in ("ok", "warn", "error")
        assert "message" in c


def test_api_cron_jobs(api_key):
    """GET /api/cron-jobs returns config-driven cron jobs."""
    response = client.get(
        "/api/cron-jobs",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for job in data:
        assert "id" in job
        assert "name" in job
        assert "schedule" in job
        assert "status" in job


def test_api_automations(api_key):
    """GET /api/automations returns config-driven automations."""
    response = client.get(
        "/api/automations",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for auto in data:
        assert "id" in auto
        assert "name" in auto
        assert "trigger" in auto
        assert "status" in auto


def test_query_unauthorized_missing_key(api_key):
    """Query should fail without API key when one is set."""
    response = client.post("/query", json={"text": "Hello"})
    assert response.status_code == 401
    assert "Missing or invalid API Key" in response.json()["detail"]

def test_query_unauthorized_invalid_key(api_key):
    """Query should fail with wrong API key."""
    response = client.post(
        "/query", 
        json={"text": "Hello"},
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401

def test_query_authorized(api_key, monkeypatch):
    """Query should succeed with correct API key."""
    # Mock the router to avoid actual LLM calls
    async def mock_route(*args, **kwargs):
        return {
            "intent": "speed",
            "adapter": "test",
            "answer": "Mocked response",
            "requires_privacy": False,
            "security": {"is_safe": True}
        }
    
    from core.router import ModelRouter
    monkeypatch.setattr(ModelRouter, "route_request", mock_route)
    
    response = client.post(
        "/query",
        json={"text": "Hello"},
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "Mocked response"


def test_query_returns_agent_generated_when_create_agent(api_key, monkeypatch):
    """When router returns agent_generated, response includes it (PBI-037)."""
    async def mock_route(*args, **kwargs):
        return {
            "intent": "create_agent",
            "adapter": "agent-generator",
            "answer": "Agent 'Test' is ready for review.",
            "requires_privacy": False,
            "security": {"is_safe": True},
            "agent_generated": {
                "code": "class Test(AgentTemplate): pass",
                "agent_id": "test-id",
                "agent_name": "Test",
                "valid": True,
            },
        }
    from core.router import ModelRouter
    monkeypatch.setattr(ModelRouter, "route_request", mock_route)
    response = client.post(
        "/query",
        json={"text": "Create an agent"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["routing"]["intent"] == "create_agent"
    assert "agent_generated" in data
    assert data["agent_generated"]["agent_id"] == "test-id"
    assert data["agent_generated"]["valid"] is True

def test_api_models_unauthorized(api_key):
    """UI API endpoints should be secured."""
    response = client.get("/api/models")
    assert response.status_code == 401

def test_api_models_authorized(api_key):
    """Models list should succeed with correct API key."""
    response = client.get(
        "/api/models",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "remote" in data
    assert "local" in data
    assert "active_local_default" in data

def test_auth_not_required_when_key_not_set():
    """Authentication should not be enforced if no API_KEY is configured."""
    original_key = settings.api_key
    settings.api_key = None
    try:
        response = client.get("/api/models")
        assert response.status_code == 200
    finally:
        settings.api_key = original_key


def test_api_config_routing_get(api_key):
    """GET /api/config/routing returns current routing config."""
    response = client.get(
        "/api/config/routing",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_api_config_routing_post(api_key):
    """POST /api/config/routing updates and returns config."""
    response = client.post(
        "/api/config/routing",
        json={"intent_classification": "auto"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "config" in data


def test_api_system_status(api_key):
    """GET /api/system/status returns ollama, backend, frontend status."""
    response = client.get(
        "/api/system/status",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert "ollama" in data
    assert "backend" in data
    assert "frontend" in data
    assert data["ollama"]["port"] == 11434
    assert data["backend"]["port"] == 8001


def test_api_mcps_authorized(api_key):
    """GET /api/mcps returns config-driven MCP server list with status."""
    response = client.get(
        "/api/mcps",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for mcp in data:
        assert "id" in mcp
        assert "name" in mcp
        assert "endpoint" in mcp
        assert "status" in mcp
        assert "description" in mcp
        assert mcp["status"] in ("connected", "disconnected", "configured", "error")


# --- Projects CRUD (PBI-040) ---


def test_api_projects_get(api_key):
    """GET /api/projects returns project list."""
    response = client.get(
        "/api/projects",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for p in data:
        assert "id" in p
        assert "name" in p
        assert "color" in p
        assert "conversationIds" in p


def test_api_projects_post(api_key):
    """POST /api/projects creates a new project."""
    response = client.post(
        "/api/projects",
        json={"name": "Test Project", "color": "hsl(217, 92%, 60%)"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["color"] == "hsl(217, 92%, 60%)"
    assert "id" in data
    assert "conversationIds" in data
    assert data["conversationIds"] == []


def test_api_projects_patch(api_key):
    """PATCH /api/projects/:id updates a project."""
    # Create a project first to avoid mutating shared state
    create_resp = client.post(
        "/api/projects",
        json={"name": "Patch Target", "color": "hsl(217, 92%, 60%)"},
        headers={"X-API-Key": api_key},
    )
    assert create_resp.status_code == 200
    pid = create_resp.json()["id"]

    response = client.patch(
        f"/api/projects/{pid}",
        json={"name": "Renamed Project", "color": "hsl(142, 76%, 36%)"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Renamed Project"
    assert data["color"] == "hsl(142, 76%, 36%)"
    assert data["id"] == pid


def test_api_projects_patch_not_found(api_key):
    """PATCH /api/projects/:id returns 404 for unknown project."""
    response = client.patch(
        "/api/projects/nonexistent-id",
        json={"name": "x"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 404


# --- Agent processes (PBI-039 / Automation Hub) ---


def test_api_agent_processes(api_key):
    """GET /api/agent-processes returns agents from data/agents.json."""
    response = client.get(
        "/api/agent-processes",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for a in data:
        assert "id" in a
        assert "name" in a
        assert "status" in a
        assert "type" in a


# --- Conversations ---


def test_api_conversations_get(api_key):
    """GET /api/conversations returns conversation list."""
    response = client.get(
        "/api/conversations",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_conversations_post(api_key):
    """POST /api/conversations creates a new conversation."""
    response = client.post(
        "/api/conversations",
        json={"title": "Test Chat", "projectId": "proj-1"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Chat"
    assert data["projectId"] == "proj-1"
    assert "id" in data
    assert "messages" in data
    assert "createdAt" in data
    assert "updatedAt" in data


# --- Modes, Personas, Skills ---


def test_api_modes(api_key):
    """GET /api/modes returns mode list."""
    response = client.get("/api/modes", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(m.get("id") == "general" for m in data)
    for m in data:
        assert "id" in m and "name" in m and "description" in m and "routing" in m


def test_api_personas(api_key):
    """GET /api/personas returns deprecated persona list."""
    response = client.get("/api/personas", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for p in data:
        assert "id" in p and "name" in p


def test_api_skills_get(api_key):
    """GET /api/skills returns skills list."""
    response = client.get("/api/skills", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for s in data:
        assert "id" in s and "name" in s and "enabled" in s


def test_api_skills_patch(api_key):
    """PATCH /api/skills/:id updates skill enabled state."""
    response = client.patch(
        "/api/skills/web-search",
        json={"enabled": False},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is False
    # Restore for other tests
    client.patch(
        "/api/skills/web-search",
        json={"enabled": True},
        headers={"X-API-Key": api_key},
    )


def test_api_skills_patch_not_found(api_key):
    """PATCH /api/skills/:id returns 404 for unknown skill."""
    response = client.patch(
        "/api/skills/nonexistent-skill",
        json={"enabled": True},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 404


def test_api_integrations(api_key):
    """GET /api/integrations returns integrations list."""
    response = client.get("/api/integrations", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for i in data:
        assert "id" in i and "name" in i and "status" in i


def test_api_ai_services(api_key):
    """GET /api/integrations/ai-services returns AI provider status."""
    response = client.get(
        "/api/integrations/ai-services",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for s in data:
        assert "provider" in s and "connected" in s and "model_count" in s


def test_api_telegram_primary(api_key):
    """GET /api/telegram/primary returns chat_id."""
    response = client.get(
        "/api/telegram/primary",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert "chat_id" in data


def test_api_telegram_send_missing_body(api_key):
    """POST /api/telegram/send with missing message/text returns 400."""
    response = client.post(
        "/api/telegram/send",
        json={},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 400
    assert "message" in response.json()["detail"].lower() or "text" in response.json()["detail"].lower()


def test_api_telegram_send_empty_message(api_key):
    """POST /api/telegram/send with empty message returns 400."""
    response = client.post(
        "/api/telegram/send",
        json={"message": "   "},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 400


def test_api_telegram_send_no_primary_chat(api_key):
    """POST /api/telegram/send with no primary chat configured returns 400."""
    with patch("core.adapters_telegram.get_primary_chat_id", return_value=None):
        response = client.post(
            "/api/telegram/send",
            json={"message": "Hello"},
            headers={"X-API-Key": api_key},
        )
    assert response.status_code == 400
    assert "primary" in response.json()["detail"].lower()


def test_api_integrations_connect_invalid_provider(api_key):
    """POST /api/integrations/{provider}/connect with invalid provider returns 400."""
    response = client.post(
        "/api/integrations/invalid-provider/connect",
        json={"api_key": "some-key"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 400
    assert "unknown" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()


def test_api_integrations_disconnect_invalid_provider(api_key):
    """DELETE /api/integrations/{provider}/connect with invalid provider returns 400."""
    response = client.delete(
        "/api/integrations/invalid-provider/connect",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 400


# --- POST /api/agents/register (PBI-037) ---


def test_api_agents_register_success(api_key, monkeypatch):
    """POST /api/agents/register with valid code returns 200 and agent metadata."""
    mock_entry = {
        "id": "test-agent-1",
        "name": "Test Agent",
        "status": "idle",
        "type": "internal",
        "model": "",
        "description": "Registered via Review UI",
        "source": "agents/test-agent-1.py",
        "skillIds": [],
        "mcpServerIds": [],
        "capabilityIds": [],
    }

    def mock_register_agent_code(code: str):
        return True, mock_entry, None

    monkeypatch.setattr("core.agent_generator.register_agent_code", mock_register_agent_code)
    response = client.post(
        "/api/agents/register",
        json={"code": "class Foo(AgentTemplate): pass"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-agent-1"
    assert data["name"] == "Test Agent"
    assert data["source"] == "agents/test-agent-1.py"


def test_api_agents_register_validation_fails(api_key, monkeypatch):
    """POST /api/agents/register with invalid code returns 400."""
    def mock_register_agent_code(code: str):
        return False, None, "Agent must inherit from AgentTemplate"

    monkeypatch.setattr("core.agent_generator.register_agent_code", mock_register_agent_code)
    response = client.post(
        "/api/agents/register",
        json={"code": "print('not an agent')"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_api_agents_register_missing_code_returns_422(api_key):
    """POST /api/agents/register without code field returns 422."""
    response = client.post(
        "/api/agents/register",
        json={},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 422


def test_query_stream_returns_done_with_routing(api_key, monkeypatch):
    """POST /query/stream yields done event with routing (and optional agent_generated)."""
    async def mock_stream(*args, **kwargs):
        yield "Streamed answer", {"intent": "quality", "adapter": "test", "requires_privacy": False}

    from core.router import ModelRouter
    monkeypatch.setattr(ModelRouter, "route_request_stream", mock_stream)
    response = client.post(
        "/query/stream",
        json={"text": "Hello"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    text = response.text
    # Response is SSE: "data: {...}\n\n"
    data_events = [s.strip().replace("data: ", "") for s in text.split("\n\n") if s.strip().startswith("data:")]
    assert len(data_events) >= 1
    last = json.loads(data_events[-1])
    assert last.get("done") is True
    assert "routing" in last
    assert last["routing"]["intent"] == "quality"


def test_query_stream_handles_router_exception(api_key, monkeypatch):
    """When route_request_stream raises during iteration, stream yields an error event."""
    async def _async_gen_that_raises():
        raise RuntimeError("Router failed")
        yield  # make this an async generator

    def mock_stream_raise(*args, **kwargs):
        return _async_gen_that_raises()

    from core.router import ModelRouter
    monkeypatch.setattr(ModelRouter, "route_request_stream", mock_stream_raise)
    response = client.post(
        "/query/stream",
        json={"text": "Hello"},
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    text = response.text
    data_events = [s.strip().replace("data: ", "") for s in text.split("\n\n") if s.strip().startswith("data:")]
    assert len(data_events) >= 1
    last = json.loads(data_events[-1])
    assert "error" in last
    assert "Router failed" in last["error"]


# --- New main.py routes: sessions, ollama, backend stop ---


def test_api_sessions(api_key):
    """GET /api/sessions returns main plus project-scoped sessions."""
    response = client.get(
        "/api/sessions",
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(s.get("id") == "main" for s in data)
    for s in data:
        assert "id" in s and "label" in s


def test_api_system_ollama_start(api_key):
    """POST /api/system/ollama/start returns success; does not run real ollama."""
    resp_404 = MagicMock(status_code=404)
    mock_get = AsyncMock(return_value=resp_404)
    mock_context = MagicMock()
    mock_context.get = mock_get
    with patch("core.main.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        with patch("subprocess.Popen", return_value=None):
            response = client.post(
                "/api/system/ollama/start",
                headers={"X-API-Key": api_key},
            )
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "success"
    assert "message" in data


def test_api_system_ollama_start_already_running(api_key):
    """POST /api/system/ollama/start when Ollama already running returns success."""
    resp_200 = MagicMock(status_code=200)
    mock_get = AsyncMock(return_value=resp_200)
    mock_context = MagicMock()
    mock_context.get = mock_get
    with patch("core.main.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        response = client.post(
            "/api/system/ollama/start",
            headers={"X-API-Key": api_key},
        )
    assert response.status_code == 200
    assert "already running" in response.json().get("message", "").lower()


def test_api_system_ollama_stop(api_key):
    """POST /api/system/ollama/stop returns success; does not run real pkill."""
    with patch("subprocess.run", return_value=None):
        response = client.post(
            "/api/system/ollama/stop",
            headers={"X-API-Key": api_key},
        )
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "success"
    assert "message" in data


def test_api_system_backend_stop(api_key):
    """POST /api/system/backend/stop returns success; must not actually exit process."""
    # Patch os._exit so the shutdown task does not exit the process. Do not patch
    # asyncio.create_task, so the shutdown coroutine is scheduled and awaited by the
    # event loop, avoiding "coroutine was never awaited" RuntimeWarning.
    with patch("os._exit"):
        response = client.post(
            "/api/system/backend/stop",
            headers={"X-API-Key": api_key},
        )
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "success"
    assert "shutdown" in data.get("message", "").lower()
