/**
 * API Request and Response interfaces for the MyAgent platform.
 */

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  type?: 'commercial' | 'local' | 'ollama';
  contextWindow?: string;
  status?: 'online' | 'offline' | 'loading';
  /** Tags for filtering and quick scanning (e.g. coding, fast, privacy) */
  tags?: string[];
  /** Strengths of this model */
  pros?: string[];
  /** Limitations to consider */
  cons?: string[];
  /** One-line summary of when to use */
  benefits?: string;
}

export interface ModelsResponse {
  remote: ModelInfo[];
  local: ModelInfo[];
  active_local_default: string;
}

export interface ModeInfo {
  id: string;
  name: string;
  description: string;
  routing: string;
}

export interface SkillInfo {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
}

export interface MCPInfo {
  id: string;
  name: string;
  endpoint: string;
  status: 'connected' | 'disconnected' | 'error';
  description: string;
}

export interface IntegrationInfo {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'error';
  description: string;
}

export interface ProjectInfo {
  id: string;
  name: string;
  color: string;
  conversationIds: string[];
}

export interface MessageInfo {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  model?: string;
  toolCalls?: { name: string; status: 'running' | 'complete' | 'error' }[];
}

export interface ConversationInfo {
  id: string;
  title: string;
  projectId: string;
  /** Session ID (default 'main'); first-class for continuity (PBI-046). */
  sessionId?: string;
  messages: MessageInfo[];
  createdAt: string;
  updatedAt: string;
  persona?: string;
  modeId?: string;
}

export interface AgentProcessInfo {
  id: string;
  name: string;
  status: 'running' | 'idle' | 'error';
  type: 'internal' | 'external';
  model: string;
  projectId?: string;
  startedAt?: string;
  description?: string;
}

export interface CronJobInfo {
  id: string;
  name: string;
  schedule: string;
  status: 'active' | 'paused' | 'error';
  lastRun: string | null;
  nextRun: string;
  projectId?: string;
  description: string;
  model?: string;
}

export interface AutomationInfo {
  id: string;
  name: string;
  trigger: string;
  status: 'active' | 'paused' | 'error';
  lastTriggered: string | null;
  runsToday: number;
  projectId?: string;
  description: string;
  type: 'webhook' | 'event' | 'schedule' | 'watch';
}

export interface ScriptInfo {
  id: string;
  name: string;
  type: string;
  status: string;
  lastRun?: string | null;
  source?: string | null;
}

export interface ExecutionLogEntry {
  id: string;
  scriptId: string;
  timestamp: string;
  status: string;
  message?: string | null;
  durationMs?: number | null;
}

export interface ErrorReportEntry {
  id: string;
  scriptId: string;
  timestamp: string;
  message: string;
  severity?: string | null;
}

export interface QueryRequest {
  text: string;
  model_id?: string;
  mode_id?: string;
  session_id?: string;
}

/** Present when CREATE_AGENT intent returns valid generated code for review. */
export interface AgentGeneratedMeta {
  code: string;
  agent_id: string;
  agent_name: string;
  valid: boolean;
}

export interface QueryResponse {
  status: string;
  routing: {
    intent: string;
    adapter: string;
    requires_privacy: boolean;
  };
  answer: string;
  security: {
    is_safe: boolean;
    reason?: string;
  };
  agent_generated?: AgentGeneratedMeta;
}

export interface StreamChunk {
  chunk?: string;
  done?: boolean;
  routing?: {
    intent: string;
    adapter: string;
    requires_privacy: boolean;
    agent_generated?: AgentGeneratedMeta;
  };
  error?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export interface AIServiceStatus {
  provider: string;
  display_name: string;
  connected: boolean;
  model_count: number;
}

export interface ConnectServiceResponse {
  success: boolean;
  provider: string;
  models: { id: string; name: string; contextWindow?: string }[];
  error?: string;
}
