import pytest
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
