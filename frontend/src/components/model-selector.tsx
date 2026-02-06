"use client"

import {
  Globe,
  Cpu,
  Server,
  Lock,
  Activity,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
  SelectSeparator,
} from "@/components/ui/select"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import type { Model } from "@/lib/store"

interface ModelSelectorProps {
  models: Model[]
  selectedModelId: string
  onSelectModel: (id: string) => void
  agenticMode: boolean
  onToggleAgenticMode: () => void
}

export function ModelSelector({
  models,
  selectedModelId,
  onSelectModel,
  agenticMode,
  onToggleAgenticMode,
}: ModelSelectorProps) {
  const selectedModel = models.find((m) => m.id === selectedModelId)

  const commercial = models.filter((m) => m.type === "commercial")
  const ollama = models.filter((m) => m.type === "ollama")
  const local = models.filter((m) => m.type === "local")

  const getStatusColor = (status: Model["status"]) => {
    switch (status) {
      case "online":
        return "bg-success"
      case "loading":
        return "bg-warning animate-pulse-dot"
      case "offline":
        return "bg-muted-foreground/40"
    }
  }

  const getTypeIcon = (type: Model["type"]) => {
    switch (type) {
      case "commercial":
        return <Globe className="h-3 w-3 text-primary" />
      case "ollama":
        return <Server className="h-3 w-3 text-success" />
      case "local":
        return <Cpu className="h-3 w-3 text-warning" />
    }
  }

  return (
    <TooltipProvider>
      <div className="flex items-center gap-2">
        {/* Agentic toggle */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={agenticMode ? "secondary" : "ghost"}
              size="sm"
              className={cn(
                "h-8 gap-1.5 px-2.5 text-xs font-medium transition-all",
                agenticMode
                  ? "bg-primary/10 text-primary hover:bg-primary/15 hover:text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
              onClick={onToggleAgenticMode}
            >
              <Activity className="h-3.5 w-3.5" />
              <span>Agentic</span>
              {agenticMode && (
                <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse-dot" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {agenticMode
              ? "Agentic mode: AI auto-selects the best model per task"
              : "Click to enable agentic model selection"}
          </TooltipContent>
        </Tooltip>

        {/* Model selector */}
        {agenticMode ? (
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex h-8 items-center gap-2 rounded-md border border-border bg-muted px-3 cursor-default">
                <Lock className="h-3 w-3 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Auto</span>
                {selectedModel && (
                  <>
                    <span className="text-border">|</span>
                    <span className="text-xs text-muted-foreground">{selectedModel.name}</span>
                    <span className={cn("h-1.5 w-1.5 rounded-full", getStatusColor(selectedModel.status))} />
                  </>
                )}
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p className="font-medium">Agentic Model Selection</p>
              <p className="text-muted-foreground">
                Currently using {selectedModel?.name}. Model is automatically
                selected based on task complexity.
              </p>
            </TooltipContent>
          </Tooltip>
        ) : (
          <Select value={selectedModelId} onValueChange={onSelectModel}>
            <SelectTrigger className="h-8 w-52 text-xs">
              <div className="flex items-center gap-2">
                {selectedModel && getTypeIcon(selectedModel.type)}
                <SelectValue />
                {selectedModel && (
                  <span className={cn("h-1.5 w-1.5 rounded-full ml-auto", getStatusColor(selectedModel.status))} />
                )}
              </div>
            </SelectTrigger>
            <SelectContent>
              {commercial.length > 0 && (
                <SelectGroup>
                  <SelectLabel className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider">
                    <Globe className="h-3 w-3" />
                    Commercial API
                  </SelectLabel>
                  {commercial.map((m) => (
                    <SelectItem key={m.id} value={m.id} disabled={m.status === "offline"}>
                      <div className="flex items-center gap-2">
                        <span className={cn("h-1.5 w-1.5 rounded-full", getStatusColor(m.status))} />
                        <span>{m.name}</span>
                        <span className="text-[10px] text-muted-foreground ml-auto">{m.contextWindow}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectGroup>
              )}
              {ollama.length > 0 && (
                <>
                  <SelectSeparator />
                  <SelectGroup>
                    <SelectLabel className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider">
                      <Server className="h-3 w-3" />
                      Ollama
                    </SelectLabel>
                    {ollama.map((m) => (
                      <SelectItem key={m.id} value={m.id} disabled={m.status === "offline"}>
                        <div className="flex items-center gap-2">
                          <span className={cn("h-1.5 w-1.5 rounded-full", getStatusColor(m.status))} />
                          <span>{m.name}</span>
                          <span className="text-[10px] text-muted-foreground ml-auto">{m.contextWindow}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </>
              )}
              {local.length > 0 && (
                <>
                  <SelectSeparator />
                  <SelectGroup>
                    <SelectLabel className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider">
                      <Cpu className="h-3 w-3" />
                      Local
                    </SelectLabel>
                    {local.map((m) => (
                      <SelectItem key={m.id} value={m.id} disabled={m.status === "offline"}>
                        <div className="flex items-center gap-2">
                          <span className={cn("h-1.5 w-1.5 rounded-full", getStatusColor(m.status))} />
                          <span>{m.name}</span>
                          <span className="text-[10px] text-muted-foreground ml-auto">{m.contextWindow}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </>
              )}
            </SelectContent>
          </Select>
        )}
      </div>
    </TooltipProvider>
  )
}
