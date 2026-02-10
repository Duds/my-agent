/**
 * Type definitions for the Command Center UI.
 * Data is fetched from the backend API via api-client.ts - no mock data.
 */

export type {
  Model,
  Persona,
  Mode,
  Skill,
  MCP,
  Integration,
  Project,
} from "./api-client";

/** AgentProcess with parsed Date for UI. */
export interface AgentProcess {
  id: string;
  name: string;
  status: "running" | "idle" | "error";
  type: "internal" | "external";
  model: string;
  projectId?: string;
  startedAt?: Date;
  description?: string;
}

/** CronJob with parsed Date for UI. */
export interface CronJob {
  id: string;
  name: string;
  schedule: string;
  status: "active" | "paused" | "error";
  lastRun: Date | null;
  nextRun: Date;
  projectId?: string;
  description: string;
  model?: string;
}

/** Automation with parsed Date for UI. */
export interface Automation {
  id: string;
  name: string;
  trigger: string;
  status: "active" | "paused" | "error";
  lastTriggered: Date | null;
  runsToday: number;
  projectId?: string;
  description: string;
  type: "webhook" | "event" | "schedule" | "watch";
}

/** Agent generated meta for review UI (CREATE_AGENT intent). */
export interface AgentGeneratedMeta {
  code: string;
  agent_id: string;
  agent_name: string;
  valid: boolean;
}

/** Message with parsed Date for UI. */
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  model?: string;
  toolCalls?: { name: string; status: "running" | "complete" | "error" }[];
  /** Set when CREATE_AGENT intent returns valid code for review. */
  agentGenerated?: AgentGeneratedMeta;
}

/** Conversation with parsed Date fields for UI. */
export interface Conversation {
  id: string;
  title: string;
  projectId: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  persona?: string;
}
