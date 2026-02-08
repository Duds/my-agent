"use client"

import React from "react"

import { useState } from "react"
import {
  Plus,
  Search,
  FolderOpen,
  MessageSquare,
  ChevronDown,
  ChevronRight,
  Hash,
  Bot,
  Clock,
  Zap,
  Play,
  Pause,
  AlertTriangle,
  Cpu,
  Globe,
  Eye,
  Webhook,
  CalendarClock,
  Radio,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import type {
  Project,
  Conversation,
  AgentProcess,
  CronJob,
  Automation,
} from "@/lib/store"

interface AppSidebarProps {
  projects: Project[]
  conversations: Conversation[]
  activeConversationId: string | null
  onSelectConversation: (id: string) => void
  onNewConversation: () => void
  collapsed: boolean
  agentProcesses: AgentProcess[]
  cronJobs: CronJob[]
  automations: Automation[]
}

export function AppSidebar({
  projects,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  collapsed,
  agentProcesses,
  cronJobs,
  automations,
}: AppSidebarProps) {
  const [activeTab, setActiveTab] = useState<"chats" | "agents">("chats")
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(
    new Set(projects.map((p) => p.id))
  )
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["agents", "cron", "automations"])
  )
  const [searchQuery, setSearchQuery] = useState("")

  const toggleProject = (id: string) => {
    setExpandedProjects((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const toggleSection = (id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const filteredConversations = searchQuery
    ? conversations.filter((c) =>
        c.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : conversations

  const getProjectConversations = (project: Project) =>
    filteredConversations.filter((c) =>
      project.conversationIds.includes(c.id)
    )

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return "now"
    if (mins < 60) return `${mins}m`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours}h`
    const days = Math.floor(hours / 24)
    return `${days}d`
  }

  const formatDuration = (start: Date) => {
    const diff = Date.now() - start.getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return "<1m"
    if (mins < 60) return `${mins}m`
    const hours = Math.floor(mins / 60)
    return `${hours}h ${mins % 60}m`
  }

  const runningAgents = agentProcesses.filter((a) => a.status === "running")
  const activeCrons = cronJobs.filter((c) => c.status === "active")
  const activeAutomations = automations.filter((a) => a.status === "active")
  const totalActive = runningAgents.length + activeCrons.length + activeAutomations.length

  // Collapsed state
  if (collapsed) {
    return (
      <aside className="flex h-full w-14 flex-col items-center border-r border-border bg-card py-3 gap-2">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={activeTab === "chats" ? "secondary" : "ghost"}
                size="icon"
                className="h-9 w-9"
                onClick={() => setActiveTab("chats")}
              >
                <MessageSquare className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Chats</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={activeTab === "agents" ? "secondary" : "ghost"}
                size="icon"
                className="relative h-9 w-9"
                onClick={() => setActiveTab("agents")}
              >
                <Bot className="h-4 w-4" />
                {runningAgents.length > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-primary text-[8px] font-bold text-primary-foreground">
                    {runningAgents.length}
                  </span>
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              Agents & Automations
              {runningAgents.length > 0 && ` (${runningAgents.length} running)`}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <Separator className="w-6" />
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                onClick={onNewConversation}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">New Chat</TooltipContent>
          </Tooltip>
        </TooltipProvider>
        {activeTab === "chats" &&
          projects.map((project) => (
            <TooltipProvider key={project.id}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    className="flex h-8 w-8 items-center justify-center rounded-md text-xs font-semibold transition-colors hover:bg-accent"
                    style={{ color: project.color }}
                  >
                    {project.name.charAt(0)}
                  </button>
                </TooltipTrigger>
                <TooltipContent side="right">{project.name}</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          ))}
      </aside>
    )
  }

  return (
    <aside className="flex h-full w-72 flex-col border-r border-border bg-card">
      {/* Tabs */}
      <div className="p-3 pb-0">
        <Tabs
          value={activeTab}
          onValueChange={(v) => setActiveTab(v as "chats" | "agents")}
        >
          <TabsList className="w-full h-8">
            <TabsTrigger value="chats" className="flex-1 text-xs gap-1.5 h-6">
              <MessageSquare className="h-3 w-3" />
              Chats
            </TabsTrigger>
            <TabsTrigger
              value="agents"
              className="flex-1 text-xs gap-1.5 h-6"
            >
              <Bot className="h-3 w-3" />
              Agents
              {totalActive > 0 && (
                <Badge
                  variant="secondary"
                  className="h-4 min-w-4 px-1 text-[9px] font-bold"
                >
                  {totalActive}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Search */}
      <div className="px-3 py-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder={
              activeTab === "chats"
                ? "Search conversations..."
                : "Search agents..."
            }
            className="h-8 pl-8 text-xs"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 px-1.5">
        {activeTab === "chats" ? (
          /* Chats tab */
          <div className="space-y-0.5 pb-4">
            {/* New chat button */}
            <Button
              variant="ghost"
              className="w-full justify-start gap-2 px-2 py-1.5 h-auto text-xs text-muted-foreground"
              onClick={onNewConversation}
            >
              <Plus className="h-3 w-3" />
              New conversation
            </Button>
            <Separator className="my-1" />
            {projects.map((project) => {
              const projConvs = getProjectConversations(project)
              const isExpanded = expandedProjects.has(project.id)
              return (
                <div key={project.id}>
                  <button
                    onClick={() => toggleProject(project.id)}
                    className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
                  >
                    {isExpanded ? (
                      <ChevronDown className="h-3 w-3 shrink-0" />
                    ) : (
                      <ChevronRight className="h-3 w-3 shrink-0" />
                    )}
                    <FolderOpen
                      className="h-3 w-3 shrink-0"
                      style={{ color: project.color }}
                    />
                    <span className="truncate">{project.name}</span>
                    <span className="ml-auto text-[10px] tabular-nums text-muted-foreground/60">
                      {projConvs.length}
                    </span>
                  </button>
                  {isExpanded && (
                    <div className="ml-3 space-y-px">
                      {projConvs.map((conv) => (
                        <button
                          key={conv.id}
                          onClick={() => onSelectConversation(conv.id)}
                          className={cn(
                            "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs transition-colors",
                            activeConversationId === conv.id
                              ? "bg-accent text-accent-foreground"
                              : "text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground"
                          )}
                        >
                          {conv.persona ? (
                            <Hash className="h-3 w-3 shrink-0" />
                          ) : (
                            <MessageSquare className="h-3 w-3 shrink-0" />
                          )}
                          <span className="truncate">{conv.title}</span>
                          <span className="ml-auto text-[10px] tabular-nums text-muted-foreground/50">
                            {formatTime(conv.updatedAt)}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          /* Agents tab - Automation Hub */
          <div className="space-y-0.5 pb-4">
            <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Automation Hub
            </div>
            {/* Background Agents */}
            <SectionHeader
              icon={Bot}
              label="Background Agents"
              count={runningAgents.length}
              countVariant="running"
              expanded={expandedSections.has("agents")}
              onToggle={() => toggleSection("agents")}
            />
            {expandedSections.has("agents") && (
              <div className="ml-1 space-y-px">
                {agentProcesses
                  .filter(
                    (a) =>
                      !searchQuery ||
                      a.name.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  .length > 0 ? (
                  agentProcesses
                    .filter(
                      (a) =>
                        !searchQuery ||
                        a.name.toLowerCase().includes(searchQuery.toLowerCase())
                    )
                    .map((agent) => (
                      <AgentItem
                        key={agent.id}
                        agent={agent}
                        projects={projects}
                        formatDuration={formatDuration}
                      />
                    ))
                ) : (
                  <p className="px-2 py-3 text-[10px] text-muted-foreground italic">
                    No agents configured. Add from Settings when available.
                  </p>
                )}
              </div>
            )}

            <Separator className="my-1.5" />

            {/* Cron Jobs */}
            <SectionHeader
              icon={Clock}
              label="Cron Jobs"
              count={activeCrons.length}
              countVariant="active"
              expanded={expandedSections.has("cron")}
              onToggle={() => toggleSection("cron")}
            />
            {expandedSections.has("cron") && (
              <div className="ml-1 space-y-px">
                {cronJobs
                  .filter(
                    (c) =>
                      !searchQuery ||
                      c.name.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  .length > 0 ? (
                  cronJobs
                    .filter(
                      (c) =>
                        !searchQuery ||
                        c.name.toLowerCase().includes(searchQuery.toLowerCase())
                    )
                    .map((cron) => (
                      <CronItem
                        key={cron.id}
                        cron={cron}
                        projects={projects}
                        formatTime={formatTime}
                      />
                    ))
                ) : (
                  <p className="px-2 py-3 text-[10px] text-muted-foreground italic">
                    No cron jobs configured. Add from Settings when available.
                  </p>
                )}
              </div>
            )}

            <Separator className="my-1.5" />

            {/* Automations */}
            <SectionHeader
              icon={Zap}
              label="Automations"
              count={activeAutomations.length}
              countVariant="active"
              expanded={expandedSections.has("automations")}
              onToggle={() => toggleSection("automations")}
            />
            {expandedSections.has("automations") && (
              <div className="ml-1 space-y-px">
                {automations
                  .filter(
                    (a) =>
                      !searchQuery ||
                      a.name.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  .length > 0 ? (
                  automations
                    .filter(
                      (a) =>
                        !searchQuery ||
                        a.name.toLowerCase().includes(searchQuery.toLowerCase())
                    )
                    .map((auto) => (
                      <AutomationItem
                        key={auto.id}
                        automation={auto}
                        projects={projects}
                        formatTime={formatTime}
                      />
                    ))
                ) : (
                  <p className="px-2 py-3 text-[10px] text-muted-foreground italic">
                    No automations configured. Add from Settings when available.
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </ScrollArea>
    </aside>
  )
}

/* --- Sub-components --- */

function SectionHeader({
  icon: Icon,
  label,
  count,
  countVariant,
  expanded,
  onToggle,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  count: number
  countVariant: "running" | "active"
  expanded: boolean
  onToggle: () => void
}) {
  return (
    <button
      onClick={onToggle}
      className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
    >
      {expanded ? (
        <ChevronDown className="h-3 w-3 shrink-0" />
      ) : (
        <ChevronRight className="h-3 w-3 shrink-0" />
      )}
      <Icon className="h-3 w-3 shrink-0" />
      <span>{label}</span>
      {count > 0 && (
        <Badge
          variant="outline"
          className={cn(
            "ml-auto h-4 min-w-4 px-1 text-[9px] font-semibold border-0",
            countVariant === "running"
              ? "bg-primary/10 text-primary"
              : "bg-success/10 text-success"
          )}
        >
          {count}
        </Badge>
      )}
    </button>
  )
}

function AgentItem({
  agent,
  projects,
  formatDuration,
}: {
  agent: AgentProcess
  projects: Project[]
  formatDuration: (d: Date) => string
}) {
  const project = projects.find((p) => p.id === agent.projectId)
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={cn(
              "flex items-start gap-2.5 rounded-md px-2 py-2 text-xs transition-colors cursor-default",
              agent.status === "running"
                ? "bg-primary/[0.04] hover:bg-primary/[0.07]"
                : "hover:bg-accent/50"
            )}
          >
            {/* Status dot */}
            <div className="mt-1 shrink-0">
              <span
                className={cn(
                  "block h-2 w-2 rounded-full",
                  agent.status === "running" &&
                    "bg-primary animate-pulse-dot",
                  agent.status === "idle" && "bg-muted-foreground/40",
                  agent.status === "error" && "bg-destructive"
                )}
              />
            </div>
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span
                  className={cn(
                    "font-medium truncate",
                    agent.status === "running"
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {agent.name}
                </span>
                {agent.type === "internal" ? (
                  <Cpu className="h-2.5 w-2.5 shrink-0 text-success" />
                ) : (
                  <Globe className="h-2.5 w-2.5 shrink-0 text-warning" />
                )}
              </div>
              <div className="flex items-center gap-1.5 mt-0.5 text-[10px] text-muted-foreground">
                <span className="font-mono">{agent.model}</span>
                {agent.startedAt && agent.status === "running" && (
                  <>
                    <span>{'/'}</span>
                    <span>{formatDuration(agent.startedAt)}</span>
                  </>
                )}
              </div>
              {project && (
                <div className="flex items-center gap-1 mt-1">
                  <span
                    className="h-1.5 w-1.5 rounded-full shrink-0"
                    style={{ backgroundColor: project.color }}
                  />
                  <span className="text-[10px] text-muted-foreground/60 truncate">
                    {project.name}
                  </span>
                </div>
              )}
            </div>
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="max-w-52">
          <p className="font-medium">{agent.name}</p>
          {agent.description && (
            <p className="text-muted-foreground mt-0.5">{agent.description}</p>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

function CronItem({
  cron,
  projects,
  formatTime,
}: {
  cron: CronJob
  projects: Project[]
  formatTime: (d: Date) => string
}) {
  const project = projects.find((p) => p.id === cron.projectId)
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-start gap-2.5 rounded-md px-2 py-2 text-xs transition-colors cursor-default hover:bg-accent/50">
            {/* Status icon */}
            <div className="mt-0.5 shrink-0">
              {cron.status === "active" ? (
                <Play className="h-3 w-3 text-success" />
              ) : cron.status === "paused" ? (
                <Pause className="h-3 w-3 text-muted-foreground" />
              ) : (
                <AlertTriangle className="h-3 w-3 text-destructive" />
              )}
            </div>
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span
                  className={cn(
                    "font-medium truncate",
                    cron.status === "active"
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {cron.name}
                </span>
              </div>
              <div className="flex items-center gap-1.5 mt-0.5 text-[10px] text-muted-foreground">
                <code className="font-mono bg-secondary px-1 rounded">
                  {cron.schedule}
                </code>
              </div>
              <div className="flex items-center gap-2 mt-1 text-[10px] text-muted-foreground/60">
                {cron.lastRun && (
                  <span>ran {formatTime(cron.lastRun)} ago</span>
                )}
                {project && (
                  <div className="flex items-center gap-1">
                    <span
                      className="h-1.5 w-1.5 rounded-full shrink-0"
                      style={{ backgroundColor: project.color }}
                    />
                    <span className="truncate">{project.name}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="max-w-52">
          <p className="font-medium">{cron.name}</p>
          <p className="text-muted-foreground mt-0.5">{cron.description}</p>
          <p className="text-muted-foreground mt-1">
            Next run: {cron.nextRun.toLocaleDateString()}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

const AUTOMATION_TYPE_ICONS: Record<
  Automation["type"],
  React.ComponentType<{ className?: string }>
> = {
  webhook: Webhook,
  event: Radio,
  schedule: CalendarClock,
  watch: Eye,
}

function AutomationItem({
  automation,
  projects,
  formatTime,
}: {
  automation: Automation
  projects: Project[]
  formatTime: (d: Date) => string
}) {
  const project = projects.find((p) => p.id === automation.projectId)
  const TypeIcon = AUTOMATION_TYPE_ICONS[automation.type]
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-start gap-2.5 rounded-md px-2 py-2 text-xs transition-colors cursor-default hover:bg-accent/50">
            {/* Type icon */}
            <div className="mt-0.5 shrink-0">
              <TypeIcon
                className={cn(
                  "h-3 w-3",
                  automation.status === "active"
                    ? "text-primary"
                    : automation.status === "paused"
                      ? "text-muted-foreground"
                      : "text-destructive"
                )}
              />
            </div>
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span
                  className={cn(
                    "font-medium truncate",
                    automation.status === "active"
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {automation.name}
                </span>
                {automation.runsToday > 0 && (
                  <Badge
                    variant="outline"
                    className="h-3.5 px-1 text-[8px] font-mono border-0 bg-secondary text-secondary-foreground"
                  >
                    {automation.runsToday}x
                  </Badge>
                )}
              </div>
              <div className="mt-0.5 text-[10px] text-muted-foreground font-mono truncate">
                {automation.trigger}
              </div>
              <div className="flex items-center gap-2 mt-1 text-[10px] text-muted-foreground/60">
                {automation.lastTriggered && (
                  <span>{formatTime(automation.lastTriggered)} ago</span>
                )}
                {project && (
                  <div className="flex items-center gap-1">
                    <span
                      className="h-1.5 w-1.5 rounded-full shrink-0"
                      style={{ backgroundColor: project.color }}
                    />
                    <span className="truncate">{project.name}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="max-w-52">
          <p className="font-medium">{automation.name}</p>
          <p className="text-muted-foreground mt-0.5">
            {automation.description}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
