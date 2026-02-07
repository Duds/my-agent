"use client"

import { AlertTriangle } from "lucide-react"

/**
 * Placeholder for Automation Hub error reports.
 * Will show error history when backend returns data (PBI-032).
 */
export function ErrorReports() {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      <AlertTriangle className="h-8 w-8 text-muted-foreground/50 mb-2" />
      <p className="text-sm font-medium text-muted-foreground">Error reports</p>
      <p className="text-xs text-muted-foreground/70 mt-0.5">
        Error history will appear when Automation Hub API is wired
      </p>
    </div>
  )
}
