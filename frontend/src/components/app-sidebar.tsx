'use client';

import React from 'react';
import Link from 'next/link';
import { useState } from 'react';
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
  MoreVertical,
  Pencil,
  FileCode,
  Lock,
  Unlock,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api-client';
import { VaultOverlay } from './vault/VaultOverlay';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from '@/components/ui/tooltip';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Label } from '@/components/ui/label';
import type {
  Project,
  Conversation,
  AgentProcess,
  CronJob,
  Automation,
} from '@/lib/store';

interface AppSidebarProps {
  projects: Project[];
  conversations: Conversation[];
  activeConversationId: string | null;
  activeProjectId: string | null;
  onSelectConversation: (id: string) => void;
  onSelectProject: (id: string) => void;
  onNewConversation: () => void;
  onMoveConversation?: (convId: string, targetProjId: string) => Promise<void>;
  onCreateProject?: (name: string, color?: string) => Promise<void>;
  onPatchProject?: (
    id: string,
    updates: { name?: string; color?: string }
  ) => Promise<void>;
  collapsed: boolean;
  agentProcesses: AgentProcess[];
  cronJobs: CronJob[];
  automations: Automation[];
}

const PROJECT_COLORS = [
  'hsl(217, 92%, 60%)',
  'hsl(142, 76%, 36%)',
  'hsl(280, 67%, 47%)',
  'hsl(25, 95%, 53%)',
  'hsl(199, 89%, 48%)',
];

export function AppSidebar({
  projects,
  conversations,
  activeConversationId,
  activeProjectId,
  onSelectConversation,
  onSelectProject,
  onNewConversation,
  onMoveConversation,
  onCreateProject,
  onPatchProject,
  collapsed,
  agentProcesses,
  cronJobs,
  automations,
}: AppSidebarProps) {
  const [activeTab, setActiveTab] = useState<
    'chats' | 'agents' | 'automations'
  >('chats');
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(
    new Set(projects.map((p) => p.id))
  );
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['agents', 'cron', 'automations'])
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [draggedConvId, setDraggedConvId] = useState<string | null>(null);
  const [dragOverProjectId, setDragOverProjectId] = useState<string | null>(
    null
  );
  const [newProjectDialogOpen, setNewProjectDialogOpen] = useState(false);
  const [editProject, setEditProject] = useState<Project | null>(null);
  const [projectFormName, setProjectFormName] = useState('');
  const [projectFormColor, setProjectFormColor] = useState(PROJECT_COLORS[0]);
  const [projectFormLoading, setProjectFormLoading] = useState(false);

  const [vaultStatus, setVaultStatus] = useState({
    initialized: false,
    locked: true,
  });
  const [showVaultOverlay, setShowVaultOverlay] = useState(false);

  const fetchVaultStatus = async () => {
    try {
      const status = await api.getVaultStatus();
      setVaultStatus(status);
    } catch (e) {
      console.error('Failed to fetch vault status', e);
    }
  };

  useEffect(() => {
    fetchVaultStatus();
  }, []);

  const toggleProject = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const project = projects.find((p) => p.id === id);
    if (project?.is_vault && vaultStatus.locked) {
      setShowVaultOverlay(true);
      return;
    }

    setExpandedProjects((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleProjectClick = (id: string) => {
    onSelectProject(id);
  };

  const toggleSection = (id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const filteredConversations = searchQuery
    ? conversations.filter((c) =>
        c.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : conversations;

  const getProjectConversations = (project: Project) =>
    filteredConversations.filter((c) => project.conversationIds.includes(c.id));

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'now';
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
  };

  const formatDuration = (start: Date) => {
    const diff = Date.now() - start.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return '<1m';
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    return `${hours}h ${mins % 60}m`;
  };

  const runningAgents = agentProcesses.filter((a) => a.status === 'running');
  const activeCrons = cronJobs.filter((c) => c.status === 'active');
  const activeAutomations = automations.filter((a) => a.status === 'active');
  // Collapsed state
  if (collapsed) {
    return (
      <aside className="border-border bg-card flex h-full w-14 flex-col items-center gap-2 border-r py-3">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={activeTab === 'chats' ? 'secondary' : 'ghost'}
                size="icon"
                className="h-9 w-9"
                onClick={() => setActiveTab('chats')}
              >
                <MessageSquare className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Chats</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={activeTab === 'agents' ? 'secondary' : 'ghost'}
                size="icon"
                className="relative h-9 w-9"
                onClick={() => setActiveTab('agents')}
              >
                <Bot className="h-4 w-4" />
                {runningAgents.length > 0 && (
                  <span className="bg-primary text-primary-foreground absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full text-[8px] font-bold">
                    {runningAgents.length}
                  </span>
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              Agents
              {runningAgents.length > 0 && ` (${runningAgents.length} running)`}
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={activeTab === 'automations' ? 'secondary' : 'ghost'}
                size="icon"
                className="relative h-9 w-9"
                onClick={() => setActiveTab('automations')}
              >
                <Zap className="h-4 w-4" />
                {activeCrons.length + activeAutomations.length > 0 && (
                  <span className="bg-success text-success-foreground absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full text-[8px] font-bold">
                    {activeCrons.length + activeAutomations.length}
                  </span>
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              Automations
              {activeCrons.length + activeAutomations.length > 0 &&
                ` (${activeCrons.length + activeAutomations.length} active)`}
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
        {activeTab === 'chats' &&
          projects.map((project) => (
            <TooltipProvider key={project.id}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    className="hover:bg-accent flex h-8 w-8 items-center justify-center rounded-md text-xs font-semibold transition-colors"
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
    );
  }

  return (
    <aside className="border-border bg-card flex h-full w-72 flex-col border-r">
      {/* Tabs */}
      <div className="p-3 pb-0">
        <Tabs
          value={activeTab}
          onValueChange={(v) =>
            setActiveTab(v as 'chats' | 'agents' | 'automations')
          }
        >
          <TabsList className="h-8 w-full">
            <TabsTrigger value="chats" className="h-6 flex-1 gap-1.5 text-xs">
              <MessageSquare className="h-3 w-3" />
              Chats
            </TabsTrigger>
            <TabsTrigger value="agents" className="h-6 flex-1 gap-1.5 text-xs">
              <Bot className="h-3 w-3" />
              Agents
              {runningAgents.length > 0 && (
                <Badge
                  variant="secondary"
                  className="h-4 min-w-4 px-1 text-[9px] font-bold"
                >
                  {runningAgents.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger
              value="automations"
              className="h-6 flex-1 gap-1.5 text-xs"
            >
              <Zap className="h-3 w-3" />
              Auto
              {activeCrons.length + activeAutomations.length > 0 && (
                <Badge
                  variant="secondary"
                  className="h-4 min-w-4 px-1 text-[9px] font-bold"
                >
                  {activeCrons.length + activeAutomations.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Search */}
      <div className="px-3 py-2">
        <div className="relative">
          <Search className="text-muted-foreground absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2" />
          <Input
            placeholder={
              activeTab === 'chats'
                ? 'Search conversations...'
                : activeTab === 'agents'
                  ? 'Search agents...'
                  : 'Search automations...'
            }
            className="h-8 pl-8 text-xs"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 px-1.5">
        {activeTab === 'chats' ? (
          /* Chats tab */
          <div className="space-y-0.5 pb-4">
            {/* New chat button */}
            <Button
              variant="ghost"
              className="text-muted-foreground h-auto w-full justify-start gap-2 px-2 py-1.5 text-xs"
              onClick={onNewConversation}
            >
              <Plus className="h-3 w-3" />
              New conversation
            </Button>
            {onCreateProject && (
              <Button
                variant="ghost"
                className="text-muted-foreground h-auto w-full justify-start gap-2 px-2 py-1.5 text-xs"
                onClick={() => {
                  setProjectFormName('');
                  setProjectFormColor(PROJECT_COLORS[0]);
                  setNewProjectDialogOpen(true);
                }}
              >
                <FolderOpen className="h-3 w-3" />
                New project
              </Button>
            )}
            <Separator className="my-1" />
            {projects.map((project) => {
              const projConvs = getProjectConversations(project);
              const isExpanded = expandedProjects.has(project.id);
              return (
                <div key={project.id} className="flex flex-col gap-0.5">
                  <div className="group relative flex items-center gap-0.5">
                    <button
                      onClick={() => handleProjectClick(project.id)}
                      onDragOver={(e) => {
                        e.preventDefault();
                        setDragOverProjectId(project.id);
                      }}
                      onDragLeave={() => setDragOverProjectId(null)}
                      onDrop={async (e) => {
                        e.preventDefault();
                        setDragOverProjectId(null);
                        if (draggedConvId && onMoveConversation) {
                          await onMoveConversation(draggedConvId, project.id);
                        }
                      }}
                      className={cn(
                        'text-muted-foreground hover:bg-accent hover:text-accent-foreground relative flex min-w-0 flex-1 items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                        activeProjectId === project.id &&
                          'bg-accent/80 text-accent-foreground ring-primary/20 shadow-sm ring-1',
                        dragOverProjectId === project.id &&
                          'bg-primary/15 ring-primary/40 ring-2 ring-inset'
                      )}
                    >
                      <div
                        onClick={(e) => toggleProject(e, project.id)}
                        className="hover:bg-accent-foreground/10 rounded p-0.5 transition-colors"
                      >
                        {isExpanded ? (
                          <ChevronDown className="h-3 w-3 shrink-0" />
                        ) : (
                          <ChevronRight className="h-3 w-3 shrink-0" />
                        )}
                      </div>
                      {project.is_vault ? (
                        vaultStatus.locked ? (
                          <Lock className="text-muted-foreground/60 h-3 w-3 shrink-0" />
                        ) : (
                          <Unlock className="text-success h-3 w-3 shrink-0" />
                        )
                      ) : (
                        <FolderOpen
                          className="h-3 w-3 shrink-0"
                          style={{ color: project.color }}
                        />
                      )}
                      <span className="truncate">{project.name}</span>
                      <span className="text-muted-foreground/60 ml-auto text-[10px] tabular-nums">
                        {projConvs.length}
                      </span>
                    </button>
                    {onPatchProject && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreVertical className="h-3 w-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => {
                              setEditProject(project);
                              setProjectFormName(project.name);
                              setProjectFormColor(project.color);
                            }}
                          >
                            <Pencil className="mr-2 h-3 w-3" />
                            Edit
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </div>
                  {isExpanded && (
                    <div className="border-border/40 ml-5 space-y-px border-l pl-2.5">
                      {/* Conversations */}
                      {projConvs.map((conv) => (
                        <button
                          key={conv.id}
                          draggable
                          onDragStart={() => setDraggedConvId(conv.id)}
                          onDragEnd={() => setDraggedConvId(null)}
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectConversation(conv.id);
                          }}
                          className={cn(
                            'flex w-full cursor-grab items-center gap-2 rounded-md px-2 py-1.5 text-xs transition-colors active:cursor-grabbing',
                            activeConversationId === conv.id
                              ? 'bg-accent text-accent-foreground ring-primary/10 shadow-sm ring-1'
                              : 'text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground',
                            draggedConvId === conv.id &&
                              'opacity-40 grayscale-[0.5]'
                          )}
                        >
                          {conv.persona ? (
                            <Hash className="h-3 w-3 shrink-0 opacity-70" />
                          ) : (
                            <MessageSquare className="h-3 w-3 shrink-0 opacity-70" />
                          )}
                          <span className="truncate">{conv.title}</span>
                          <span className="text-muted-foreground/50 ml-auto text-[10px] tabular-nums">
                            {formatTime(conv.updatedAt)}
                          </span>
                        </button>
                      ))}

                      {/* Other Assets (Agents/Crons/Autos) */}
                      {agentProcesses
                        .filter((a) => a.projectId === project.id)
                        .map((agent) => (
                          <div
                            key={agent.id}
                            className="text-muted-foreground/60 flex items-center gap-2 px-2 py-1.5 text-[10px]"
                          >
                            <Bot className="h-2.5 w-2.5 shrink-0 opacity-50" />
                            <span className="truncate">{agent.name}</span>
                            <Badge
                              variant="outline"
                              className={cn(
                                'bg-primary/5 h-3 px-1 text-[8px]',
                                agent.status === 'running'
                                  ? 'text-success border-success/30'
                                  : 'border-muted-foreground/20'
                              )}
                            >
                              {agent.status}
                            </Badge>
                          </div>
                        ))}

                      {cronJobs
                        .filter((c) => c.projectId === project.id)
                        .map((cron) => (
                          <div
                            key={cron.id}
                            className="text-muted-foreground/60 flex items-center gap-2 px-2 py-1.5 text-[10px]"
                          >
                            <Clock className="h-2.5 w-2.5 shrink-0 opacity-50" />
                            <span className="truncate">{cron.name}</span>
                          </div>
                        ))}

                      {automations
                        .filter((a) => a.projectId === project.id)
                        .map((auto) => (
                          <div
                            key={auto.id}
                            className="text-muted-foreground/60 flex items-center gap-2 px-2 py-1.5 text-[10px]"
                          >
                            <Zap className="h-2.5 w-2.5 shrink-0 opacity-50" />
                            <span className="truncate">{auto.name}</span>
                          </div>
                        ))}

                      {projConvs.length === 0 &&
                        agentProcesses.filter((a) => a.projectId === project.id)
                          .length === 0 &&
                        cronJobs.filter((c) => c.projectId === project.id)
                          .length === 0 &&
                        automations.filter((a) => a.projectId === project.id)
                          .length === 0 && (
                          <p className="text-muted-foreground/40 px-3 py-1.5 text-[10px] italic">
                            Empty project
                          </p>
                        )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : activeTab === 'agents' ? (
          /* Agents tab */
          <div className="space-y-0.5 pb-4">
            <div className="text-muted-foreground px-2 py-1.5 text-[10px] font-semibold tracking-wider uppercase">
              Goal-Based Processes
            </div>
            <SectionHeader
              icon={Bot}
              label="Background Agents"
              count={runningAgents.length}
              countVariant="running"
              expanded={expandedSections.has('agents')}
              onToggle={() => toggleSection('agents')}
            />
            {expandedSections.has('agents') && (
              <div className="ml-1 space-y-px">
                {agentProcesses.filter(
                  (a) =>
                    !searchQuery ||
                    a.name.toLowerCase().includes(searchQuery.toLowerCase())
                ).length > 0 ? (
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
                  <p className="text-muted-foreground px-2 py-3 text-[10px] italic">
                    No agents configured.
                  </p>
                )}
              </div>
            )}
          </div>
        ) : (
          /* Automations tab */
          <div className="space-y-0.5 pb-4">
            <div className="text-muted-foreground px-2 py-1.5 text-[10px] font-semibold tracking-wider uppercase">
              Deterministic Triggers
            </div>
            <SectionHeader
              icon={Clock}
              label="Cron Jobs"
              count={activeCrons.length}
              countVariant="active"
              expanded={expandedSections.has('cron')}
              onToggle={() => toggleSection('cron')}
            />
            {expandedSections.has('cron') && (
              <div className="ml-1 space-y-px">
                {cronJobs.filter(
                  (c) =>
                    !searchQuery ||
                    c.name.toLowerCase().includes(searchQuery.toLowerCase())
                ).length > 0 ? (
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
                  <p className="text-muted-foreground px-2 py-3 text-[10px] italic">
                    No cron jobs configured.
                  </p>
                )}
              </div>
            )}

            <Separator className="my-1.5" />

            <SectionHeader
              icon={Zap}
              label="Event Automations"
              count={activeAutomations.length}
              countVariant="active"
              expanded={expandedSections.has('automations')}
              onToggle={() => toggleSection('automations')}
            />
            {expandedSections.has('automations') && (
              <div className="ml-1 space-y-px">
                {automations.filter(
                  (a) =>
                    !searchQuery ||
                    a.name.toLowerCase().includes(searchQuery.toLowerCase())
                ).length > 0 ? (
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
                  <p className="text-muted-foreground px-2 py-3 text-[10px] italic">
                    No automations configured.
                  </p>
                )}
              </div>
            )}

            <Separator className="my-1.5" />

            <Link
              href="/automation"
              className="text-muted-foreground hover:bg-sidebar-accent hover:text-foreground flex items-center gap-2 rounded-md px-2 py-2 text-[11px] transition-colors"
            >
              <FileCode className="h-3.5 w-3.5 shrink-0" />
              Scripts & logs
            </Link>
          </div>
        )}
      </ScrollArea>

      {/* New project dialog */}
      <Dialog
        open={newProjectDialogOpen}
        onOpenChange={setNewProjectDialogOpen}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>New project</DialogTitle>
            <DialogDescription>
              Create a project to organise your conversations.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="project-name">Name</Label>
              <Input
                id="project-name"
                value={projectFormName}
                onChange={(e) => setProjectFormName(e.target.value)}
                placeholder="Project name"
              />
            </div>
            <div className="space-y-2">
              <Label>Colour</Label>
              <div className="flex flex-wrap gap-2">
                {PROJECT_COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    aria-label={`Select colour ${c}`}
                    className={cn(
                      'h-6 w-6 rounded-full border-2 transition-colors',
                      projectFormColor === c
                        ? 'border-foreground'
                        : 'hover:border-muted-foreground border-transparent'
                    )}
                    style={{ backgroundColor: c }}
                    onClick={() => setProjectFormColor(c)}
                  />
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setNewProjectDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              disabled={!projectFormName.trim() || projectFormLoading}
              onClick={async () => {
                if (!projectFormName.trim() || !onCreateProject) return;
                setProjectFormLoading(true);
                try {
                  await onCreateProject(
                    projectFormName.trim(),
                    projectFormColor
                  );
                  setNewProjectDialogOpen(false);
                } finally {
                  setProjectFormLoading(false);
                }
              }}
            >
              {projectFormLoading ? 'Creating…' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit project dialog */}
      <Dialog
        open={!!editProject}
        onOpenChange={(o) => !o && setEditProject(null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Edit project</DialogTitle>
            <DialogDescription>
              Change the project name or colour.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-project-name">Name</Label>
              <Input
                id="edit-project-name"
                value={projectFormName}
                onChange={(e) => setProjectFormName(e.target.value)}
                placeholder="Project name"
              />
            </div>
            <div className="space-y-2">
              <Label>Colour</Label>
              <div className="flex flex-wrap gap-2">
                {PROJECT_COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    aria-label={`Select colour ${c}`}
                    className={cn(
                      'h-6 w-6 rounded-full border-2 transition-colors',
                      projectFormColor === c
                        ? 'border-foreground'
                        : 'hover:border-muted-foreground border-transparent'
                    )}
                    style={{ backgroundColor: c }}
                    onClick={() => setProjectFormColor(c)}
                  />
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditProject(null)}>
              Cancel
            </Button>
            <Button
              disabled={!projectFormName.trim() || projectFormLoading}
              onClick={async () => {
                if (!editProject || !projectFormName.trim() || !onPatchProject)
                  return;
                setProjectFormLoading(true);
                try {
                  await onPatchProject(editProject.id, {
                    name: projectFormName.trim(),
                    color: projectFormColor,
                  });
                  setEditProject(null);
                } finally {
                  setProjectFormLoading(false);
                }
              }}
            >
              {projectFormLoading ? 'Saving…' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      {showVaultOverlay && (
        <VaultOverlay
          isInitialized={vaultStatus.initialized}
          onUnlock={() => {
            setShowVaultOverlay(false);
            fetchVaultStatus();
          }}
        />
      )}
    </aside>
  );
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
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  count: number;
  countVariant: 'running' | 'active';
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      onClick={onToggle}
      className="text-muted-foreground hover:bg-accent hover:text-accent-foreground flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors"
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
            'ml-auto h-4 min-w-4 border-0 px-1 text-[9px] font-semibold',
            countVariant === 'running'
              ? 'bg-primary/10 text-primary'
              : 'bg-success/10 text-success'
          )}
        >
          {count}
        </Badge>
      )}
    </button>
  );
}

function AgentItem({
  agent,
  projects,
  formatDuration,
}: {
  agent: AgentProcess;
  projects: Project[];
  formatDuration: (d: Date) => string;
}) {
  const project = projects.find((p) => p.id === agent.projectId);
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={cn(
              'flex cursor-default items-start gap-2.5 rounded-md px-2 py-2 text-xs transition-colors',
              agent.status === 'running'
                ? 'bg-primary/[0.04] hover:bg-primary/[0.07]'
                : 'hover:bg-accent/50'
            )}
          >
            {/* Status dot */}
            <div className="mt-1 shrink-0">
              <span
                className={cn(
                  'block h-2 w-2 rounded-full',
                  agent.status === 'running' && 'bg-primary animate-pulse-dot',
                  agent.status === 'idle' && 'bg-muted-foreground/40',
                  agent.status === 'error' && 'bg-destructive'
                )}
              />
            </div>
            {/* Content */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5">
                <span
                  className={cn(
                    'truncate font-medium',
                    agent.status === 'running'
                      ? 'text-foreground'
                      : 'text-muted-foreground'
                  )}
                >
                  {agent.name}
                </span>
                {agent.type === 'internal' ? (
                  <Cpu className="text-success h-2.5 w-2.5 shrink-0" />
                ) : (
                  <Globe className="text-warning h-2.5 w-2.5 shrink-0" />
                )}
              </div>
              <div className="text-muted-foreground mt-0.5 flex items-center gap-1.5 text-[10px]">
                <span className="font-mono">{agent.model}</span>
                {agent.startedAt && agent.status === 'running' && (
                  <>
                    <span>{'/'}</span>
                    <span>{formatDuration(agent.startedAt)}</span>
                  </>
                )}
              </div>
              {project && (
                <div className="mt-1 flex items-center gap-1">
                  <span
                    className="h-1.5 w-1.5 shrink-0 rounded-full"
                    style={{ backgroundColor: project.color }}
                  />
                  <span className="text-muted-foreground/60 truncate text-[10px]">
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
  );
}

function CronItem({
  cron,
  projects,
  formatTime,
}: {
  cron: CronJob;
  projects: Project[];
  formatTime: (d: Date) => string;
}) {
  const project = projects.find((p) => p.id === cron.projectId);
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="hover:bg-accent/50 flex cursor-default items-start gap-2.5 rounded-md px-2 py-2 text-xs transition-colors">
            {/* Status icon */}
            <div className="mt-0.5 shrink-0">
              {cron.status === 'active' ? (
                <Play className="text-success h-3 w-3" />
              ) : cron.status === 'paused' ? (
                <Pause className="text-muted-foreground h-3 w-3" />
              ) : (
                <AlertTriangle className="text-destructive h-3 w-3" />
              )}
            </div>
            {/* Content */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5">
                <span
                  className={cn(
                    'truncate font-medium',
                    cron.status === 'active'
                      ? 'text-foreground'
                      : 'text-muted-foreground'
                  )}
                >
                  {cron.name}
                </span>
              </div>
              <div className="text-muted-foreground mt-0.5 flex items-center gap-1.5 text-[10px]">
                <code className="bg-secondary rounded px-1 font-mono">
                  {cron.schedule}
                </code>
              </div>
              <div className="text-muted-foreground/60 mt-1 flex items-center gap-2 text-[10px]">
                {cron.lastRun && (
                  <span>ran {formatTime(cron.lastRun)} ago</span>
                )}
                {project && (
                  <div className="flex items-center gap-1">
                    <span
                      className="h-1.5 w-1.5 shrink-0 rounded-full"
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
  );
}

const AUTOMATION_TYPE_ICONS: Record<
  Automation['type'],
  React.ComponentType<{ className?: string }>
> = {
  webhook: Webhook,
  event: Radio,
  schedule: CalendarClock,
  watch: Eye,
};

function AutomationItem({
  automation,
  projects,
  formatTime,
}: {
  automation: Automation;
  projects: Project[];
  formatTime: (d: Date) => string;
}) {
  const project = projects.find((p) => p.id === automation.projectId);
  const TypeIcon = AUTOMATION_TYPE_ICONS[automation.type];
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="hover:bg-accent/50 flex cursor-default items-start gap-2.5 rounded-md px-2 py-2 text-xs transition-colors">
            {/* Type icon */}
            <div className="mt-0.5 shrink-0">
              <TypeIcon
                className={cn(
                  'h-3 w-3',
                  automation.status === 'active'
                    ? 'text-primary'
                    : automation.status === 'paused'
                      ? 'text-muted-foreground'
                      : 'text-destructive'
                )}
              />
            </div>
            {/* Content */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5">
                <span
                  className={cn(
                    'truncate font-medium',
                    automation.status === 'active'
                      ? 'text-foreground'
                      : 'text-muted-foreground'
                  )}
                >
                  {automation.name}
                </span>
                {automation.runsToday > 0 && (
                  <Badge
                    variant="outline"
                    className="bg-secondary text-secondary-foreground h-3.5 border-0 px-1 font-mono text-[8px]"
                  >
                    {automation.runsToday}x
                  </Badge>
                )}
              </div>
              <div className="text-muted-foreground mt-0.5 truncate font-mono text-[10px]">
                {automation.trigger}
              </div>
              <div className="text-muted-foreground/60 mt-1 flex items-center gap-2 text-[10px]">
                {automation.lastTriggered && (
                  <span>{formatTime(automation.lastTriggered)} ago</span>
                )}
                {project && (
                  <div className="flex items-center gap-1">
                    <span
                      className="h-1.5 w-1.5 shrink-0 rounded-full"
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
  );
}
