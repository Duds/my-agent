"use client"

import React from "react"
import {
  Bot,
  Code,
  BarChart3,
  FileText,
  Server,
  Search,
  Check,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import type { Persona } from "@/lib/store"

interface PersonaSelectorProps {
  personas: Persona[]
  selectedPersonaId: string
  onSelectPersona: (id: string) => void
  open: boolean
  onOpenChange: (open: boolean) => void
}

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Bot,
  Code,
  BarChart3,
  FileText,
  Server,
  Search,
}

export function PersonaSelector({
  personas,
  selectedPersonaId,
  onSelectPersona,
  open,
  onOpenChange,
}: PersonaSelectorProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Select Persona</DialogTitle>
          <DialogDescription>
            Choose an AI persona to tailor the conversation style and expertise.
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 gap-2 mt-2">
          {personas.map((persona) => {
            const Icon = ICON_MAP[persona.icon] || Bot
            const isSelected = persona.id === selectedPersonaId
            return (
              <button
                key={persona.id}
                onClick={() => {
                  onSelectPersona(persona.id)
                  onOpenChange(false)
                }}
                className={cn(
                  "relative flex flex-col items-start gap-2 rounded-lg border p-4 text-left transition-all",
                  isSelected
                    ? "border-primary bg-primary/5 ring-1 ring-primary/20"
                    : "border-border bg-card hover:bg-accent"
                )}
              >
                {isSelected && (
                  <div className="absolute top-2 right-2">
                    <Check className="h-3.5 w-3.5 text-primary" />
                  </div>
                )}
                <div
                  className="flex h-9 w-9 items-center justify-center rounded-lg"
                  style={{ backgroundColor: `${persona.color}15`, color: persona.color }}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-foreground">
                    {persona.name}
                  </p>
                  <p className="text-[10px] text-muted-foreground leading-relaxed mt-0.5">
                    {persona.description}
                  </p>
                </div>
              </button>
            )
          })}
        </div>
      </DialogContent>
    </Dialog>
  )
}

export function PersonaBadge({
  persona,
  onClick,
}: {
  persona: Persona
  onClick: () => void
}) {
  const Icon = ICON_MAP[persona.icon] || Bot
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 gap-1.5 px-2.5 text-xs font-medium"
            style={{ color: persona.color }}
            onClick={onClick}
          >
            <Icon className="h-3.5 w-3.5" />
            <span>{persona.name}</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>{persona.description}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
