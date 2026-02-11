"use client";

import { use } from "react";
import { useAudit } from "@/hooks/use-audit";
import { ProgressView } from "@/components/audit/progress-view";
import { ErrorView } from "@/components/audit/error-view";
import { ReportLayout } from "@/components/audit/report/report-layout";
import { Skeleton } from "@/components/ui/skeleton";

export default function AuditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: audit, isLoading, error } = useAudit(id);

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4">
        <div className="w-full max-w-lg space-y-4">
          <Skeleton className="h-8 w-48 mx-auto" />
          <Skeleton className="h-4 w-64 mx-auto" />
          <Skeleton className="h-40 w-full" />
        </div>
      </main>
    );
  }

  if (error || !audit) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4">
        <ErrorView message="Audit not found or could not be loaded." />
      </main>
    );
  }

  if (audit.status === "failed") {
    return (
      <main className="flex min-h-screen items-center justify-center p-4">
        <ErrorView handle={audit.brand?.handle} />
      </main>
    );
  }

  if (audit.status === "completed") {
    return <ReportLayout audit={audit} />;
  }

  // In-progress states
  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <ProgressView
        progress={audit.progress}
        currentStep={audit.current_step}
        handle={audit.brand?.handle}
      />
    </main>
  );
}
