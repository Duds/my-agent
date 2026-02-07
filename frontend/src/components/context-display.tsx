"use client"

import { Monitor, Activity } from "lucide-react"
import { cn } from "@/lib/utils"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface ContextDisplayProps {
  activeWindow?: string
  currentActivity?: string
  className?: string
}

/**
 * Context display for active window and current activity.
 * Per research: status bar for passive context; popover for on-demand detail.
 */
export function ContextDisplay({
  activeWindow,
  currentActivity,
  className,
}: ContextDisplayProps) {
  const hasContext = activeWindow || currentActivity

  if (!hasContext) {
    return null
  }

  return (
    <TooltipProvider>
      <Popover>
        <PopoverTrigger asChild>
          <Tooltip>
            <TooltipTrigger asChild>
              <div
                className={cn(
                  "flex items-center gap-1.5 cursor-default text-muted-foreground hover:text-foreground transition-colors",
                  className
                )}
              >
                <Monitor className="h-3 w-3" />
                <span className="text-[10px] truncate max-w-24">
                  {activeWindow ?? "Unknown"}
                </span>
              </div>
            </TooltipTrigger>
            <TooltipContent side="top">
              <p className="font-medium">Active context</p>
              <p className="text-muted-foreground text-xs">
                {activeWindow ?? "—"} / {currentActivity ?? "—"}
              </p>
            </TooltipContent>
          </Tooltip>
        </PopoverTrigger>
        <PopoverContent align="start" className="w-64">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Monitor className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs font-medium text-muted-foreground">Active window</p>
                <p className="text-sm">{activeWindow ?? "—"}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs font-medium text-muted-foreground">Current activity</p>
                <p className="text-sm">{currentActivity ?? "—"}</p>
              </div>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </TooltipProvider>
  )
}
