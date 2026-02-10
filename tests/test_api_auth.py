import pytest
from unittest.mock import patch
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
    with patch("core.main.get_primary_chat_id", return_value=None):
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
