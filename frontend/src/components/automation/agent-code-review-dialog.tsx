"use client";

import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { AgentGeneratedMeta } from "@/types/api";

export interface AgentCodeReviewDialogProps {
  open: boolean;
  onClose: () => void;
  code: string;
  agentName: string;
  onApprove: (editedCode: string) => Promise<void>;
  onReject: () => void;
}

export function AgentCodeReviewDialog({
  open,
  onClose,
  code,
  agentName,
  onApprove,
  onReject,
}: AgentCodeReviewDialogProps) {
  const [editedCode, setEditedCode] = useState(code);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (open) setEditedCode(code);
  }, [open, code]);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      await onApprove(editedCode);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Review agent: {agentName}</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Edit the code below if needed, then approve to register the agent. It
          will appear in the Automation Hub.
        </p>
        <ScrollArea className="flex-1 min-h-[200px] rounded-lg border border-input bg-muted/30 p-3">
          <textarea
            value={editedCode}
            onChange={(e) => setEditedCode(e.target.value)}
            className="w-full min-h-[280px] font-mono text-xs text-foreground bg-transparent resize-none focus:outline-none"
            spellCheck={false}
            aria-label="Agent code"
            placeholder="Python agent code..."
          />
        </ScrollArea>
        <DialogFooter>
          <Button variant="outline" onClick={onReject} disabled={isSubmitting}>
            Reject
          </Button>
          <Button onClick={handleApprove} disabled={isSubmitting}>
            {isSubmitting ? "Registering…" : "Approve & register"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
