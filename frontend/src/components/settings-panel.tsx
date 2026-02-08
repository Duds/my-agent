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
  ChevronDown,
  ChevronRight,
  Lock,
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
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@/components/ui/hover-card';
import { ModelInfoCard } from '@/components/model-info-card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
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
  /** Called when AI service is connected/disconnected so parent can refetch models */
  onServiceChanged?: () => void;
}

export function SettingsPanel({
  open,
  onClose,
  models,
  skills,
  mcps,
  integrations,
  onToggleSkill,
  onServiceChanged,
}: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState('ai');
  const [routingConfig, setRoutingConfig] = useState<Record<string, string>>(
    {}
  );
  const [isSaving, setIsSaving] = useState(false);
  const [advancedRoutingOpen, setAdvancedRoutingOpen] = useState(false);
  const [modelTagFilter, setModelTagFilter] = useState<string | null>(null);
  const [advancedSystemOpen, setAdvancedSystemOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState<{
    ollama: { status: string; port: number };
    backend: { status: string; port: number };
    frontend: { status: string; port: number };
  } | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isOllamaAction, setIsOllamaAction] = useState(false);
  const [isBackendAction, setIsBackendAction] = useState(false);
  const [lastCheckedAt, setLastCheckedAt] = useState<Date | null>(null);
  const [mcpAddDialogOpen, setMcpAddDialogOpen] = useState(false);
  const [aiServices, setAiServices] = useState<
    { provider: string; display_name: string; connected: boolean; model_count: number }[]
  >([]);
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [connectDialogProvider, setConnectDialogProvider] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [connectDialogApiKey, setConnectDialogApiKey] = useState('');
  const [connectDialogError, setConnectDialogError] = useState<string | null>(null);
  const [connectDialogLoading, setConnectDialogLoading] = useState(false);
  const [telegramTestMessage, setTelegramTestMessage] = useState('');
  const [telegramSending, setTelegramSending] = useState(false);
  const [telegramSendResult, setTelegramSendResult] = useState<string | null>(null);
  const [telegramPrimaryChatId, setTelegramPrimaryChatId] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setIsRefreshing(true);
      const status = await api.getSystemStatus();
      setSystemStatus(status);
      setLastCheckedAt(new Date());
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

  // Fetch primary Telegram chat when Extensions tab is open and Telegram is active
  useEffect(() => {
    const telegramActive = integrations.some(
      (i) => i.id === 'telegram' && i.status === 'active'
    );
    if (open && activeTab === 'extensions' && telegramActive) {
      api
        .getTelegramPrimaryChat()
        .then((res) => setTelegramPrimaryChatId(res.chat_id))
        .catch(() => setTelegramPrimaryChatId(null));
    }
  }, [open, activeTab, integrations]);

  const handleStartOllama = async () => {
    try {
      setIsOllamaAction(true);
      await api.startOllama();
      setTimeout(fetchStatus, 2000);
    } catch (err) {
      console.error('Failed to start Ollama:', err);
    } finally {
      setIsOllamaAction(false);
    }
  };

  const handleStopOllama = async () => {
    try {
      setIsOllamaAction(true);
      await api.stopOllama();
      setTimeout(fetchStatus, 1000);
    } catch (err) {
      console.error('Failed to stop Ollama:', err);
    } finally {
      setIsOllamaAction(false);
    }
  };

  const handleStopBackend = async () => {
    try {
      setIsBackendAction(true);
      await api.stopBackend();
      setTimeout(fetchStatus, 1000);
    } catch (err) {
      console.error('Failed to stop backend:', err);
    } finally {
      setIsBackendAction(false);
    }
  };

  useEffect(() => {
    if (open) {
      api.getRoutingConfig().then(setRoutingConfig).catch(console.error);
    }
  }, [open]);

  useEffect(() => {
    if (open && activeTab === 'ai') {
      api.getAIServices().then(setAiServices).catch(console.error);
    }
  }, [open, activeTab]);

  const openConnectDialog = (provider: string, name: string) => {
    setConnectDialogProvider({ id: provider, name });
    setConnectDialogApiKey('');
    setConnectDialogError(null);
    setConnectDialogOpen(true);
  };

  const closeConnectDialog = () => {
    setConnectDialogOpen(false);
    setConnectDialogProvider(null);
    setConnectDialogApiKey('');
    setConnectDialogError(null);
  };

  const handleConnect = async () => {
    if (!connectDialogProvider) return;
    const key = connectDialogApiKey.trim();
    if (!key) {
      setConnectDialogError('API key is required');
      return;
    }
    setConnectDialogLoading(true);
    setConnectDialogError(null);
    try {
      const res = await api.connectAIService(connectDialogProvider.id, key);
      if (res.success) {
        closeConnectDialog();
        setAiServices((prev) =>
          prev.map((s) =>
            s.provider === connectDialogProvider.id
              ? { ...s, connected: true, model_count: res.models.length }
              : s
          )
        );
        onServiceChanged?.();
      } else {
        setConnectDialogError(res.error || 'Connection failed');
      }
    } catch (err) {
      setConnectDialogError(
        err instanceof Error ? err.message : 'Connection failed'
      );
    } finally {
      setConnectDialogLoading(false);
    }
  };

  const handleDisconnect = async (provider: string) => {
    try {
      await api.disconnectAIService(provider);
      setAiServices((prev) =>
        prev.map((s) =>
          s.provider === provider
            ? { ...s, connected: false, model_count: 0 }
            : s
        )
      );
      onServiceChanged?.();
    } catch (err) {
      console.error('Disconnect failed:', err);
    }
  };

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
          <TabsList className="grid h-8 w-full grid-cols-3">
            <TabsTrigger value="ai" className="text-[10px]">
              AI
            </TabsTrigger>
            <TabsTrigger value="extensions" className="text-[10px]">
              Extensions
            </TabsTrigger>
            <TabsTrigger value="system" className="text-[10px]">
              System
            </TabsTrigger>
          </TabsList>
        </div>

        <ScrollArea className="flex-1">
          {/* AI Tab (Models & Services + Routing + Privacy) */}
          <TabsContent value="ai" className="mt-0 space-y-4 p-3">
            {/* Models & Services */}
            <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
              AI Services
            </p>
            <p className="text-muted-foreground mb-2 text-[10px]">
              Connect APIs to discover and use commercial models
            </p>
            {aiServices.map((svc) => (
              <Card key={svc.provider} className="bg-background">
                <CardContent className="flex items-center justify-between gap-3 p-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={cn(
                        'flex h-8 w-8 shrink-0 items-center justify-center rounded-md',
                        svc.connected ? 'bg-success/15 text-success' : 'bg-muted'
                      )}
                    >
                      <Globe
                        className={cn(
                          'h-4 w-4',
                          svc.connected ? 'text-success' : 'text-muted-foreground'
                        )}
                      />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-foreground text-xs font-medium">
                          {svc.display_name}
                        </span>
                        <span
                          className={cn(
                            'h-2 w-2 shrink-0 rounded-full',
                            svc.connected ? 'bg-success' : 'bg-muted-foreground/40'
                          )}
                        />
                      </div>
                      <p className="text-muted-foreground text-[10px]">
                        {svc.connected
                          ? `${svc.model_count} model${svc.model_count !== 1 ? 's' : ''} available`
                          : 'Not connected'}
                      </p>
                    </div>
                  </div>
                  <div className="shrink-0">
                    {svc.connected ? (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-destructive hover:bg-destructive/10 h-7 px-2 text-[10px]"
                        onClick={() => handleDisconnect(svc.provider)}
                      >
                        Disconnect
                      </Button>
                    ) : (
                      <Button
                        variant="default"
                        size="sm"
                        className="h-7 px-2 text-[10px]"
                        onClick={() =>
                          openConnectDialog(svc.provider, svc.display_name)
                        }
                      >
                        Connect
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}

            <Dialog open={connectDialogOpen} onOpenChange={(o) => !o && closeConnectDialog()}>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Connect {connectDialogProvider?.name}</DialogTitle>
                  <DialogDescription>
                    Enter your API key. It will be validated and models will be
                    discovered automatically. Keys are stored locally in{' '}
                    <code className="rounded bg-muted px-1">data/credentials.json</code>.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-3 py-2">
                  <div className="space-y-2">
                    <label
                      htmlFor="api-key"
                      className="text-foreground text-sm font-medium"
                    >
                      API Key
                    </label>
                    <Input
                      id="api-key"
                      type="password"
                      placeholder="sk-..."
                      value={connectDialogApiKey}
                      onChange={(e) => {
                        setConnectDialogApiKey(e.target.value);
                        setConnectDialogError(null);
                      }}
                      className="font-mono text-sm"
                      autoComplete="off"
                    />
                  </div>
                  {connectDialogError && (
                    <p className="text-destructive text-sm">{connectDialogError}</p>
                  )}
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={closeConnectDialog}>
                    Cancel
                  </Button>
                  <Button
                    onClick={handleConnect}
                    disabled={connectDialogLoading}
                  >
                    {connectDialogLoading ? (
                      <>
                        <RefreshCw className="mr-2 h-3.5 w-3.5 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      'Connect & Discover'
                    )}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Separator className="my-6" />

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
                            <HoverCard key={m.id} openDelay={200} closeDelay={100}>
                              <HoverCardTrigger asChild>
                                <SelectItem
                                  value={m.id}
                                  className="text-[11px]"
                                >
                                  <div className="flex items-center gap-2">
                                    <span>{m.name}</span>
                                    {(m.tags ?? []).length > 0 && (
                                      <span className="text-muted-foreground flex gap-0.5">
                                        {(m.tags ?? []).slice(0, 2).map((t) => (
                                          <Badge
                                            key={t}
                                            variant="outline"
                                            className="text-[8px] px-1 py-0 font-normal"
                                          >
                                            {t}
                                          </Badge>
                                        ))}
                                      </span>
                                    )}
                                  </div>
                                </SelectItem>
                              </HoverCardTrigger>
                              <HoverCardContent side="right" className="max-w-xs p-0">
                                <ModelInfoCard model={m} variant="compact" />
                              </HoverCardContent>
                            </HoverCard>
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
                            <HoverCard key={m.id} openDelay={200} closeDelay={100}>
                              <HoverCardTrigger asChild>
                                <SelectItem
                                  value={m.id}
                                  className="text-[11px]"
                                >
                                  <div className="flex items-center gap-2">
                                    <span>{m.name}</span>
                                    {(m.tags ?? []).length > 0 && (
                                      <span className="text-muted-foreground flex gap-0.5">
                                        {(m.tags ?? []).slice(0, 2).map((t) => (
                                          <Badge
                                            key={t}
                                            variant="outline"
                                            className="text-[8px] px-1 py-0 font-normal"
                                          >
                                            {t}
                                          </Badge>
                                        ))}
                                      </span>
                                    )}
                                  </div>
                                </SelectItem>
                              </HoverCardTrigger>
                              <HoverCardContent side="right" className="max-w-xs p-0">
                                <ModelInfoCard model={m} variant="compact" />
                              </HoverCardContent>
                            </HoverCard>
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

            <Collapsible
              open={advancedRoutingOpen}
              onOpenChange={setAdvancedRoutingOpen}
            >
              <CollapsibleTrigger asChild>
                <Button
                  variant="ghost"
                  className="text-muted-foreground hover:text-foreground flex h-8 w-full items-center justify-between px-0 text-[10px] font-medium"
                >
                  <span className="flex items-center gap-2">
                    {advancedRoutingOpen ? (
                      <ChevronDown className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5" />
                    )}
                    Advanced: Available Models
                  </span>
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                {(() => {
                  const allTags = Array.from(
                    new Set(models.flatMap((m) => m.tags ?? []))
                  ).sort();
                  const filteredModels =
                    modelTagFilter === null
                      ? models
                      : models.filter((m) =>
                          (m.tags ?? []).includes(modelTagFilter)
                        );
                  return (
                    <>
                      {allTags.length > 0 && (
                        <div className="mb-2 flex flex-wrap items-center gap-1.5">
                          <span className="text-muted-foreground mr-1 text-[10px]">
                            Filter:
                          </span>
                          <Button
                            variant={
                              modelTagFilter === null ? 'secondary' : 'ghost'
                            }
                            size="sm"
                            className="h-6 px-2 text-[10px]"
                            onClick={() => setModelTagFilter(null)}
                          >
                            All
                          </Button>
                          {allTags.map((tag) => (
                            <Button
                              key={tag}
                              variant={
                                modelTagFilter === tag ? 'secondary' : 'ghost'
                              }
                              size="sm"
                              className="h-6 px-2 text-[10px]"
                              onClick={() =>
                                setModelTagFilter(modelTagFilter === tag ? null : tag)
                              }
                            >
                              {tag}
                            </Button>
                          ))}
                        </div>
                      )}
                      {filteredModels.length === 0 ? (
                        <p className="text-muted-foreground py-4 text-center text-xs">
                          No models match the selected tag. Try another filter.
                        </p>
                      ) : (
                      <div className="mt-2 space-y-2">
                  {filteredModels.map((model) => (
                    <HoverCard key={model.id} openDelay={200} closeDelay={100}>
                      <HoverCardTrigger asChild>
                        <Card className="bg-background cursor-help transition-shadow hover:shadow-sm">
                          <CardContent className="flex items-center gap-3 p-3">
                            <div className="bg-muted flex h-8 w-8 shrink-0 items-center justify-center rounded-md">
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
                              <div className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1">
                                <span className="text-muted-foreground text-[10px]">
                                  {model.provider}
                                </span>
                                <Separator orientation="vertical" className="h-2.5" />
                                <span className="text-muted-foreground text-[10px]">
                                  {model.contextWindow}
                                </span>
                                {(model.tags ?? []).length > 0 && (
                                  <>
                                    <Separator orientation="vertical" className="h-2.5" />
                                    <span className="flex flex-wrap gap-1">
                                      {(model.tags ?? []).slice(0, 3).map((tag) => (
                                        <Badge
                                          key={tag}
                                          variant="outline"
                                          className="text-[9px] px-1 py-0 font-normal"
                                        >
                                          {tag}
                                        </Badge>
                                      ))}
                                    </span>
                                  </>
                                )}
                              </div>
                              {model.benefits && (
                                <p className="text-muted-foreground mt-1 line-clamp-2 text-[10px] leading-relaxed">
                                  {model.benefits}
                                </p>
                              )}
                            </div>
                            <Badge
                              variant="secondary"
                              className="shrink-0 px-1.5 py-0 text-[9px]"
                            >
                              {model.type}
                            </Badge>
                          </CardContent>
                        </Card>
                      </HoverCardTrigger>
                      <HoverCardContent side="right" align="start" className="w-80 p-0">
                        <ModelInfoCard model={model} variant="full" />
                      </HoverCardContent>
                    </HoverCard>
                  ))}
                      </div>
                      )}
                    </>
                  );
                })()}
              </CollapsibleContent>
            </Collapsible>

            <Separator className="my-6" />

            <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
              PII & Sensitive Data
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <EyeOff className="text-muted-foreground h-3.5 w-3.5" />
                <span className="text-foreground text-xs font-medium">
                  PII Redactor
                </span>
              </div>
              <p className="text-muted-foreground ml-0.5 px-5 text-[10px] leading-tight">
                Masks names, emails, phone numbers and other PII in model
                responses before display.
              </p>
              <div className="mt-1 px-5">
                <Select
                  value={routingConfig.pii_redactor || 'auto'}
                  onValueChange={(val) =>
                    handleUpdateRouting('pii_redactor', val)
                  }
                >
                  <SelectTrigger className="bg-background h-8 text-[11px]">
                    <SelectValue placeholder="Select model..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto" className="text-[11px]">
                      Off (Auto)
                    </SelectItem>
                    <SelectSeparator />
                    <SelectGroup>
                      <SelectLabel className="text-[10px] font-bold">
                        Commercial
                      </SelectLabel>
                      {models
                        .filter((m) => m.provider !== 'Ollama (Local)')
                        .map((m) => (
                          <HoverCard key={m.id} openDelay={200} closeDelay={100}>
                            <HoverCardTrigger asChild>
                              <SelectItem value={m.id} className="text-[11px]">
                                <div className="flex items-center gap-2">
                                  <span>{m.name}</span>
                                  {(m.tags ?? []).length > 0 && (
                                    <span className="flex gap-0.5">
                                      {(m.tags ?? []).slice(0, 2).map((t) => (
                                        <Badge
                                          key={t}
                                          variant="outline"
                                          className="text-[8px] px-1 py-0 font-normal"
                                        >
                                          {t}
                                        </Badge>
                                      ))}
                                    </span>
                                  )}
                                </div>
                              </SelectItem>
                            </HoverCardTrigger>
                            <HoverCardContent side="right" className="max-w-xs p-0">
                              <ModelInfoCard model={m} variant="compact" />
                            </HoverCardContent>
                          </HoverCard>
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
                          <HoverCard key={m.id} openDelay={200} closeDelay={100}>
                            <HoverCardTrigger asChild>
                              <SelectItem value={m.id} className="text-[11px]">
                                <div className="flex items-center gap-2">
                                  <span>{m.name}</span>
                                  {(m.tags ?? []).length > 0 && (
                                    <span className="flex gap-0.5">
                                      {(m.tags ?? []).slice(0, 2).map((t) => (
                                        <Badge
                                          key={t}
                                          variant="outline"
                                          className="text-[8px] px-1 py-0 font-normal"
                                        >
                                          {t}
                                        </Badge>
                                      ))}
                                    </span>
                                  )}
                                </div>
                              </SelectItem>
                            </HoverCardTrigger>
                            <HoverCardContent side="right" className="max-w-xs p-0">
                              <ModelInfoCard model={m} variant="compact" />
                            </HoverCardContent>
                          </HoverCard>
                        ))}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="bg-muted/40 border-border/50 mt-4 rounded-md border p-3">
              <div className="mb-1.5 flex items-center gap-2">
                <Lock className="text-primary h-3.5 w-3.5" />
                <span className="text-[10px] font-semibold tracking-tight uppercase">
                  Privacy Vault
                </span>
                <Badge variant="outline" className="text-[9px] px-1.5 py-0">
                  Coming soon
                </Badge>
              </div>
              <p className="text-muted-foreground text-[10px] leading-relaxed">
                Local-only storage for sensitive data (PBI-030).
              </p>
            </div>
          </TabsContent>

          {/* Extensions Tab (Skills + MCPs + Integrations) */}
          <TabsContent value="extensions" className="mt-0 space-y-4 p-3">
            <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
              Skills
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

            <Separator className="my-4" />

            <div className="flex items-center justify-between">
              <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
                MCP Servers
              </p>
              <AlertDialog open={mcpAddDialogOpen} onOpenChange={setMcpAddDialogOpen}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-6 bg-transparent text-[10px]"
                      onClick={() => setMcpAddDialogOpen(true)}
                    >
                      <Plug className="mr-1 h-3 w-3" />
                      Add
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Add MCP server via config</p>
                    <p className="text-muted-foreground text-xs">
                      Edit data/mcp_servers.json
                    </p>
                  </TooltipContent>
                </Tooltip>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Add MCP Server</AlertDialogTitle>
                    <AlertDialogDescription asChild>
                      <div className="space-y-2 text-left">
                        <p>
                          Add MCP (Model Context Protocol) servers by editing the
                          config file:
                        </p>
                        <code className="block rounded bg-muted px-2 py-1.5 text-xs font-mono">
                          data/mcp_servers.json
                        </code>
                        <p>
                          Add entries to the <code className="rounded bg-muted px-1">servers</code> array
                          with <code className="rounded bg-muted px-1">id</code>,{' '}
                          <code className="rounded bg-muted px-1">name</code>,{' '}
                          <code className="rounded bg-muted px-1">endpoint</code>, and{' '}
                          <code className="rounded bg-muted px-1">description</code>.
                          Restart the backend to load changes. See docs/MCP_CONFIG.md
                          for the full format.
                        </p>
                      </div>
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogAction onClick={() => setMcpAddDialogOpen(false)}>
                      Got it
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
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
                          : mcp.status === 'configured'
                            ? 'bg-primary/10'
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
                            : mcp.status === 'configured'
                              ? 'text-primary'
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
                              : mcp.status === 'configured'
                                ? 'text-primary border-primary/30'
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

            <Separator className="my-6" />

            <p className="text-muted-foreground text-[10px] font-medium tracking-wider uppercase">
              Connected Services
            </p>
            <p className="text-muted-foreground mb-2 text-[10px]">
              Status only — connect flows coming soon
            </p>
            {integrations.map((integration) => (
              <Card
                key={integration.id}
                className="bg-background cursor-default transition-colors"
              >
                <CardContent className="flex flex-col gap-3 p-3">
                  <div className="flex items-center gap-3">
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
                  </div>
                  {integration.id === 'telegram' && integration.status === 'active' && (
                    <div className="border-border flex flex-col gap-2 rounded border p-2">
                      <p className="text-muted-foreground text-[10px]">
                        Send a message to your primary Telegram chat. Run /setmychat in
                        the bot first.
                      </p>
                      {telegramPrimaryChatId ? (
                        <p className="text-muted-foreground text-[10px] font-mono">
                          Connected chat: {telegramPrimaryChatId}
                        </p>
                      ) : (
                        <p className="text-muted-foreground text-[10px] italic">
                          No primary chat set — run /setmychat in Telegram.
                        </p>
                      )}
                      <div className="flex gap-2">
                        <Input
                          placeholder="Test message..."
                          value={telegramTestMessage}
                          onChange={(e) => {
                            setTelegramTestMessage(e.target.value);
                            setTelegramSendResult(null);
                          }}
                          className="h-7 text-[10px]"
                        />
                        <Button
                          size="sm"
                          className="h-7 shrink-0 px-2 text-[10px]"
                          disabled={!telegramTestMessage.trim() || telegramSending}
                          onClick={async () => {
                            const msg = telegramTestMessage.trim();
                            if (!msg) return;
                            setTelegramSending(true);
                            setTelegramSendResult(null);
                            try {
                              const res = await api.sendToTelegram(msg);
                              setTelegramSendResult('Sent!');
                              setTelegramTestMessage('');
                              if (res.chat_id) setTelegramPrimaryChatId(res.chat_id);
                            } catch (err) {
                              setTelegramSendResult(
                                err instanceof Error ? err.message : 'Failed'
                              );
                            } finally {
                              setTelegramSending(false);
                            }
                          }}
                        >
                          {telegramSending ? 'Sending...' : 'Send'}
                        </Button>
                      </div>
                      {telegramSendResult && (
                        <p
                          className={cn(
                            'text-[10px]',
                            telegramSendResult === 'Sent!'
                              ? 'text-success'
                              : 'text-destructive'
                          )}
                        >
                          {telegramSendResult}
                        </p>
                      )}
                    </div>
                  )}
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
              <div className="flex items-center gap-2">
                {lastCheckedAt && (
                  <span className="text-muted-foreground text-[9px]">
                    {lastCheckedAt.toLocaleTimeString()}
                  </span>
                )}
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
            </div>

            {/* Ollama */}
            <Card className="bg-background">
              <CardContent className="p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        'flex h-8 w-8 items-center justify-center rounded-md',
                        systemStatus?.ollama.status === 'online'
                          ? 'bg-success/15 text-success'
                          : 'bg-destructive/10 text-destructive'
                      )}
                    >
                      <Cpu className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-foreground text-xs font-medium">
                          Ollama Service
                        </span>
                        <span
                          className={cn(
                            'h-2 w-2 shrink-0 rounded-full',
                            systemStatus?.ollama.status === 'online'
                              ? 'bg-success'
                              : 'bg-destructive animate-pulse'
                          )}
                        />
                      </div>
                      <p className="text-muted-foreground text-[10px]">
                        Port 11434 •{' '}
                        {systemStatus?.ollama.status || 'Checking...'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {systemStatus?.ollama.status !== 'online' ? (
                      <Button
                        size="sm"
                        className="h-7 px-2 text-[10px]"
                        onClick={handleStartOllama}
                        disabled={isRefreshing || isOllamaAction}
                      >
                        {isOllamaAction ? (
                          <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
                        ) : (
                          <Power className="mr-1 h-3 w-3" />
                        )}
                        Start
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-destructive hover:bg-destructive/10 h-7 px-2 text-[10px]"
                        onClick={handleStopOllama}
                        disabled={isRefreshing || isOllamaAction}
                      >
                        {isOllamaAction ? (
                          <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
                        ) : (
                          <X className="mr-1 h-3 w-3" />
                        )}
                        Stop
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Backend */}
            <Card className="bg-background">
              <CardContent className="p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        'flex h-8 w-8 items-center justify-center rounded-md',
                        systemStatus?.backend.status === 'online'
                          ? 'bg-success/15 text-success'
                          : 'bg-destructive/10 text-destructive'
                      )}
                    >
                      <Activity className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-foreground text-xs font-medium">
                          Backend API
                        </span>
                        <span
                          className={cn(
                            'h-2 w-2 shrink-0 rounded-full',
                            systemStatus?.backend.status === 'online'
                              ? 'bg-success'
                              : 'bg-destructive animate-pulse'
                          )}
                        />
                      </div>
                      <p className="text-muted-foreground text-[10px]">
                        Port 8001 •{' '}
                        {systemStatus?.backend.status || 'Checking...'}
                      </p>
                      {systemStatus?.backend.status !== 'online' && (
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <p className="text-muted-foreground mt-1 cursor-help text-[9px] underline decoration-dotted">
                              Run ./manage.sh start backend
                            </p>
                          </TooltipTrigger>
                          <TooltipContent side="bottom" className="max-w-48">
                            Start the backend from terminal: ./manage.sh start
                            backend
                          </TooltipContent>
                        </Tooltip>
                      )}
                    </div>
                  </div>
                  {systemStatus?.backend.status === 'online' && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-destructive hover:bg-destructive/10 h-7 px-2 text-[10px]"
                      onClick={handleStopBackend}
                      disabled={isRefreshing || isBackendAction}
                    >
                      {isBackendAction ? (
                        <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
                      ) : (
                        <X className="mr-1 h-3 w-3" />
                      )}
                      Stop
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Frontend */}
            <Card className="bg-background">
              <CardContent className="p-3">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-md',
                      systemStatus?.frontend.status === 'online'
                        ? 'bg-success/15 text-success'
                        : 'bg-destructive/10 text-destructive'
                    )}
                  >
                    <Globe className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-foreground text-xs font-medium">
                        Frontend Web
                      </span>
                      <span className="text-muted-foreground font-normal text-[9px]">
                        (status only)
                      </span>
                      <span
                        className={cn(
                          'h-2 w-2 shrink-0 rounded-full',
                          systemStatus?.frontend.status === 'online'
                            ? 'bg-success'
                            : 'bg-destructive animate-pulse'
                        )}
                      />
                    </div>
                    <p className="text-muted-foreground text-[10px]">
                      Port 3000 •{' '}
                      {systemStatus?.frontend.status || 'Checking...'}
                    </p>
                    {systemStatus?.frontend.status !== 'online' && (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <p className="text-muted-foreground mt-1 cursor-help text-[9px] underline decoration-dotted">
                            Run ./manage.sh start frontend
                          </p>
                        </TooltipTrigger>
                        <TooltipContent side="bottom" className="max-w-48">
                          Start the frontend from terminal: ./manage.sh start
                          frontend
                        </TooltipContent>
                      </Tooltip>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Collapsible
              open={advancedSystemOpen}
              onOpenChange={setAdvancedSystemOpen}
            >
              <CollapsibleTrigger asChild>
                <Button
                  variant="ghost"
                  className="text-muted-foreground hover:text-foreground flex h-8 w-full items-center justify-between px-0 text-[10px] font-medium"
                >
                  <span className="flex items-center gap-2">
                    {advancedSystemOpen ? (
                      <ChevronDown className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5" />
                    )}
                    Advanced: Lifecycle Control
                  </span>
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="bg-muted/40 border-border/50 mt-2 rounded-md border p-3 space-y-2">
                  <p className="text-muted-foreground text-[10px] leading-relaxed">
                    Full lifecycle control via{' '}
                    <code className="bg-background px-1">manage.sh</code>:
                  </p>
                  <p className="text-muted-foreground font-mono text-[9px] leading-relaxed">
                    ./manage.sh start [ollama|backend|frontend|all]
                    <br />
                    ./manage.sh stop [ollama|backend|frontend|all]
                    <br />
                    ./manage.sh status
                  </p>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  );
}
