'use client';

import React from 'react';
import {
  MessageSquare,
  Bot,
  Clock,
  Zap,
  Plus,
  Settings,
  Trash2,
  ChevronRight,
  TrendingUp,
  Activity,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import type {
  Project,
  Conversation,
  AgentProcess,
  CronJob,
  Automation,
} from '@/lib/store';

interface ProjectPageProps {
  project: Project;
  conversations: Conversation[];
  agentProcesses: AgentProcess[];
  cronJobs: CronJob[];
  automations: Automation[];
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteProject?: (id: string) => void;
  onProjectSettings?: (id: string) => void;
}

export function ProjectPage({
  project,
  conversations,
  agentProcesses,
  cronJobs,
  automations,
  onSelectConversation,
  onNewConversation,
  onDeleteProject,
  onProjectSettings,
}: ProjectPageProps) {
  const projectConvs = conversations.filter((c) =>
    project.conversationIds.includes(c.id)
  );
  const projectAgents = agentProcesses.filter(
    (a) => a.projectId === project.id
  );
  const projectCrons = cronJobs.filter((c) => c.projectId === project.id);
  const projectAutos = automations.filter((a) => a.projectId === project.id);

  return (
    <div className="bg-background flex flex-1 flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-card/50 flex items-center justify-between border-b p-6 backdrop-blur-sm">
        <div className="flex items-center gap-4">
          <div
            className="flex h-10 w-10 items-center justify-center rounded-xl text-xl font-bold text-white shadow-lg"
            style={{
              backgroundColor: project.color,
              textShadow: '0 2px 4px rgba(0,0,0,0.2)',
            }}
          >
            {project.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight">
              {project.name}
            </h2>
            <p className="text-muted-foreground text-sm">Project Workspace</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onProjectSettings?.(project.id)}
          >
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => onDeleteProject?.(project.id)}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="mx-auto max-w-6xl space-y-8 p-8">
          {/* Stats Overview */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Conversations"
              value={projectConvs.length}
              icon={MessageSquare}
              trend="+2 this week"
            />
            <StatsCard
              title="Agents"
              value={projectAgents.length}
              icon={Bot}
              trend="All systems stable"
            />
            <StatsCard
              title="Cron Jobs"
              value={projectCrons.length}
              icon={Clock}
              trend="Next run in 2h"
            />
            <StatsCard
              title="Automations"
              value={projectAutos.length}
              icon={Zap}
              trend="15 executions today"
            />
          </div>

          <div className="grid gap-8 md:grid-cols-7">
            {/* Main Content: Conversations List */}
            <Card className="bg-card/40 border-none shadow-md md:col-span-4">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Recent Conversations</CardTitle>
                  <CardDescription>
                    Manage your chat history in this project.
                  </CardDescription>
                </div>
                <Button size="sm" className="gap-2" onClick={onNewConversation}>
                  <Plus className="h-4 w-4" />
                  New Chat
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {projectConvs.length > 0 ? (
                    projectConvs.slice(0, 5).map((conv) => (
                      <div
                        key={conv.id}
                        className="hover:bg-accent/50 group flex cursor-pointer items-center justify-between rounded-lg border p-3 transition-colors"
                        onClick={() => onSelectConversation(conv.id)}
                      >
                        <div className="flex items-center gap-3">
                          <div className="bg-primary/10 border-primary/20 flex h-8 w-8 items-center justify-center rounded-full border">
                            <MessageSquare className="text-primary h-4 w-4" />
                          </div>
                          <div>
                            <p className="text-sm leading-none font-medium">
                              {conv.title}
                            </p>
                            <p className="text-muted-foreground mt-1 text-xs">
                              Updated{' '}
                              {new Date(conv.updatedAt).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <ChevronRight className="text-muted-foreground h-4 w-4 opacity-0 transition-opacity group-hover:opacity-100" />
                      </div>
                    ))
                  ) : (
                    <div className="rounded-xl border-2 border-dashed py-12 text-center">
                      <MessageSquare className="text-muted-foreground/20 mx-auto h-12 w-12" />
                      <p className="text-muted-foreground mt-4 text-sm">
                        No conversations yet.
                      </p>
                      <Button
                        variant="link"
                        className="mt-2"
                        onClick={onNewConversation}
                      >
                        Start a chat
                      </Button>
                    </div>
                  )}
                  {projectConvs.length > 5 && (
                    <Button
                      variant="ghost"
                      className="text-muted-foreground w-full text-xs"
                    >
                      View all {projectConvs.length} conversations
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Sidebar: Activity & Assets */}
            <div className="space-y-8 md:col-span-3">
              <Card className="bg-card/40 border-none shadow-md">
                <CardHeader>
                  <CardTitle className="text-lg">Project Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <ActivityItem
                      icon={TrendingUp}
                      title="Model usage optimized"
                      time="2 hours ago"
                      color="text-success"
                    />
                    <ActivityItem
                      icon={Bot}
                      title="Subagent 'Researcher' started"
                      time="5 hours ago"
                      color="text-primary"
                    />
                    <ActivityItem
                      icon={Zap}
                      title="Daily summary automation trigger"
                      time="Yesterday"
                      color="text-amber-500"
                    />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card/40 border-none shadow-md">
                <CardHeader>
                  <CardTitle className="text-lg">Project Health</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Privacy Mode</span>
                    <Badge
                      variant="outline"
                      className="text-success border-success/30 bg-success/10"
                    >
                      Active
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Encryption</span>
                    <Badge
                      variant="outline"
                      className="text-primary border-primary/30 bg-primary/10"
                    >
                      AES-256
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      Local Resources
                    </span>
                    <div className="flex items-center gap-2">
                      <Separator className="bg-success/30 h-1 w-12 rounded" />
                      <span className="text-xs">Healthy</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}

function StatsCard({
  title,
  value,
  icon: Icon,
  trend,
}: {
  title: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  trend: string;
}) {
  return (
    <Card className="bg-card/40 border-none shadow-sm transition-shadow hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="text-muted-foreground h-4 w-4" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-muted-foreground mt-1 flex items-center gap-1 text-[10px]">
          <Activity className="text-success h-3 w-3" />
          {trend}
        </p>
      </CardContent>
    </Card>
  );
}

function ActivityItem({
  icon: Icon,
  title,
  time,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  time: string;
  color: string;
}) {
  return (
    <div className="flex gap-3">
      <div className={cn('mt-0.5', color)}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="space-y-1">
        <p className="text-xs leading-none font-medium">{title}</p>
        <p className="text-muted-foreground text-[10px]">{time}</p>
      </div>
    </div>
  );
}
