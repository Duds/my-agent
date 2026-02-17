import pytest
import os
import json
from fastapi.testclient import TestClient
from core.main import app, _load_projects, _load_conversations
from core.config import settings
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def temp_persistence(tmp_path):
    proj_path = str(tmp_path / "projects.json")
    conv_path = str(tmp_path / "conversations.json")
    
    with patch.object(settings, 'projects_config_path', proj_path), \
         patch.object(settings, 'conversations_config_path', conv_path):
        yield proj_path, conv_path

@pytest.fixture(autouse=True)
def mock_api_auth():
    from core.main import get_api_key
    app.dependency_overrides[get_api_key] = lambda: "mock-key"
    yield
    app.dependency_overrides = {}

def test_project_persistence(client, temp_persistence):
    proj_path, _ = temp_persistence
    
    # Create project
    response = client.post("/api/projects", json={"name": "Test Proj", "color": "blue"}, headers={"X-API-Key": "mock-key"})
    assert response.status_code == 200
    data = response.json()
    pid = data["id"]
    
    # Verify file exists and has data
    assert os.path.exists(proj_path)
    with open(proj_path) as f:
        saved = json.load(f)
    assert any(p["id"] == pid for p in saved["projects"])

    # List projects
    response = client.get("/api/projects", headers={"X-API-Key": "mock-key"})
    assert any(p["id"] == pid for p in response.json())

def test_conversation_persistence(client, temp_persistence):
    _, conv_path = temp_persistence
    
    # Create conversation
    response = client.post("/api/conversations", json={"title": "Test Conv"}, headers={"X-API-Key": "mock-key"})
    assert response.status_code == 200
    data = response.json()
    cid = data["id"]
    pid = data["projectId"]
    
    # Verify file
    assert os.path.exists(conv_path)
    with open(conv_path) as f:
        saved = json.load(f)
    assert any(c["id"] == cid for c in saved["conversations"])

    # Patch conversation (rename)
    response = client.patch(f"/api/conversations/{cid}", json={"title": "Renamed"}, headers={"X-API-Key": "mock-key"})
    assert response.status_code == 200
    assert response.json()["title"] == "Renamed"
    
    # Verify file updated
    with open(conv_path) as f:
        saved = json.load(f)
    assert any(c["id"] == cid and c["title"] == "Renamed" for c in saved["conversations"])

def test_move_conversation_between_projects(client, temp_persistence):
    proj_path, conv_path = temp_persistence
    
    # Create two projects
    p1 = client.post("/api/projects", json={"name": "P1"}, headers={"X-API-Key": "mock-key"}).json()["id"]
    p2 = client.post("/api/projects", json={"name": "P2"}, headers={"X-API-Key": "mock-key"}).json()["id"]
    
    # Create conversation in P1
    c1 = client.post("/api/conversations", json={"title": "C1", "projectId": p1}, headers={"X-API-Key": "mock-key"}).json()["id"]
    
    # Move to P2
    response = client.patch(f"/api/conversations/{c1}", json={"projectId": p2}, headers={"X-API-Key": "mock-key"})
    assert response.status_code == 200
    assert response.json()["projectId"] == p2
    
    # Verify in persistence
    with open(proj_path) as f:
        projs = json.load(f)["projects"]
    
    p1_data = next(p for p in projs if p["id"] == p1)
    p2_data = next(p for p in projs if p["id"] == p2)
    
    assert c1 not in p1_data["conversationIds"]
    assert c1 in p2_data["conversationIds"]
