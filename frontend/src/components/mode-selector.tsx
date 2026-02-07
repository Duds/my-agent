"use client"

import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import type { Mode } from "@/lib/api-client"

interface ModeSelectorProps {
  modes: Mode[]
  selectedModeId: string
  onSelectMode: (id: string) => void
  className?: string
}

export function ModeSelector({
  modes,
  selectedModeId,
  onSelectMode,
  className,
}: ModeSelectorProps) {
  const selectedMode = modes.find((m) => m.id === selectedModeId) ?? modes[0]

  return (
    <TooltipProvider>
      <Select value={selectedModeId || "general"} onValueChange={onSelectMode}>
        <Tooltip>
          <TooltipTrigger asChild>
            <SelectTrigger
              className={cn(
                "h-7 w-[100px] border-0 bg-transparent px-2 text-xs font-medium text-muted-foreground hover:text-foreground focus:ring-0 focus:ring-offset-0",
                className
              )}
            >
              <SelectValue>{selectedMode?.name ?? "General"}</SelectValue>
              <ChevronDown className="h-3 w-3 ml-0.5 opacity-50" />
            </SelectTrigger>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p className="font-medium">Mode</p>
            <p className="text-muted-foreground text-xs">
              {selectedMode?.description ?? "General-purpose assistance"}
            </p>
          </TooltipContent>
        </Tooltip>
        <SelectContent>
          {modes.map((mode) => (
            <SelectItem key={mode.id} value={mode.id} className="text-xs">
              {mode.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </TooltipProvider>
  )
}
