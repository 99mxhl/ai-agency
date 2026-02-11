"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AlertCircle, RotateCcw, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useCreateAudit } from "@/hooks/use-create-audit";
import { useRouter } from "next/navigation";

interface ErrorViewProps {
  handle?: string;
  message?: string;
}

export function ErrorView({ handle, message }: ErrorViewProps) {
  const router = useRouter();
  const createAudit = useCreateAudit();

  async function handleRetry() {
    if (!handle) return;
    const result = await createAudit.mutateAsync({
      instagram_handle: handle,
    });
    router.push(`/audit/${result.id}`);
  }

  return (
    <div className="mx-auto w-full max-w-lg space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Audit Failed</h1>
      </div>

      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Something went wrong</AlertTitle>
        <AlertDescription>
          {message || "The audit could not be completed. This might be a temporary issue."}
        </AlertDescription>
      </Alert>

      <div className="flex gap-3 justify-center">
        {handle && (
          <Button
            onClick={handleRetry}
            disabled={createAudit.isPending}
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Retry Audit
          </Button>
        )}
        <Button variant="outline" asChild>
          <Link href="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
        </Button>
      </div>
    </div>
  );
}
