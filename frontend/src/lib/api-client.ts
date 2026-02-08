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
  ProjectInfo,
  MessageInfo,
  ConversationInfo,
  QueryRequest,
  QueryResponse,
  StreamChunk,
  HealthResponse,
  AgentProcessInfo,
  CronJobInfo,
  AutomationInfo,
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
export type Project = ProjectInfo;
export type Persona = ModeInfo; // Deprecated, but used in some places

export const api = {
  getModels: () =>
    fetchApi<ModelsResponse>('/api/models').then((r) => [
      ...r.remote,
      ...r.local,
    ]),
  getModes: () => fetchApi<ModeInfo[]>('/api/modes'),
  getSkills: () => fetchApi<SkillInfo[]>('/api/skills'),
  getMcps: () => fetchApi<MCPInfo[]>('/api/mcps'),
  getIntegrations: () => fetchApi<IntegrationInfo[]>('/api/integrations'),
  getProjects: () => fetchApi<ProjectInfo[]>('/api/projects'),
  getConversations: () => fetchApi<ConversationInfo[]>('/api/conversations'),
  getAgentProcesses: () => fetchApi<AgentProcessInfo[]>('/api/agent-processes'),
  getCronJobs: () => fetchApi<CronJobInfo[]>('/api/cron-jobs'),
  getAutomations: () => fetchApi<AutomationInfo[]>('/api/automations'),

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
  ): Promise<{ routing?: { intent: string; adapter: string } }> => {
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
    let routing: { intent: string; adapter: string } | undefined;

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
  }): Promise<ConversationInfo> => {
    return fetchApi<ConversationInfo>('/api/conversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  },

  patchConversation: async (
    conversationId: string,
    body: { title?: string; messages?: MessageInfo[] }
  ): Promise<ConversationInfo> => {
    return fetchApi<ConversationInfo>(`/api/conversations/${conversationId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  },
};
