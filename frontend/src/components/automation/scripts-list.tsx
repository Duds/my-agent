"use client"

import { FileCode } from "lucide-react"

/**
 * Placeholder for Automation Hub scripts list.
 * Will show scripts/configs when backend returns data (PBI-032).
 */
export function ScriptsList() {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      <FileCode className="h-8 w-8 text-muted-foreground/50 mb-2" />
      <p className="text-sm font-medium text-muted-foreground">Scripts</p>
      <p className="text-xs text-muted-foreground/70 mt-0.5">
        Script list will appear when Automation Hub API is wired
      </p>
    </div>
  )
}
