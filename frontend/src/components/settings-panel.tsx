'use client';

import { useState } from 'react';
import {
  X,
  Cpu,
  Globe,
  Server,
  Zap,
  Plug,
  Settings2,
  CircleDot,
  Route,
  ShieldCheck,
  EyeOff,
  Search,
  Activity,
  Power,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api } from '@/lib/api-client';
import { useEffect } from 'react';
import type { Model, Skill, MCP, Integration } from '@/lib/store';

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
  models: Model[];
  skills: Skill[];
  mcps: MCP[];
  integrations: Integration[];
  onToggleSkill: (id: string) => void;
}

export function SettingsPanel({
  open,
  onClose,
  models,
  skills,
  mcps,
  integrations,
  onToggleSkill,
}: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState('routing');
  const [routingConfig, setRoutingConfig] = useState<Record<string, string>>(
    {}
  );
  const [isSaving, setIsSaving] = useState(false);
  const [systemStatus, setSystemStatus] = useState<{
    ollama: { status: string; port: number };
    backend: { status: string; port: number };
    frontend: { status: string; port: number };
  } | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchStatus = async () => {
    try {
      setIsRefreshing(true);
      const status = await api.getSystemStatus();
      setSystemStatus(status);
    } catch (err) {
      console.error('Failed to fetch system status:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    if (open && activeTab === 'system') {
      fetchStatus();
      const interval = setInterval(fetchStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [open, activeTab]);

  const handleStartOllama = async () => {
    try {
      await api.startOllama();
      setTimeout(fetchStatus, 2000);
    } catch (err) {
      console.error('Failed to start Ollama:', err);
    }
  };

  const handleStopOllama = async () => {
    try {
      await api.stopOllama();
      setTimeout(fetchStatus, 1000);
    } catch (err) {
      console.error('Failed to stop Ollama:', err);
    }
  };

  useEffect(() => {
    if (open) {
      api.getRoutingConfig().then(setRoutingConfig).catch(console.error);
    }
  }, [open]);

  const handleUpdateRouting = async (task: string, modelId: string) => {
    const newConfig = { ...routingConfig, [task]: modelId };
    setRoutingConfig(newConfig);
    setIsSaving(true);
    try {
      await api.updateRoutingConfig({ [task]: modelId });
    } catch (err) {
      console.error('Failed to update routing:', err);
    } finally {
      setIsSaving(false);
    }
  };

  if (!open) return null;

  return (
    <div className="border-border bg-card flex h-full w-80 flex-col border-l">
      {/* Header */}
      <div className="border-border flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <Settings2 className="text-muted-foreground h-4 w-4" />
          <span className="text-foreground text-sm font-semibold">
            Settings
          </span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={onClose}
        >
          <X className="h-3.5 w-3.5" />
        </Button>
      </div>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="flex flex-1 flex-col"
      >
        <div className="px-3 pt-3">
          <TabsList className="grid h-8 w-full grid-cols-6">
            <TabsTrigger value="routing" className="text-[10px]">
              Routing
            </TabsTrigger>
            <TabsTrigger value="models" className="text-[10px]">
              Models
            </TabsTrigger>
            <TabsTrigger value="skills" className="text-[10px]">
              Skills
            </TabsTrigger>
            <TabsTrigger value="mcps" className="text-[10px]">
              MCPs
            </TabsTrigger>
            <TabsTrigger value="integrations" className="text-[10px]">
              Integrations
            </TabsTrigger>
            <TabsTrigger value="system" className="text-[10px]">
              System
            </TabsTrigger>
          </TabsList>
        </div>

        <ScrollArea className="flex-1">
          {/* Routing Tab */}
          <TabsContent value="routing" className="mt-0 space-y-4 p-3">
            <div className="flex items-center justify-between">
              <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
                Meta-Task Assignment
              </p>
              {isSaving && (
                <span className="text-primary animate-pulse text-[9px]">
                  Saving...
                </span>
              )}
            </div>

            {[
              {
                id: 'intent_classification',
                name: 'Intent Classification',
                icon: Search,
                description: 'Determines user goal (Coding, Private, etc.)',
              },
              {
                id: 'security_judge',
                name: 'Security Judge',
                icon: ShieldCheck,
                description: 'Validates output for safety and leaks',
              },
              {
                id: 'pii_redactor',
                name: 'PII Redactor',
                icon: EyeOff,
                description: 'Masks sensitive personal information',
              },
            ].map((task) => (
              <div key={task.id} className="space-y-2">
                <div className="flex items-center gap-2">
                  <task.icon className="text-muted-foreground h-3.5 w-3.5" />
                  <span className="text-foreground text-xs font-medium">
                    {task.name}
                  </span>
                </div>
                <p className="text-muted-foreground ml-0.5 px-5 text-[10px] leading-tight">
                  {task.description}
                </p>
                <div className="mt-1 px-5">
                  <Select
                    value={routingConfig[task.id] || 'auto'}
                    onValueChange={(val) => handleUpdateRouting(task.id, val)}
                  >
                    <SelectTrigger className="bg-background h-8 text-[11px]">
                      <SelectValue placeholder="Select model..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto" className="text-[11px]">
                        Best Local (Auto)
                      </SelectItem>
                      <SelectSeparator />
                      <SelectGroup>
                        <SelectLabel className="text-[10px] font-bold">
                          Commercial (Recommended)
                        </SelectLabel>
                        {models
                          .filter((m) => m.provider !== 'Ollama (Local)')
                          .map((m) => (
                            <SelectItem
                              key={m.id}
                              value={m.id}
                              className="text-[11px]"
                            >
                              {m.name}
                            </SelectItem>
                          ))}
                      </SelectGroup>
                      <SelectSeparator />
                      <SelectGroup>
                        <SelectLabel className="text-[10px]">
                          Local (Ollama)
                        </SelectLabel>
                        {models
                          .filter((m) => m.provider === 'Ollama (Local)')
                          .map((m) => (
                            <SelectItem
                              key={m.id}
                              value={m.id}
                              className="text-[11px]"
                            >
                              {m.name}
                            </SelectItem>
                          ))}
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            ))}

            <div className="bg-muted/40 border-border/50 mt-6 rounded-md border p-3">
              <div className="mb-1.5 flex items-center gap-2">
                <Route className="text-primary h-3.5 w-3.5" />
                <span className="text-[10px] font-semibold tracking-tight uppercase">
                  Performance Tip
                </span>
              </div>
              <p className="text-muted-foreground text-[10px] leading-relaxed">
                Use commercial models for these tasks to offload your local
                CPU/GPU. They are fast and low-token, typically costing
                fractions of a cent per request.
              </p>
            </div>
          </TabsContent>

          {/* Models Tab */}
          <TabsContent value="models" className="mt-0 space-y-2 p-3">
            <p className="text-muted-foreground mb-3 text-[10px] font-medium tracking-wider uppercase">
              Available Models
            </p>
            {models.map((model) => (
              <Card key={model.id} className="bg-background">
                <CardContent className="flex items-center gap-3 p-3">
                  <div className="bg-muted flex h-8 w-8 items-center justify-center rounded-md">
                    {model.type === 'commercial' && (
                      <Globe className="text-primary h-4 w-4" />
                    )}
                    {model.type === 'ollama' && (
                      <Server className="text-success h-4 w-4" />
                    )}
                    {model.type === 'local' && (
                      <Cpu className="text-warning h-4 w-4" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-foreground truncate text-xs font-medium">
                        {model.name}
                      </span>
                      <span
                        className={cn(
                          'h-1.5 w-1.5 shrink-0 rounded-full',
                          model.status === 'online'
                            ? 'bg-success'
                            : model.status === 'loading'
                              ? 'bg-warning animate-pulse-dot'
                              : 'bg-muted-foreground/40'
                        )}
                      />
                    </div>
                    <div className="mt-0.5 flex items-center gap-2">
                      <span className="text-muted-foreground text-[10px]">
                        {model.provider}
                      </span>
                      <Separator orientation="vertical" className="h-2.5" />
                      <span className="text-muted-foreground text-[10px]">
                        {model.contextWindow}
                      </span>
                    </div>
                  </div>
                  <Badge
                    variant="secondary"
                    className="shrink-0 px-1.5 py-0 text-[9px]"
                  >
                    {model.type}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Skills Tab */}
          <TabsContent value="skills" className="mt-0 space-y-2 p-3">
            <p className="text-muted-foreground mb-3 text-[10px] font-medium tracking-wider uppercase">
              Agent Capabilities
            </p>
            {skills.map((skill) => (
              <Card key={skill.id} className="bg-background">
                <CardContent className="flex items-center gap-3 p-3">
                  <div className="bg-muted flex h-8 w-8 items-center justify-center rounded-md">
                    <Zap
                      className={cn(
                        'h-4 w-4',
                        skill.enabled ? 'text-primary' : 'text-muted-foreground'
                      )}
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <span className="text-foreground text-xs font-medium">
                      {skill.name}
                    </span>
                    <p className="text-muted-foreground mt-0.5 text-[10px] leading-relaxed">
                      {skill.description}
                    </p>
                  </div>
                  <Switch
                    checked={skill.enabled}
                    onCheckedChange={() => onToggleSkill(skill.id)}
                    className="shrink-0"
                  />
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* MCPs Tab */}
          <TabsContent value="mcps" className="mt-0 space-y-2 p-3">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
                MCP Servers
              </p>
              <Button
                variant="outline"
                size="sm"
                className="h-6 bg-transparent text-[10px]"
              >
                <Plug className="mr-1 h-3 w-3" />
                Add
              </Button>
            </div>
            {mcps.map((mcp) => (
              <Card key={mcp.id} className="bg-background">
                <CardContent className="flex items-center gap-3 p-3">
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-md',
                      mcp.status === 'connected'
                        ? 'bg-success/10'
                        : mcp.status === 'error'
                          ? 'bg-destructive/10'
                          : 'bg-muted'
                    )}
                  >
                    <Plug
                      className={cn(
                        'h-4 w-4',
                        mcp.status === 'connected'
                          ? 'text-success'
                          : mcp.status === 'error'
                            ? 'text-destructive'
                            : 'text-muted-foreground'
                      )}
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-foreground text-xs font-medium">
                        {mcp.name}
                      </span>
                      <Badge
                        variant="outline"
                        className={cn(
                          'px-1.5 py-0 text-[9px]',
                          mcp.status === 'connected'
                            ? 'text-success border-success/30'
                            : mcp.status === 'error'
                              ? 'text-destructive border-destructive/30'
                              : 'text-muted-foreground'
                        )}
                      >
                        {mcp.status}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground mt-0.5 truncate font-mono text-[10px]">
                      {mcp.endpoint}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Integrations Tab */}
          <TabsContent value="integrations" className="mt-0 space-y-2 p-3">
            <p className="text-muted-foreground mb-3 text-[10px] font-medium tracking-wider uppercase">
              Connected Services
            </p>
            {integrations.map((integration) => (
              <Card
                key={integration.id}
                className="bg-background hover:bg-accent cursor-pointer transition-colors"
              >
                <CardContent className="flex items-center gap-3 p-3">
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-md',
                      integration.status === 'active'
                        ? 'bg-primary/10'
                        : integration.status === 'error'
                          ? 'bg-destructive/10'
                          : 'bg-muted'
                    )}
                  >
                    <CircleDot
                      className={cn(
                        'h-4 w-4',
                        integration.status === 'active'
                          ? 'text-primary'
                          : integration.status === 'error'
                            ? 'text-destructive'
                            : 'text-muted-foreground'
                      )}
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-foreground text-xs font-medium">
                        {integration.name}
                      </span>
                      <Badge
                        variant="secondary"
                        className="px-1.5 py-0 text-[9px]"
                      >
                        {integration.type}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground mt-0.5 text-[10px]">
                      {integration.description}
                    </p>
                  </div>
                  <span
                    className={cn(
                      'h-2 w-2 shrink-0 rounded-full',
                      integration.status === 'active'
                        ? 'bg-success'
                        : integration.status === 'error'
                          ? 'bg-destructive'
                          : 'bg-muted-foreground/40'
                    )}
                  />
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="mt-0 space-y-4 p-3">
            <div className="flex items-center justify-between">
              <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
                Daemon Management
              </p>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={fetchStatus}
                disabled={isRefreshing}
              >
                <RefreshCw
                  className={cn('h-3 w-3', isRefreshing && 'animate-spin')}
                />
              </Button>
            </div>

            {[
              {
                id: 'ollama',
                name: 'Ollama Service',
                icon: Cpu,
                status: systemStatus?.ollama.status,
                port: 11434,
                canControl: true,
              },
              {
                id: 'backend',
                name: 'Backend API',
                icon: Activity,
                status: systemStatus?.backend.status,
                port: 8001,
                canControl: false,
              },
              {
                id: 'frontend',
                name: 'Frontend Web',
                icon: Globe,
                status: systemStatus?.frontend.status,
                port: 3000,
                canControl: false,
              },
            ].map((daemon) => (
              <Card key={daemon.id} className="bg-background">
                <CardContent className="p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          'bg-muted flex h-8 w-8 items-center justify-center rounded-md',
                          daemon.status === 'online'
                            ? 'text-success'
                            : 'text-muted-foreground'
                        )}
                      >
                        <daemon.icon className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-foreground text-xs font-medium">
                            {daemon.name}
                          </span>
                          <span
                            className={cn(
                              'h-1.5 w-1.5 rounded-full',
                              daemon.status === 'online'
                                ? 'bg-success'
                                : 'bg-destructive animate-pulse'
                            )}
                          />
                        </div>
                        <p className="text-muted-foreground text-[10px]">
                          Port {daemon.port} • {daemon.status || 'Checking...'}
                        </p>
                      </div>
                    </div>

                    {daemon.canControl && (
                      <div className="flex gap-1">
                        {daemon.status !== 'online' ? (
                          <Button
                            size="sm"
                            className="h-7 px-2 text-[10px]"
                            onClick={handleStartOllama}
                            disabled={isRefreshing}
                          >
                            <Power className="mr-1 h-3 w-3" />
                            Start
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-destructive hover:bg-destructive/10 h-7 px-2 text-[10px]"
                            onClick={handleStopOllama}
                            disabled={isRefreshing}
                          >
                            <X className="mr-1 h-3 w-3" />
                            Kill
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}

            <div className="bg-muted/40 border-border/50 mt-2 rounded-md border p-3">
              <p className="text-muted-foreground text-[10px] leading-relaxed">
                Management of core platform daemons. Use the root{' '}
                <code className="bg-background px-1">manage.sh</code> script for
                full platform lifecycle control.
              </p>
            </div>
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  );
}
