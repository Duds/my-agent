"use client"

import { ChevronDown, Cpu, Globe, Server } from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
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
import { ModelInfoCard } from "@/components/model-info-card"
import type { Model } from "@/lib/store"

interface ChatInputModelSelectorProps {
  models: Model[]
  selectedModelId: string
  onSelectModel: (id: string) => void
  className?: string
}

const AUTO_VALUE = "auto"

export function ChatInputModelSelector({
  models,
  selectedModelId,
  onSelectModel,
  className,
}: ChatInputModelSelectorProps) {
  const isAuto = !selectedModelId || selectedModelId === AUTO_VALUE
  const selectedModel = models.find((m) => m.id === selectedModelId)

  const commercial = models.filter((m) => m.type === "commercial")
  const ollama = models.filter((m) => m.type === "ollama")
  const local = models.filter((m) => m.type === "local")

  const getTypeIcon = (type: Model["type"]) => {
    switch (type) {
      case "commercial":
        return <Globe className="h-3 w-3" />
      case "ollama":
        return <Server className="h-3 w-3" />
      case "local":
        return <Cpu className="h-3 w-3" />
    }
  }

  return (
    <TooltipProvider>
      <Select
        value={isAuto ? AUTO_VALUE : selectedModelId}
        onValueChange={(v) => onSelectModel(v === AUTO_VALUE ? "" : v)}
      >
        <Tooltip>
          <TooltipTrigger asChild>
            <SelectTrigger
              className={cn(
                "h-7 w-[100px] border-0 bg-transparent px-2 text-xs font-medium focus:ring-0 focus:ring-offset-0",
                isAuto
                  ? "text-muted-foreground hover:text-foreground"
                  : "text-foreground",
                className
              )}
            >
              <SelectValue>
                {isAuto ? "Auto" : selectedModel?.name ?? "Auto"}
              </SelectValue>
              <ChevronDown className="h-3 w-3 ml-0.5 opacity-50" />
            </SelectTrigger>
          </TooltipTrigger>
          <TooltipContent side="top" className={!isAuto && selectedModel ? "max-w-xs p-0" : undefined}>
            {!isAuto && selectedModel ? (
              <ModelInfoCard model={selectedModel} variant="compact" />
            ) : (
              <>
                <p className="font-medium">{isAuto ? "Auto" : "Pinned model"}</p>
                <p className="text-muted-foreground text-xs">
                  {isAuto
                    ? "Best-fit routing; model selected per message"
                    : `${selectedModel?.name ?? ""} — manually overridden`}
                </p>
              </>
            )}
          </TooltipContent>
        </Tooltip>
        <SelectContent>
          <SelectItem value={AUTO_VALUE} className="text-xs">
            <span className="text-muted-foreground">Auto</span>
          </SelectItem>
          <SelectSeparator />
          {commercial.length > 0 && (
            <SelectGroup>
              <SelectLabel className="text-[10px] uppercase tracking-wider">
                Commercial
              </SelectLabel>
              {commercial.map((m) => (
                <Tooltip key={m.id}>
                  <TooltipTrigger asChild>
                    <SelectItem value={m.id} className="text-xs">
                      <div className="flex items-center gap-2">
                        {getTypeIcon(m.type)}
                        <span>{m.name}</span>
                        {(m.tags ?? []).length > 0 && (
                          <span className="flex gap-0.5">
                            {(m.tags ?? []).slice(0, 2).map((t) => (
                              <Badge key={t} variant="outline" className="text-[8px] px-1 py-0 font-normal">
                                {t}
                              </Badge>
                            ))}
                          </span>
                        )}
                      </div>
                    </SelectItem>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="max-w-xs p-0">
                    <ModelInfoCard model={m} variant="compact" />
                  </TooltipContent>
                </Tooltip>
              ))}
            </SelectGroup>
          )}
          {ollama.length > 0 && (
            <>
              <SelectSeparator />
              <SelectGroup>
                <SelectLabel className="text-[10px] uppercase tracking-wider">
                  Ollama
                </SelectLabel>
                {ollama.map((m) => (
                  <Tooltip key={m.id}>
                    <TooltipTrigger asChild>
                      <SelectItem value={m.id} className="text-xs">
                        <div className="flex items-center gap-2">
                          {getTypeIcon(m.type)}
                          <span>{m.name}</span>
                          {(m.tags ?? []).length > 0 && (
                            <span className="flex gap-0.5">
                              {(m.tags ?? []).slice(0, 2).map((t) => (
                                <Badge key={t} variant="outline" className="text-[8px] px-1 py-0 font-normal">
                                  {t}
                                </Badge>
                              ))}
                            </span>
                          )}
                        </div>
                      </SelectItem>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="max-w-xs p-0">
                      <ModelInfoCard model={m} variant="compact" />
                    </TooltipContent>
                  </Tooltip>
                ))}
              </SelectGroup>
            </>
          )}
          {local.length > 0 && (
            <>
              <SelectSeparator />
              <SelectGroup>
                <SelectLabel className="text-[10px] uppercase tracking-wider">
                  Local
                </SelectLabel>
                {local.map((m) => (
                  <Tooltip key={m.id}>
                    <TooltipTrigger asChild>
                      <SelectItem value={m.id} className="text-xs">
                        <div className="flex items-center gap-2">
                          {getTypeIcon(m.type)}
                          <span>{m.name}</span>
                          {(m.tags ?? []).length > 0 && (
                            <span className="flex gap-0.5">
                              {(m.tags ?? []).slice(0, 2).map((t) => (
                                <Badge key={t} variant="outline" className="text-[8px] px-1 py-0 font-normal">
                                  {t}
                                </Badge>
                              ))}
                            </span>
                          )}
                        </div>
                      </SelectItem>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="max-w-xs p-0">
                      <ModelInfoCard model={m} variant="compact" />
                    </TooltipContent>
                  </Tooltip>
                ))}
              </SelectGroup>
            </>
          )}
        </SelectContent>
      </Select>
    </TooltipProvider>
  )
}
