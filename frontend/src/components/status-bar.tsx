'use client';

import { Cpu, Globe, Server, Wifi, Activity, ShieldCheck } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Separator } from '@/components/ui/separator';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from '@/components/ui/tooltip';
import type { AgentProcess, Model } from '@/lib/store';

const TYPE_ICONS: Record<string, LucideIcon> = {
  commercial: Globe,
  local: Cpu,
  ollama: Server,
};

interface StatusBarProps {
  activeModel: Model | undefined;
  agentProcesses: AgentProcess[];
  agenticMode: boolean;
}

export function StatusBar({
  activeModel,
  agentProcesses,
  agenticMode,
}: StatusBarProps) {
  const runningProcesses = agentProcesses.filter((p) => p.status === 'running');
  const internalCount = runningProcesses.filter(
    (p) => p.type === 'internal'
  ).length;
  const externalCount = runningProcesses.filter(
    (p) => p.type === 'external'
  ).length;

  const activeType = activeModel?.type;

  const getTypeLabel = (type: Model['type'] | undefined) => {
    if (!type) return 'No Model';
    switch (type) {
      case 'commercial':
        return 'Cloud API';
      case 'local':
        return 'Local Model';
      case 'ollama':
        return 'Ollama';
    }
  };

  const TypeIcon =
    activeType && activeType in TYPE_ICONS ? TYPE_ICONS[activeType] : Cpu;

  return (
    <TooltipProvider>
      <footer className="border-border bg-card text-muted-foreground flex h-7 items-center justify-between border-t px-3 text-[11px]">
        {/* Left side */}
        <div className="flex items-center gap-3">
          {activeModel && (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex cursor-default items-center gap-1.5">
                  <TypeIcon className="h-3 w-3" />
                  <span>{getTypeLabel(activeModel.type)}</span>
                  <span
                    className={cn(
                      'h-1.5 w-1.5 rounded-full',
                      activeModel.status === 'online'
                        ? 'bg-success'
                        : activeModel.status === 'loading'
                          ? 'bg-warning animate-pulse-dot'
                          : 'bg-destructive'
                    )}
                  />
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p className="font-medium">{activeModel.name}</p>
                <p className="text-muted-foreground">
                  {activeModel.provider} / {activeModel.contextWindow} context
                </p>
              </TooltipContent>
            </Tooltip>
          )}

          {agenticMode && (
            <>
              <Separator orientation="vertical" className="h-3" />
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex cursor-default items-center gap-1.5">
                    <Activity className="text-primary h-3 w-3" />
                    <span className="text-primary">Agentic</span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="font-medium">Status: Agentic mode active</p>
                  <p className="text-muted-foreground">
                    Model selection handled automatically. Toggle in chat input.
                  </p>
                </TooltipContent>
              </Tooltip>
            </>
          )}

          <Separator orientation="vertical" className="h-3" />
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="group flex cursor-default items-center gap-1.5">
                <ShieldCheck
                  className={cn(
                    'h-3 w-3 transition-colors',
                    activeModel?.type !== 'commercial'
                      ? 'text-success'
                      : 'text-muted-foreground/40'
                  )}
                />
                <span
                  className={cn(
                    'transition-colors',
                    activeModel?.type !== 'commercial'
                      ? 'text-foreground'
                      : 'text-muted-foreground/40'
                  )}
                >
                  Vault
                </span>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p className="font-medium">
                Status: {activeModel?.type !== 'commercial' ? 'Local data only' : 'Cloud API in use'}
              </p>
              <p className="text-muted-foreground">
                {activeModel?.type !== 'commercial'
                  ? 'Sensitive data stays on device. Configure in Settings → AI.'
                  : 'Check Settings → AI for data handling.'}
              </p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {runningProcesses.length > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex cursor-default items-center gap-1.5">
                  <span className="bg-primary animate-pulse-dot h-1.5 w-1.5 rounded-full" />
                  <span>
                    {runningProcesses.length} agent
                    {runningProcesses.length > 1 ? 's' : ''}
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="space-y-1">
                  <p className="font-medium">Active Background Agents</p>
                  {runningProcesses.map((p) => (
                    <div key={p.id} className="flex items-center gap-2 text-xs">
                      <span
                        className={cn(
                          'h-1.5 w-1.5 rounded-full',
                          p.type === 'internal' ? 'bg-success' : 'bg-warning'
                        )}
                      />
                      <span>{p.name}</span>
                      <span className="text-muted-foreground">({p.model})</span>
                    </div>
                  ))}
                </div>
              </TooltipContent>
            </Tooltip>
          )}

          {(internalCount > 0 || externalCount > 0) && (
            <>
              <Separator orientation="vertical" className="h-3" />
              <div className="flex items-center gap-2">
                {internalCount > 0 && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex cursor-default items-center gap-1">
                        <Cpu className="text-success h-3 w-3" />
                        <span>{internalCount}</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      {internalCount} local/internal process
                      {internalCount > 1 ? 'es' : ''}
                    </TooltipContent>
                  </Tooltip>
                )}
                {externalCount > 0 && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex cursor-default items-center gap-1">
                        <Wifi className="text-warning h-3 w-3" />
                        <span>{externalCount}</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      {externalCount} external API call
                      {externalCount > 1 ? 's' : ''}
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
            </>
          )}
        </div>
      </footer>
    </TooltipProvider>
  );
}
