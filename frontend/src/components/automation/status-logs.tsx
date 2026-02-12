"use client";

import { useEffect, useState } from "react";
import { ListChecks } from "lucide-react";
import { api } from "@/lib/api-client";
import type { ExecutionLogEntry } from "@/types/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const LOG_LIMIT = 100;

function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      dateStyle: "short",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

function formatDuration(ms: number | null | undefined): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

export function StatusLogs() {
  const [logs, setLogs] = useState<ExecutionLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .getAutomationLogs({ limit: LOG_LIMIT })
      .then((data) => {
        if (!cancelled) setLogs(data);
      })
      .catch((e) => {
        if (!cancelled)
          setError(
            e instanceof Error ? e.message : "Failed to load execution logs"
          );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <p className="text-sm text-muted-foreground">Loading status logs…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <p className="text-sm font-medium text-destructive">{error}</p>
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <ListChecks className="h-8 w-8 text-muted-foreground/50 mb-2" />
        <p className="text-sm font-medium text-muted-foreground">
          No execution logs
        </p>
        <p className="text-xs text-muted-foreground/70 mt-0.5">
          Logs will appear here when scripts or automations run.
        </p>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <p className="text-sm text-muted-foreground">
          Latest {logs.length} execution log{logs.length !== 1 ? "s" : ""}
        </p>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>Script ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Message</TableHead>
              <TableHead>Duration</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell className="text-muted-foreground text-xs whitespace-nowrap">
                  {formatDateTime(log.timestamp)}
                </TableCell>
                <TableCell className="font-mono text-xs">{log.scriptId}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      log.status === "success"
                        ? "default"
                        : log.status === "error"
                          ? "destructive"
                          : "secondary"
                    }
                  >
                    {log.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground text-xs max-w-[200px] truncate">
                  {log.message ?? "—"}
                </TableCell>
                <TableCell className="text-muted-foreground text-xs tabular-nums">
                  {formatDuration(log.durationMs ?? undefined)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
