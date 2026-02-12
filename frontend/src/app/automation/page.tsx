"use client";

import Link from "next/link";
import { ArrowLeft, FileCode, ListChecks, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScriptsList } from "@/components/automation/scripts-list";
import { StatusLogs } from "@/components/automation/status-logs";
import { ErrorReports } from "@/components/automation/error-reports";

export default function AutomationHubPage() {
  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="flex shrink-0 items-center gap-2 border-b border-border px-4 py-3">
        <Button variant="ghost" size="icon" asChild aria-label="Back to dashboard">
          <Link href="/">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <h1 className="text-lg font-semibold">Automation Hub</h1>
      </header>
      <main className="flex-1 overflow-hidden p-4">
        <Tabs defaultValue="scripts" className="flex h-full flex-col">
          <TabsList className="mb-4 shrink-0">
            <TabsTrigger value="scripts" className="gap-2">
              <FileCode className="h-4 w-4" />
              Scripts
            </TabsTrigger>
            <TabsTrigger value="logs" className="gap-2">
              <ListChecks className="h-4 w-4" />
              Status logs
            </TabsTrigger>
            <TabsTrigger value="errors" className="gap-2">
              <AlertTriangle className="h-4 w-4" />
              Error reports
            </TabsTrigger>
          </TabsList>
          <TabsContent value="scripts" className="mt-0 flex-1 overflow-auto data-[state=inactive]:hidden">
            <ScriptsList />
          </TabsContent>
          <TabsContent value="logs" className="mt-0 flex-1 overflow-auto data-[state=inactive]:hidden">
            <StatusLogs />
          </TabsContent>
          <TabsContent value="errors" className="mt-0 flex-1 overflow-auto data-[state=inactive]:hidden">
            <ErrorReports />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
