'use client';

import React, { useState } from 'react';
import { toast } from 'sonner';
import { ApprovalCard, ApprovalItem } from '@/components/approval/ApprovalCard';
import { Button } from '@/components/ui/button';

const INITIAL_ITEMS: ApprovalItem[] = [
  {
    id: '1',
    title: 'Move DSC_0124.jpg',
    subtitle: 'Downloads -> Photography/2026',
    description: 'Image of a sunset with mountain range.',
    reasoning:
      'AI detected high-quality landscape imagery and metadata matching Photography collection.',
    type: 'file',
    metadata: {
      Size: '2.4 MB',
      Date: '2026-02-05',
      Resolution: '4000x3000',
    },
  },
  {
    id: '2',
    title: 'Run "Cleanup Temp" Script',
    subtitle: 'Automation Engine',
    description: 'Deletes files older than 30 days in .tmp/',
    reasoning:
      'Routine maintenance script triggered by low disk space (under 5GB).',
    type: 'automation',
    metadata: {
      EstimatedGain: '1.2 GB',
      Frequency: 'Monthly',
    },
  },
  {
    id: '3',
    title: 'Suspicious Execution Prevented',
    subtitle: 'Security Sentinel',
    description: 'node_modules/unknown-lib/post-install.sh',
    reasoning:
      'Script attempted to access ~/.ssh/config. Execution blocked by default.',
    type: 'security',
    metadata: {
      Severity: 'CRITICAL',
      Source: 'npm-install',
    },
  },
];

export default function DesignSystemPage() {
  const [items, setItems] = useState<ApprovalItem[]>(INITIAL_ITEMS);
  const [undoStack, setUndoStack] = useState<
    { item: ApprovalItem; action: 'approve' | 'reject' }[]
  >([]);

  const handleApprove = (id: string) => {
    const item = items.find((i) => i.id === id);
    if (!item) return;

    setItems((prev) => prev.filter((i) => i.id !== id));
    setUndoStack((prev) => [...prev, { item, action: 'approve' }]);

    toast.success(`Approved: ${item.title}`, {
      action: {
        label: 'Undo',
        onClick: () => handleUndo(),
      },
    });
  };

  const handleReject = (id: string) => {
    const item = items.find((i) => i.id === id);
    if (!item) return;

    setItems((prev) => prev.filter((i) => i.id !== id));
    setUndoStack((prev) => [...prev, { item, action: 'reject' }]);

    toast.error(`Rejected: ${item.title}`, {
      action: {
        label: 'Undo',
        onClick: () => handleUndo(),
      },
    });
  };

  const handleUndo = () => {
    const last = undoStack.pop();
    if (!last) return;

    setItems((prev) => [last.item, ...prev]);
    setUndoStack([...undoStack]);
    toast.info(`Restored: ${last.item.title}`);
  };

  const reset = () => {
    setItems(INITIAL_ITEMS);
    setUndoStack([]);
  };

  return (
    <div className="bg-background min-h-screen p-8 font-sans">
      <div className="mx-auto max-w-4xl space-y-12">
        <header className="space-y-4">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
            Design System
          </h1>
          <p className="text-muted-foreground text-xl">
            Verifying Phase 3 components and interaction patterns.
          </p>
        </header>

        <section className="space-y-6">
          <div className="flex items-end justify-between">
            <div>
              <h2 className="text-2xl font-bold">Approval UX</h2>
              <p className="text-muted-foreground text-sm">
                Unified "Tinder-style" approval pattern.
              </p>
            </div>
            <Button variant="outline" onClick={reset}>
              Reset Queue
            </Button>
          </div>

          <div className="border-primary/10 bg-primary/5 relative flex h-[500px] items-center justify-center rounded-3xl border-2 border-dashed p-8">
            {items.length > 0 ? (
              <div className="relative flex h-full w-full items-center justify-center">
                {items.map((item, index) => (
                  <ApprovalCard
                    key={item.id}
                    item={item}
                    onApprove={handleApprove}
                    onReject={handleReject}
                    className={cn(
                      'transition-all duration-300',
                      index < items.length - 1
                        ? 'pointer-events-none scale-95 opacity-50 blur-[2px]'
                        : 'z-10'
                    )}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-4 text-center">
                <div className="bg-success/20 text-success inline-block rounded-full p-4">
                  <span className="text-4xl">✨</span>
                </div>
                <h3 className="text-xl font-semibold">Queue Clear!</h3>
                <p className="text-muted-foreground text-sm">
                  All items have been reviewed.
                </p>
                <Button onClick={reset}>Refill Mock Items</Button>
              </div>
            )}
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-bold">Guidelines</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="bg-card rounded-xl border p-4">
              <h3 className="mb-2 font-semibold">Keyboard Shortcuts</h3>
              <ul className="text-muted-foreground space-y-1 text-sm">
                <li>
                  <kbd className="bg-muted rounded border px-1.5 py-0.5">A</kbd>{' '}
                  Approve
                </li>
                <li>
                  <kbd className="bg-muted rounded border px-1.5 py-0.5">R</kbd>{' '}
                  Reject
                </li>
                <li>
                  <kbd className="bg-muted rounded border px-1.5 py-0.5">
                    Cmd+Z
                  </kbd>{' '}
                  Undo
                </li>
              </ul>
            </div>
            <div className="bg-card rounded-xl border p-4">
              <h3 className="mb-2 font-semibold">Visual State</h3>
              <ul className="text-muted-foreground space-y-1 text-sm">
                <li>
                  <span className="text-success">Green</span>: High confidence
                  recommendation
                </li>
                <li>
                  <span className="text-warning">Amber</span>: Requires careful
                  review
                </li>
                <li>
                  <span className="text-destructive">Red</span>:
                  Dangerous/Security action
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(' ');
}
