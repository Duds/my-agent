from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class RoutingMeta(BaseModel):
    intent: str
    adapter: str
    requires_privacy: bool

class SecurityInfo(BaseModel):
    is_safe: bool
    reason: Optional[str] = None

class AgentGeneratedMeta(BaseModel):
    """Present when CREATE_AGENT intent returns valid generated code for review."""

    code: str
    agent_id: str
    agent_name: str
    valid: bool


class QueryResponse(BaseModel):
    status: str
    routing: RoutingMeta
    answer: str
    security: SecurityInfo
    agent_generated: Optional[AgentGeneratedMeta] = None

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    type: Optional[str] = None  # 'commercial' | 'ollama' | 'local'
    status: Optional[str] = None  # 'online' | 'offline' | 'loading'
    contextWindow: Optional[str] = None
    # Metadata for informed model selection
    tags: Optional[List[str]] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    benefits: Optional[str] = None

class ModelsResponse(BaseModel):
    remote: List[ModelInfo]
    local: List[ModelInfo]
    active_local_default: str

class ModeInfo(BaseModel):
    id: str
    name: str
    description: str
    routing: str

class SkillInfo(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool

class MCPInfo(BaseModel):
    id: str
    name: str
    endpoint: str
    status: str
    description: str

class IntegrationInfo(BaseModel):
    id: str
    name: str
    type: str
    status: str
    description: str


class TelegramSendBody(BaseModel):
    """Body for POST /api/telegram/send. Send message to primary chat."""

    message: Optional[str] = None
    text: Optional[str] = None  # Alias for message


class ConnectServiceBody(BaseModel):
    """Body for POST /api/integrations/{provider}/connect."""

    api_key: str


class ConnectServiceResponse(BaseModel):
    """Response from connect and discover."""

    success: bool
    provider: str
    models: List[dict] = []
    error: Optional[str] = None


class AIServiceStatus(BaseModel):
    """Status of an AI provider (Anthropic, Mistral, Moonshot)."""

    provider: str
    display_name: str
    connected: bool
    model_count: int

class ProjectInfo(BaseModel):
    id: str
    name: str
    color: str
    conversationIds: List[str]

class MessageInfo(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str
    model: Optional[str] = None
    toolCalls: Optional[List[Dict[str, str]]] = None

class ConversationInfo(BaseModel):
    id: str
    title: str
    projectId: str
    messages: List[MessageInfo]
    createdAt: str
    updatedAt: str
    modeId: Optional[str] = None

class AgentProcessInfo(BaseModel):
    id: str
    name: str
    status: str
    type: str
    model: str
    projectId: Optional[str] = None
    startedAt: Optional[str] = None
    description: Optional[str] = None

class CronJobInfo(BaseModel):
    id: str
    name: str
    schedule: str
    status: str
    lastRun: Optional[str] = None
    nextRun: str
    projectId: Optional[str] = None
    description: str
    model: Optional[str] = None

class AutomationInfo(BaseModel):
    id: str
    name: str
    trigger: str
    status: str
    lastTriggered: Optional[str] = None
    runsToday: int
    projectId: Optional[str] = None
    description: str
    type: str
