"use client"

import {
  Cpu,
  Globe,
  Server,
  Wifi,
  Activity,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { Separator } from "@/components/ui/separator"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import type { AgentProcess, Model } from "@/lib/store"

const TYPE_ICONS: Record<Model["type"], LucideIcon> = {
  commercial: Globe,
  local: Cpu,
  ollama: Server,
}

interface StatusBarProps {
  activeModel: Model | undefined
  agentProcesses: AgentProcess[]
  agenticMode: boolean
}

export function StatusBar({
  activeModel,
  agentProcesses,
  agenticMode,
}: StatusBarProps) {
  const runningProcesses = agentProcesses.filter((p) => p.status === "running")
  const internalCount = runningProcesses.filter((p) => p.type === "internal").length
  const externalCount = runningProcesses.filter((p) => p.type === "external").length

  const getTypeLabel = (type: Model["type"]) => {
    switch (type) {
      case "commercial":
        return "Cloud API"
      case "local":
        return "Local Model"
      case "ollama":
        return "Ollama"
    }
  }

  const TypeIcon = activeModel ? TYPE_ICONS[activeModel.type] : Cpu

  return (
    <TooltipProvider>
      <footer className="flex h-7 items-center justify-between border-t border-border bg-card px-3 text-[11px] text-muted-foreground">
        {/* Left side */}
        <div className="flex items-center gap-3">
          {activeModel && (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-1.5 cursor-default">
                  <TypeIcon className="h-3 w-3" />
                  <span>{getTypeLabel(activeModel.type)}</span>
                  <span
                    className={cn(
                      "h-1.5 w-1.5 rounded-full",
                      activeModel.status === "online"
                        ? "bg-success"
                        : activeModel.status === "loading"
                          ? "bg-warning animate-pulse-dot"
                          : "bg-destructive"
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
                  <div className="flex items-center gap-1.5 cursor-default">
                    <Activity className="h-3 w-3 text-primary" />
                    <span className="text-primary">Agentic</span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  Agentic mode: Model selection handled automatically
                </TooltipContent>
              </Tooltip>
            </>
          )}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {runningProcesses.length > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-1.5 cursor-default">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse-dot" />
                  <span>
                    {runningProcesses.length} agent
                    {runningProcesses.length > 1 ? "s" : ""}
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
                          "h-1.5 w-1.5 rounded-full",
                          p.type === "internal" ? "bg-success" : "bg-warning"
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
                      <div className="flex items-center gap-1 cursor-default">
                        <Cpu className="h-3 w-3 text-success" />
                        <span>{internalCount}</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      {internalCount} local/internal process
                      {internalCount > 1 ? "es" : ""}
                    </TooltipContent>
                  </Tooltip>
                )}
                {externalCount > 0 && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex items-center gap-1 cursor-default">
                        <Wifi className="h-3 w-3 text-warning" />
                        <span>{externalCount}</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      {externalCount} external API call
                      {externalCount > 1 ? "s" : ""}
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
            </>
          )}
        </div>
      </footer>
    </TooltipProvider>
  )
}
