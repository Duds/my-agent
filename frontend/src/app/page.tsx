"use client";

import { useState, useCallback, useEffect } from "react";
import {
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";
import { AppSidebar } from "@/components/app-sidebar";
import { ChatInterface } from "@/components/chat-interface";
import { ModelSelector } from "@/components/model-selector";
import { StatusBar } from "@/components/status-bar";
import { SettingsPanel } from "@/components/settings-panel";
import { PersonaSelector, PersonaBadge } from "@/components/persona-selector";
import { ThemeToggle } from "@/components/theme-toggle";
import { api } from "@/lib/api-client";
import type {
  Conversation,
  Message,
  Skill,
  Model,
  Persona,
  Project,
  AgentProcess,
  CronJob,
  Automation,
  MCP,
  Integration,
} from "@/lib/store";

function parseConversation(c: {
  id: string;
  title: string;
  projectId: string;
  messages: { id: string; role: string; content: string; timestamp: string; model?: string; toolCalls?: { name: string; status: string }[] }[];
  createdAt: string;
  updatedAt: string;
  persona?: string;
}): Conversation {
  return {
    ...c,
    messages: c.messages.map((m) => ({
      ...m,
      role: m.role as "user" | "assistant" | "system",
      timestamp: new Date(m.timestamp),
      toolCalls: m.toolCalls as { name: string; status: "running" | "complete" | "error" }[] | undefined,
    })),
    createdAt: new Date(c.createdAt),
    updatedAt: new Date(c.updatedAt),
  };
}

export default function Page() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [personaDialogOpen, setPersonaDialogOpen] = useState(false);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [selectedModelId, setSelectedModelId] = useState<string>("");
  const [selectedPersonaId, setSelectedPersonaId] = useState("coder");
  const [agenticMode, setAgenticMode] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [models, setModels] = useState<Model[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [agentProcesses, setAgentProcesses] = useState<AgentProcess[]>([]);
  const [cronJobs, setCronJobs] = useState<CronJob[]>([]);
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [mcps, setMcps] = useState<MCP[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>([]);

  const activeConversation = conversations.find((c) => c.id === activeConversationId) ?? null;
  const selectedModel = models.find((m) => m.id === selectedModelId) ?? models[0] ?? null;
  const selectedPersona = personas.find((p) => p.id === selectedPersonaId) ?? personas[0] ?? null;

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [m, p, s, proj, conv, ap, cj, auto, mcpsRes, intRes] = await Promise.all([
          api.getModels(),
          api.getPersonas(),
          api.getSkills(),
          api.getProjects(),
          api.getConversations(),
          api.getAgentProcesses(),
          api.getCronJobs(),
          api.getAutomations(),
          api.getMcps(),
          api.getIntegrations(),
        ]);
        setModels(m);
        setPersonas(p);
        setSkills(s);
        setProjects(proj);
        setConversations(conv.map(parseConversation));
        setAgentProcesses(ap.map((a) => ({ ...a, startedAt: a.startedAt ? new Date(a.startedAt) : undefined })));
        setCronJobs(cj.map((c) => ({ ...c, lastRun: c.lastRun ? new Date(c.lastRun) : null, nextRun: new Date(c.nextRun) })));
        setAutomations(auto.map((a) => ({ ...a, lastTriggered: a.lastTriggered ? new Date(a.lastTriggered) : null })));
        setMcps(mcpsRes);
        setIntegrations(intRes);
        if (m.length > 0 && !selectedModelId) setSelectedModelId(m[0].id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional: load once on mount
  }, []);

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!activeConversationId) return;

      const userMessage: Message = {
        id: `m-${Date.now()}`,
        role: "user",
        content,
        timestamp: new Date(),
      };

      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeConversationId
            ? { ...c, messages: [...c.messages, userMessage], updatedAt: new Date() }
            : c
        )
      );
      setIsStreaming(true);

      try {
        const res = await api.postQuery(content);
        const assistantMessage: Message = {
          id: `m-${Date.now() + 1}`,
          role: "assistant",
          content: res.answer,
          timestamp: new Date(),
          model: res.routing?.adapter,
        };
        setConversations((prev) =>
          prev.map((c) =>
            c.id === activeConversationId
              ? { ...c, messages: [...c.messages, assistantMessage], updatedAt: new Date() }
              : c
          )
        );
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : "Request failed";
        const errorMessage: Message = {
          id: `m-${Date.now() + 1}`,
          role: "assistant",
          content: `Error: ${errMsg}`,
          timestamp: new Date(),
        };
        setConversations((prev) =>
          prev.map((c) =>
            c.id === activeConversationId
              ? { ...c, messages: [...c.messages, errorMessage], updatedAt: new Date() }
              : c
          )
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [activeConversationId]
  );

  const handleNewConversation = useCallback(() => {
    const newConv: Conversation = {
      id: `conv-${Date.now()}`,
      title: "New conversation",
      projectId: projects[0]?.id ?? "proj-1",
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      persona: selectedPersonaId,
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
  }, [selectedPersonaId, projects]);

  const handleToggleSkill = useCallback((id: string) => {
    setSkills((prev) =>
      prev.map((s) => (s.id === id ? { ...s, enabled: !s.enabled } : s))
    );
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-background p-8">
        <p className="text-destructive">{error}</p>
        <p className="text-sm text-muted-foreground">
          Ensure the backend is running on port 8001 (or set NEXT_PUBLIC_API_URL).
        </p>
      </div>
    );
  }

  return (
    <TooltipProvider delayDuration={0}>
      <div className="flex h-screen flex-col bg-background">
        <div className="flex flex-1 overflow-hidden">
          <AppSidebar
            projects={projects}
            conversations={conversations}
            activeConversationId={activeConversationId}
            onSelectConversation={setActiveConversationId}
            onNewConversation={handleNewConversation}
            collapsed={sidebarCollapsed}
            agentProcesses={agentProcesses}
            cronJobs={cronJobs}
            automations={automations}
          />

          <div className="flex flex-1 flex-col overflow-hidden">
            <header className="flex h-12 items-center justify-between border-b border-border bg-card px-3">
              <div className="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                    >
                      {sidebarCollapsed ? (
                        <PanelLeftOpen className="h-4 w-4" />
                      ) : (
                        <PanelLeftClose className="h-4 w-4" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    {sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                  </TooltipContent>
                </Tooltip>

                {activeConversation && (
                  <div className="ml-1 flex items-center gap-2">
                    <h1 className="max-w-48 truncate text-sm font-medium text-foreground">
                      {activeConversation.title}
                    </h1>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-1">
                {selectedPersona && (
                  <PersonaBadge
                    persona={selectedPersona}
                    onClick={() => setPersonaDialogOpen(true)}
                  />
                )}

                <ModelSelector
                  models={models}
                  selectedModelId={selectedModelId}
                  onSelectModel={setSelectedModelId}
                  agenticMode={agenticMode}
                  onToggleAgenticMode={() => setAgenticMode(!agenticMode)}
                />

                <ThemeToggle />

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => setSettingsOpen(!settingsOpen)}
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Settings</TooltipContent>
                </Tooltip>
              </div>
            </header>

            <div className="flex flex-1 overflow-hidden">
              <ChatInterface
                conversation={activeConversation}
                onSendMessage={handleSendMessage}
                isStreaming={isStreaming}
              />

              <SettingsPanel
                open={settingsOpen}
                onClose={() => setSettingsOpen(false)}
                models={models}
                skills={skills}
                mcps={mcps}
                integrations={integrations}
                onToggleSkill={handleToggleSkill}
              />
            </div>
          </div>
        </div>

        <StatusBar
          activeModel={selectedModel}
          agentProcesses={agentProcesses}
          agenticMode={agenticMode}
        />

        <PersonaSelector
          personas={personas}
          selectedPersonaId={selectedPersonaId}
          onSelectPersona={setSelectedPersonaId}
          open={personaDialogOpen}
          onOpenChange={setPersonaDialogOpen}
        />
      </div>
    </TooltipProvider>
  );
}
