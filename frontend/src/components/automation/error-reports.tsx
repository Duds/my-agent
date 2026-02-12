"use client";

import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { api } from "@/lib/api-client";
import type { ErrorReportEntry } from "@/types/api";
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

const REPORT_LIMIT = 100;

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

export function ErrorReports() {
  const [reports, setReports] = useState<ErrorReportEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .getErrorReports({ limit: REPORT_LIMIT })
      .then((data) => {
        if (!cancelled) setReports(data);
      })
      .catch((e) => {
        if (!cancelled)
          setError(
            e instanceof Error ? e.message : "Failed to load error reports"
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
        <p className="text-sm text-muted-foreground">
          Loading error reports…
        </p>
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

  if (reports.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <AlertTriangle className="h-8 w-8 text-muted-foreground/50 mb-2" />
        <p className="text-sm font-medium text-muted-foreground">
          No error reports
        </p>
        <p className="text-xs text-muted-foreground/70 mt-0.5">
          Error reports will appear here when script or automation runs fail.
        </p>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <p className="text-sm text-muted-foreground">
          Latest {reports.length} error report
          {reports.length !== 1 ? "s" : ""}
        </p>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>Script ID</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Message</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {reports.map((r) => (
              <TableRow key={r.id}>
                <TableCell className="text-muted-foreground text-xs whitespace-nowrap">
                  {formatDateTime(r.timestamp)}
                </TableCell>
                <TableCell className="font-mono text-xs">{r.scriptId}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      r.severity === "error" || r.severity === "critical"
                        ? "destructive"
                        : r.severity === "warning"
                          ? "secondary"
                          : "outline"
                    }
                  >
                    {r.severity ?? "—"}
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground text-xs max-w-[300px]">
                  {r.message}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
