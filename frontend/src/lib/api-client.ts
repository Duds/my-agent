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
  getSkills: () => fetchApi<Skill[]>("/api/skills"),
  getMcps: () => fetchApi<MCP[]>("/api/mcps"),
  getIntegrations: () => fetchApi<Integration[]>("/api/integrations"),
  getProjects: () => fetchApi<Project[]>("/api/projects"),
  getConversations: () => fetchApi<Conversation[]>("/api/conversations"),
  getAgentProcesses: () => fetchApi<AgentProcess[]>("/api/agent-processes"),
  getCronJobs: () => fetchApi<CronJob[]>("/api/cron-jobs"),
  getAutomations: () => fetchApi<Automation[]>("/api/automations"),
  postQuery: async (text: string, apiKey?: string) => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (apiKey) headers["X-API-Key"] = apiKey;
    const res = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers,
      body: JSON.stringify({ text }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Query failed: ${res.statusText}`);
    }
    return res.json();
  },
  getHealth: () => fetchApi<{ status: string; service: string }>("/health"),
};
