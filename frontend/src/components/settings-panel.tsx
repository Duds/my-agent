"use client"

import { useState } from "react"
import {
  X,
  Cpu,
  Globe,
  Server,
  Zap,
  Plug,
  Settings2,
  CircleDot,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent } from "@/components/ui/card"
import type { Model, Skill, MCP, Integration } from "@/lib/store"

interface SettingsPanelProps {
  open: boolean
  onClose: () => void
  models: Model[]
  skills: Skill[]
  mcps: MCP[]
  integrations: Integration[]
  onToggleSkill: (id: string) => void
}

export function SettingsPanel({
  open,
  onClose,
  models,
  skills,
  mcps,
  integrations,
  onToggleSkill,
}: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState("models")

  if (!open) return null

  return (
    <div className="flex h-full w-80 flex-col border-l border-border bg-card">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <Settings2 className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-semibold text-foreground">Settings</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={onClose}
        >
          <X className="h-3.5 w-3.5" />
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="px-3 pt-3">
          <TabsList className="grid w-full grid-cols-4 h-8">
            <TabsTrigger value="models" className="text-[10px]">
              Models
            </TabsTrigger>
            <TabsTrigger value="skills" className="text-[10px]">
              Skills
            </TabsTrigger>
            <TabsTrigger value="mcps" className="text-[10px]">
              MCPs
            </TabsTrigger>
            <TabsTrigger value="integrations" className="text-[10px]">
              Integrations
            </TabsTrigger>
          </TabsList>
        </div>

        <ScrollArea className="flex-1">
          {/* Models Tab */}
          <TabsContent value="models" className="mt-0 p-3 space-y-2">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium mb-3">
              Available Models
            </p>
            {models.map((model) => (
              <Card key={model.id} className="bg-background">
                <CardContent className="flex items-center gap-3 p-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted">
                    {model.type === "commercial" && <Globe className="h-4 w-4 text-primary" />}
                    {model.type === "ollama" && <Server className="h-4 w-4 text-success" />}
                    {model.type === "local" && <Cpu className="h-4 w-4 text-warning" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-foreground truncate">{model.name}</span>
                      <span
                        className={cn(
                          "h-1.5 w-1.5 rounded-full shrink-0",
                          model.status === "online"
                            ? "bg-success"
                            : model.status === "loading"
                              ? "bg-warning animate-pulse-dot"
                              : "bg-muted-foreground/40"
                        )}
                      />
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] text-muted-foreground">{model.provider}</span>
                      <Separator orientation="vertical" className="h-2.5" />
                      <span className="text-[10px] text-muted-foreground">{model.contextWindow}</span>
                    </div>
                  </div>
                  <Badge variant="secondary" className="text-[9px] px-1.5 py-0 shrink-0">
                    {model.type}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Skills Tab */}
          <TabsContent value="skills" className="mt-0 p-3 space-y-2">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium mb-3">
              Agent Capabilities
            </p>
            {skills.map((skill) => (
              <Card key={skill.id} className="bg-background">
                <CardContent className="flex items-center gap-3 p-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted">
                    <Zap className={cn("h-4 w-4", skill.enabled ? "text-primary" : "text-muted-foreground")} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-medium text-foreground">{skill.name}</span>
                    <p className="text-[10px] text-muted-foreground mt-0.5 leading-relaxed">{skill.description}</p>
                  </div>
                  <Switch
                    checked={skill.enabled}
                    onCheckedChange={() => onToggleSkill(skill.id)}
                    className="shrink-0"
                  />
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* MCPs Tab */}
          <TabsContent value="mcps" className="mt-0 p-3 space-y-2">
            <div className="flex items-center justify-between mb-3">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">
                MCP Servers
              </p>
              <Button variant="outline" size="sm" className="h-6 text-[10px] bg-transparent">
                <Plug className="h-3 w-3 mr-1" />
                Add
              </Button>
            </div>
            {mcps.map((mcp) => (
              <Card key={mcp.id} className="bg-background">
                <CardContent className="flex items-center gap-3 p-3">
                  <div
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-md",
                      mcp.status === "connected"
                        ? "bg-success/10"
                        : mcp.status === "error"
                          ? "bg-destructive/10"
                          : "bg-muted"
                    )}
                  >
                    <Plug
                      className={cn(
                        "h-4 w-4",
                        mcp.status === "connected"
                          ? "text-success"
                          : mcp.status === "error"
                            ? "text-destructive"
                            : "text-muted-foreground"
                      )}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-foreground">{mcp.name}</span>
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-[9px] px-1.5 py-0",
                          mcp.status === "connected"
                            ? "text-success border-success/30"
                            : mcp.status === "error"
                              ? "text-destructive border-destructive/30"
                              : "text-muted-foreground"
                        )}
                      >
                        {mcp.status}
                      </Badge>
                    </div>
                    <p className="text-[10px] font-mono text-muted-foreground mt-0.5 truncate">
                      {mcp.endpoint}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Integrations Tab */}
          <TabsContent value="integrations" className="mt-0 p-3 space-y-2">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium mb-3">
              Connected Services
            </p>
            {integrations.map((integration) => (
              <Card
                key={integration.id}
                className="bg-background cursor-pointer hover:bg-accent transition-colors"
              >
                <CardContent className="flex items-center gap-3 p-3">
                  <div
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-md",
                      integration.status === "active"
                        ? "bg-primary/10"
                        : integration.status === "error"
                          ? "bg-destructive/10"
                          : "bg-muted"
                    )}
                  >
                    <CircleDot
                      className={cn(
                        "h-4 w-4",
                        integration.status === "active"
                          ? "text-primary"
                          : integration.status === "error"
                            ? "text-destructive"
                            : "text-muted-foreground"
                      )}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-foreground">{integration.name}</span>
                      <Badge variant="secondary" className="text-[9px] px-1.5 py-0">
                        {integration.type}
                      </Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{integration.description}</p>
                  </div>
                  <span
                    className={cn(
                      "h-2 w-2 rounded-full shrink-0",
                      integration.status === "active"
                        ? "bg-success"
                        : integration.status === "error"
                          ? "bg-destructive"
                          : "bg-muted-foreground/40"
                    )}
                  />
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  )
}
