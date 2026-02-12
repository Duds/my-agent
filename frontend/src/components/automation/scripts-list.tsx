"use client";

import { useEffect, useState } from "react";
import { FileCode } from "lucide-react";
import { api } from "@/lib/api-client";
import type { ScriptInfo } from "@/types/api";
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

function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
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

export function ScriptsList() {
  const [scripts, setScripts] = useState<ScriptInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .getScripts()
      .then((data) => {
        if (!cancelled) setScripts(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load scripts");
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
        <p className="text-sm text-muted-foreground">Loading scripts…</p>
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

  if (scripts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <FileCode className="h-8 w-8 text-muted-foreground/50 mb-2" />
        <p className="text-sm font-medium text-muted-foreground">No scripts</p>
        <p className="text-xs text-muted-foreground/70 mt-0.5">
          Scripts will appear here when configured (e.g. from cron or agent runs).
        </p>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <p className="text-sm text-muted-foreground">
          {scripts.length} script{scripts.length !== 1 ? "s" : ""}
        </p>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Last run</TableHead>
              <TableHead className="text-muted-foreground">Source</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {scripts.map((s) => (
              <TableRow key={s.id}>
                <TableCell className="font-medium">{s.name}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="font-normal">
                    {s.type}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge
                    variant={
                      s.status === "active"
                        ? "default"
                        : s.status === "error"
                          ? "destructive"
                          : "secondary"
                    }
                  >
                    {s.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground text-xs">
                  {formatDateTime(s.lastRun ?? undefined)}
                </TableCell>
                <TableCell className="text-muted-foreground text-xs">
                  {s.source ?? "—"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
