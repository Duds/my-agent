"use client"

import { ListChecks } from "lucide-react"

/**
 * Placeholder for Automation Hub status logs.
 * Will show execution logs when backend returns data (PBI-032).
 */
export function StatusLogs() {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      <ListChecks className="h-8 w-8 text-muted-foreground/50 mb-2" />
      <p className="text-sm font-medium text-muted-foreground">Status logs</p>
      <p className="text-xs text-muted-foreground/70 mt-0.5">
        Execution logs will appear when Automation Hub API is wired
      </p>
    </div>
  )
}
