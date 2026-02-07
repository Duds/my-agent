"use client"

import React, { useState, useRef, useEffect } from "react"
import {
  Send,
  Bot,
  User,
  Loader2,
  Wrench,
  CheckCircle2,
  AlertCircle,
  Copy,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ModeSelector } from "@/components/mode-selector"
import { ChatInputModelSelector } from "@/components/chat-input-model-selector"
import type { Message, Conversation, Model } from "@/lib/store"
import type { Mode } from "@/lib/api-client"

interface ChatInterfaceProps {
  conversation: Conversation | null
  onSendMessage: (content: string) => void
  isStreaming: boolean
  modes?: Mode[]
  models?: Model[]
  selectedModeId?: string
  selectedModelId?: string
  onSelectMode?: (id: string) => void
  onSelectModel?: (id: string) => void
}

export function ChatInterface({
  conversation,
  onSendMessage,
  isStreaming,
  modes = [],
  models = [],
  selectedModeId = "general",
  selectedModelId = "",
  onSelectMode = () => {},
  onSelectModel = () => {},
}: ChatInterfaceProps) {
  const [input, setInput] = useState("")
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [conversation?.messages])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`
    }
  }, [input])

  const handleSubmit = () => {
    if (!input.trim() || isStreaming) return
    if (!hasConversation) return
    onSendMessage(input.trim())
    setInput("")
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const hasConversation = !!conversation

  return (
    <div className="flex flex-1 flex-col">
      {/* Messages or empty state */}
      <ScrollArea className="flex-1">
        <div ref={scrollRef} className="mx-auto max-w-3xl space-y-6 px-4 py-6">
          {!hasConversation ? (
            <div className="flex flex-1 flex-col items-center justify-center py-16">
              <Avatar className="mx-auto h-12 w-12">
                <AvatarFallback className="bg-muted">
                  <Bot className="h-6 w-6 text-muted-foreground" />
                </AvatarFallback>
              </Avatar>
              <div className="mt-3 text-center">
                <h3 className="text-sm font-medium text-foreground">
                  Start a new conversation
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Select a conversation or create a new one from the sidebar
                </p>
              </div>
            </div>
          ) : (
            <>
          {conversation!.messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {hasConversation && isStreaming && (
            <div className="flex items-start gap-3">
              <Avatar className="h-7 w-7">
                <AvatarFallback className="bg-primary/10 text-primary">
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div className="flex items-center gap-2 pt-1">
                <div className="flex gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-pulse-dot" />
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-pulse-dot [animation-delay:300ms]" />
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-pulse-dot [animation-delay:600ms]" />
                </div>
              </div>
            </div>
          )}
            </>
          )}
        </div>
      </ScrollArea>

      {/* Input area - always visible per plan (empty state controls) */}
      <div className="border-t border-border bg-card p-4">
        <div className="mx-auto max-w-3xl">
          {/* Mode and Model controls - bottom-left of input */}
          <div className="flex items-center gap-1 mb-2">
            {modes.length > 0 && (
              <ModeSelector
                modes={modes}
                selectedModeId={selectedModeId}
                onSelectMode={onSelectMode}
              />
            )}
            {models.length > 0 && (
              <>
                <span className="text-border text-[10px]">|</span>
                <ChatInputModelSelector
                  models={models}
                  selectedModelId={selectedModelId}
                  onSelectModel={onSelectModel}
                />
              </>
            )}
          </div>
          <div className="relative rounded-lg border border-input bg-background focus-within:ring-2 focus-within:ring-ring/20 transition-all">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message, @ for context, / for commands"
              rows={1}
              disabled={!hasConversation}
              className="w-full resize-none bg-transparent px-4 py-3 pr-12 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-60"
            />
            <Button
              size="icon"
              variant="ghost"
              className={cn(
                "absolute bottom-2 right-2 h-7 w-7 transition-colors",
                input.trim()
                  ? "text-primary hover:text-primary hover:bg-primary/10"
                  : "text-muted-foreground"
              )}
              onClick={handleSubmit}
              disabled={!input.trim() || isStreaming || !hasConversation}
            >
              {isStreaming ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="mt-1.5 text-center text-[10px] text-muted-foreground/60">
            Press Enter to send, Shift + Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false)
  const isAssistant = message.role === "assistant"

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <TooltipProvider>
      <div className={cn("flex items-start gap-3 group", !isAssistant && "flex-row-reverse")}>
        <Avatar className="h-7 w-7">
          <AvatarFallback
            className={cn(
              isAssistant ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
            )}
          >
            {isAssistant ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
          </AvatarFallback>
        </Avatar>

        <div className={cn("flex-1 space-y-2", !isAssistant && "flex flex-col items-end")}>
          {/* Model badge for assistant */}
          {isAssistant && message.model && (
            <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
              {message.model}
            </span>
          )}

          {/* Message content */}
          <div
            className={cn(
              "text-sm leading-relaxed",
              isAssistant
                ? "text-foreground"
                : "inline-block rounded-lg bg-primary/10 px-4 py-2.5 text-foreground max-w-[85%]"
            )}
          >
            {message.content.split("```").map((block, i) => {
              if (i % 2 === 1) {
                const lines = block.split("\n")
                const lang = lines[0]
                const code = lines.slice(1).join("\n")
                return (
                  <div key={i} className="my-3 rounded-lg border border-border overflow-hidden">
                    <div className="flex items-center justify-between px-3 py-1.5 bg-muted border-b border-border">
                      <span className="text-[10px] font-mono font-medium text-muted-foreground">
                        {lang || "code"}
                      </span>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button
                            onClick={handleCopy}
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <Copy className="h-3 w-3" />
                          </button>
                        </TooltipTrigger>
                        <TooltipContent>{copied ? "Copied!" : "Copy code"}</TooltipContent>
                      </Tooltip>
                    </div>
                    <pre className="p-3 text-xs overflow-x-auto bg-muted/50">
                      <code className="font-mono">{code}</code>
                    </pre>
                  </div>
                )
              }
              return (
                <span key={i} className="whitespace-pre-wrap">
                  {block.split("\n").map((line, j) => {
                    if (line.startsWith("**") && line.endsWith("**")) {
                      return (
                        <strong key={j} className="block font-semibold mt-2">
                          {line.replace(/\*\*/g, "")}
                        </strong>
                      )
                    }
                    if (line.startsWith("- ")) {
                      return (
                        <span key={j} className="block pl-3">
                          {"  "}{line}
                        </span>
                      )
                    }
                    return (
                      <span key={j}>
                        {line}
                        {j < block.split("\n").length - 1 && "\n"}
                      </span>
                    )
                  })}
                </span>
              )
            })}
          </div>

          {/* Tool calls */}
          {message.toolCalls && message.toolCalls.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {message.toolCalls.map((tool, i) => (
                <Badge
                  key={i}
                  variant="outline"
                  className={cn(
                    "gap-1 px-2 py-0.5 text-[10px] font-normal",
                    tool.status === "running" && "border-primary/30 text-primary",
                    tool.status === "complete" && "border-success/30 text-success",
                    tool.status === "error" && "border-destructive/30 text-destructive"
                  )}
                >
                  {tool.status === "running" && <Loader2 className="h-2.5 w-2.5 animate-spin" />}
                  {tool.status === "complete" && <CheckCircle2 className="h-2.5 w-2.5" />}
                  {tool.status === "error" && <AlertCircle className="h-2.5 w-2.5" />}
                  <Wrench className="h-2.5 w-2.5" />
                  {tool.name}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>
    </TooltipProvider>
  )
}
