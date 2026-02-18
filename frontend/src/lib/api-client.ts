/**
 * API client for the Secure Personal Agentic Platform backend.
 * All data is fetched from real backend endpoints - no mock data.
 */

import {
  ModelInfo,
  ModelsResponse,
  ModeInfo,
  SkillInfo,
  MCPInfo,
  IntegrationInfo,
  MessageInfo,
  ConversationInfo,
  QueryRequest,
  QueryResponse,
  StreamChunk,
  HealthResponse,
  AgentProcessInfo,
  CronJobInfo,
  AutomationInfo,
  AgentGeneratedMeta,
} from '@/types/api';

const API_BASE =
  typeof window !== 'undefined'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
    : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (apiKey && !headers.has('X-API-Key')) {
    headers.set('X-API-Key', apiKey);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(
      errorBody.detail || `API error ${res.status}: ${res.statusText}`
    );
  }
  return res.json();
}

export type Model = ModelInfo;
export type Mode = ModeInfo;
export type Skill = SkillInfo;
export type MCP = MCPInfo;
export type Integration = IntegrationInfo;
export interface ProjectInfo {
  id: string;
  name: string;
  color: string;
  conversationIds: string[];
  is_vault?: boolean;
}
export type Project = ProjectInfo;
export type Persona = ModeInfo; // Deprecated, but used in some places

export const api = {
  getModels: () =>
    fetchApi<ModelsResponse>('/api/models').then((r) => {
      const withMeta = (m: ModelInfo, type: 'commercial' | 'ollama') => ({
        ...m,
        type: m.type ?? type,
        status: m.status ?? 'online',
        contextWindow: m.contextWindow ?? '128k',
      });
      return [
        ...r.remote.map((m) => withMeta(m, 'commercial')),
        ...r.local.map((m) => withMeta(m, 'ollama')),
      ];
    }),
  getModes: () => fetchApi<ModeInfo[]>('/api/modes'),
  getSkills: () => fetchApi<SkillInfo[]>('/api/skills'),
  getMcps: () => fetchApi<MCPInfo[]>('/api/mcps'),
  getIntegrations: () => fetchApi<IntegrationInfo[]>('/api/integrations'),
  getContext: () =>
    fetchApi<{ activeWindow: string | null; currentActivity: string | null }>(
      '/api/context'
    ),
  getProjects: () => fetchApi<ProjectInfo[]>('/api/projects'),
  createProject: (body: { name: string; color?: string }) =>
    fetchApi<ProjectInfo>('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  patchProject: (projectId: string, body: { name?: string; color?: string }) =>
    fetchApi<ProjectInfo>(`/api/projects/${projectId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  getConversations: () => fetchApi<ConversationInfo[]>('/api/conversations'),

  /** List first-class sessions (main + project-scoped) (PBI-046). */
  getSessions: () => fetchApi<{ id: string; label: string }[]>('/api/sessions'),
  getAgentProcesses: () => fetchApi<AgentProcessInfo[]>('/api/agent-processes'),
  getCronJobs: () => fetchApi<CronJobInfo[]>('/api/cron-jobs'),
  getAutomations: () => fetchApi<AutomationInfo[]>('/api/automations'),
  getScripts: () =>
    fetchApi<import('@/types/api').ScriptInfo[]>('/api/scripts'),
  getAutomationLogs: (options?: { limit?: number; scriptId?: string }) => {
    const params = new URLSearchParams();
    if (options?.limit != null) params.set('limit', String(options.limit));
    if (options?.scriptId) params.set('scriptId', options.scriptId);
    const qs = params.toString();
    return fetchApi<import('@/types/api').ExecutionLogEntry[]>(
      `/api/automation-logs${qs ? `?${qs}` : ''}`
    );
  },
  getErrorReports: (options?: { limit?: number; scriptId?: string }) => {
    const params = new URLSearchParams();
    if (options?.limit != null) params.set('limit', String(options.limit));
    if (options?.scriptId) params.set('scriptId', options.scriptId);
    const qs = params.toString();
    return fetchApi<import('@/types/api').ErrorReportEntry[]>(
      `/api/error-reports${qs ? `?${qs}` : ''}`
    );
  },

  registerAgent: (code: string) =>
    fetchApi<AgentProcessInfo>('/api/agents/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    }),

  postQuery: async (
    text: string,
    options?: {
      apiKey?: string;
      modelId?: string;
      modeId?: string;
      sessionId?: string;
    }
  ): Promise<QueryResponse> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (options?.apiKey) headers['X-API-Key'] = options.apiKey;
    const body: QueryRequest = { text };
    if (options?.modelId) body.model_id = options.modelId;
    if (options?.modeId) body.mode_id = options.modeId;
    if (options?.sessionId) body.session_id = options.sessionId;

    return fetchApi<QueryResponse>('/query', {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
  },

  postQueryStream: async (
    text: string,
    onChunk: (chunk: string) => void,
    options?: {
      apiKey?: string;
      modelId?: string;
      modeId?: string;
      sessionId?: string;
    }
  ): Promise<{
    routing?: {
      intent: string;
      adapter: string;
      agent_generated?: AgentGeneratedMeta;
    };
  }> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const apiKey = options?.apiKey || process.env.NEXT_PUBLIC_API_KEY;
    if (apiKey) headers['X-API-Key'] = apiKey;
    const body: QueryRequest = { text };
    if (options?.modelId) body.model_id = options.modelId;
    if (options?.modeId) body.mode_id = options.modeId;
    if (options?.sessionId) body.session_id = options.sessionId;

    const res = await fetch(`${API_BASE}/query/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Query failed: ${res.statusText}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No response body');
    const decoder = new TextDecoder();
    let buffer = '';
    let routing:
      | {
          intent: string;
          adapter: string;
          agent_generated?: AgentGeneratedMeta;
        }
      | undefined;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() ?? '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6)) as StreamChunk;
            if (data.chunk) onChunk(data.chunk);
            if (data.done && data.routing) {
              routing = {
                intent: data.routing.intent,
                adapter: data.routing.adapter,
                agent_generated: data.routing.agent_generated,
              };
            }
            if (data.error) throw new Error(data.error);
          } catch (e) {
            if (
              e instanceof Error &&
              e.message !== 'Unexpected end of JSON input'
            )
              throw e;
          }
        }
      }
    }
    return { routing };
  },

  getHealth: () => fetchApi<HealthResponse>('/health'),

  patchSkill: async (skillId: string, enabled: boolean): Promise<SkillInfo> => {
    return fetchApi<SkillInfo>(`/api/skills/${skillId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
  },

  postConversation: async (body: {
    title?: string;
    projectId?: string;
    modeId?: string;
    sessionId?: string;
  }): Promise<ConversationInfo> => {
    return fetchApi<ConversationInfo>('/api/conversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  },

  patchConversation: async (
    conversationId: string,
    body: { title?: string; messages?: MessageInfo[]; projectId?: string }
  ): Promise<ConversationInfo> => {
    return fetchApi<ConversationInfo>(`/api/conversations/${conversationId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  },

  getRoutingConfig: () =>
    fetchApi<Record<string, string>>('/api/config/routing'),

  updateRoutingConfig: (config: Record<string, string>) =>
    fetchApi<{ status: string; config: Record<string, string> }>(
      '/api/config/routing',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      }
    ),

  getSystemStatus: () =>
    fetchApi<{
      ollama: { status: string; port: number };
      backend: { status: string; port: number };
      frontend: { status: string; port: number };
    }>('/api/system/status'),

  startOllama: () =>
    fetchApi<{ status: string; message: string }>('/api/system/ollama/start', {
      method: 'POST',
    }),

  stopOllama: () =>
    fetchApi<{ status: string; message: string }>('/api/system/ollama/stop', {
      method: 'POST',
    }),

  stopBackend: () =>
    fetchApi<{ status: string; message: string }>('/api/system/backend/stop', {
      method: 'POST',
    }),

  getAIServices: () =>
    fetchApi<import('@/types/api').AIServiceStatus[]>(
      '/api/integrations/ai-services'
    ),

  connectAIService: async (
    provider: string,
    apiKey: string
  ): Promise<import('@/types/api').ConnectServiceResponse> => {
    return fetchApi<import('@/types/api').ConnectServiceResponse>(
      `/api/integrations/${provider}/connect`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey }),
      }
    );
  },

  disconnectAIService: (provider: string) =>
    fetchApi<{ success: boolean; provider: string }>(
      `/api/integrations/${provider}/connect`,
      { method: 'DELETE' }
    ),

  getTelegramPrimaryChat: () =>
    fetchApi<{ chat_id: string | null }>('/api/telegram/primary'),

  sendToTelegram: (message: string) =>
    fetchApi<{ status: string; chat_id: string }>('/api/telegram/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    }),

  getVaultStatus: () =>
    fetchApi<import('@/types/api').VaultStatus>('/api/vault/status'),
  unlockVault: (password: string) =>
    fetchApi<{ status: string }>('/api/vault/unlock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    }),
  lockVault: () =>
    fetchApi<{ status: string }>('/api/vault/lock', { method: 'POST' }),
  resetVault: () =>
    fetchApi<{ status: string; message: string }>('/api/vault/reset', {
      method: 'POST',
    }),
};
