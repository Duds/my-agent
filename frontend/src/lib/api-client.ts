/**
 * API client for the Secure Personal Agentic Platform backend.
 * All data is fetched from real backend endpoints - no mock data.
 */

const API_BASE =
  typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001")
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export interface Model {
  id: string;
  name: string;
  provider: string;
  type: "commercial" | "local" | "ollama";
  contextWindow: string;
  status: "online" | "offline" | "loading";
}

export interface Persona {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  icon: string;
  color: string;
}

export interface Mode {
  id: string;
  name: string;
  description: string;
  routing: string;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
}

export interface MCP {
  id: string;
  name: string;
  endpoint: string;
  status: "connected" | "disconnected" | "error";
  description: string;
}

export interface Integration {
  id: string;
  name: string;
  type: string;
  status: "active" | "inactive" | "error";
  description: string;
}

export interface Project {
  id: string;
  name: string;
  color: string;
  conversationIds: string[];
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  model?: string;
  toolCalls?: { name: string; status: "running" | "complete" | "error" }[];
}

export interface Conversation {
  id: string;
  title: string;
  projectId: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
  persona?: string;
}

export interface AgentProcess {
  id: string;
  name: string;
  status: "running" | "idle" | "error";
  type: "internal" | "external";
  model: string;
  projectId?: string;
  startedAt?: string;
  description?: string;
}

export interface CronJob {
  id: string;
  name: string;
  schedule: string;
  status: "active" | "paused" | "error";
  lastRun: string | null;
  nextRun: string;
  projectId?: string;
  description: string;
  model?: string;
}

export interface Automation {
  id: string;
  name: string;
  trigger: string;
  status: "active" | "paused" | "error";
  lastTriggered: string | null;
  runsToday: number;
  projectId?: string;
  description: string;
  type: "webhook" | "event" | "schedule" | "watch";
}

export const api = {
  getModels: () => fetchApi<Model[]>("/api/models"),
  getPersonas: () => fetchApi<Persona[]>("/api/personas"),
  getModes: () => fetchApi<Mode[]>("/api/modes"),
  getSkills: () => fetchApi<Skill[]>("/api/skills"),
  getMcps: () => fetchApi<MCP[]>("/api/mcps"),
  getIntegrations: () => fetchApi<Integration[]>("/api/integrations"),
  getProjects: () => fetchApi<Project[]>("/api/projects"),
  getConversations: () => fetchApi<Conversation[]>("/api/conversations"),
  getAgentProcesses: () => fetchApi<AgentProcess[]>("/api/agent-processes"),
  getCronJobs: () => fetchApi<CronJob[]>("/api/cron-jobs"),
  getAutomations: () => fetchApi<Automation[]>("/api/automations"),
  postQuery: async (
    text: string,
    options?: {
      apiKey?: string;
      modelId?: string;
      modeId?: string;
      sessionId?: string;
    }
  ) => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (options?.apiKey) headers["X-API-Key"] = options.apiKey;
    const body: Record<string, string> = { text };
    if (options?.modelId) body.model_id = options.modelId;
    if (options?.modeId) body.mode_id = options.modeId;
    if (options?.sessionId) body.session_id = options.sessionId;
    const res = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Query failed: ${res.statusText}`);
    }
    return res.json();
  },

  /**
   * Stream query response (SSE). Use for lower perceived latency with Ollama.
   * Calls onChunk for each token and onDone with final routing info.
   */
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
      "Content-Type": "application/json",
    };
    if (options?.apiKey) headers["X-API-Key"] = options.apiKey;
    const body: Record<string, string> = { text };
    if (options?.modelId) body.model_id = options.modelId;
    if (options?.modeId) body.mode_id = options.modeId;
    if (options?.sessionId) body.session_id = options.sessionId;
    const res = await fetch(`${API_BASE}/query/stream`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Query failed: ${res.statusText}`);
    }
    const reader = res.body?.getReader();
    if (!reader) throw new Error("No response body");
    const decoder = new TextDecoder();
    let buffer = "";
    let routing: { intent: string; adapter: string } | undefined;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6)) as {
              chunk?: string;
              done?: boolean;
              routing?: { intent: string; adapter: string };
              error?: string;
            };
            if (data.chunk) onChunk(data.chunk);
            if (data.done && data.routing) routing = data.routing;
            if (data.error) throw new Error(data.error);
          } catch (e) {
            if (e instanceof Error && e.message !== "Unexpected end of JSON input") throw e;
          }
        }
      }
    }
    return { routing };
  },
  getHealth: () => fetchApi<{ status: string; service: string }>("/health"),
  patchSkill: async (skillId: string, enabled: boolean) => {
    const res = await fetch(`${API_BASE}/api/skills/${skillId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `PATCH failed: ${res.statusText}`);
    }
    return res.json();
  },
  postConversation: async (body: {
    title?: string;
    projectId?: string;
    modeId?: string;
  }) => {
    const res = await fetch(`${API_BASE}/api/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `POST failed: ${res.statusText}`);
    }
    return res.json();
  },
  patchConversation: async (
    conversationId: string,
    body: { title?: string; messages?: unknown[] }
  ) => {
    const res = await fetch(`${API_BASE}/api/conversations/${conversationId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `PATCH failed: ${res.statusText}`);
    }
    return res.json();
  },
};
