"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { useCreateAudit } from "@/hooks/use-create-audit";
import { Loader2, Search } from "lucide-react";

const HANDLE_REGEX = /^[a-zA-Z0-9._]+$/;

export function AuditForm() {
  const router = useRouter();
  const [handle, setHandle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createAudit = useCreateAudit();

  const sanitized = handle.replace(/^@/, "").trim();
  const isValid = sanitized.length > 0 && HANDLE_REGEX.test(sanitized);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!isValid) {
      setError("Enter a valid Instagram handle (letters, numbers, dots, underscores)");
      return;
    }

    try {
      const result = await createAudit.mutateAsync({
        instagram_handle: sanitized,
      });
      router.push(`/audit/${result.id}`);
    } catch {
      setError("Something went wrong. Please try again.");
    }
  }

  return (
    <Card className="mx-auto w-full max-w-md">
      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              @
            </span>
            <Input
              type="text"
              placeholder="instagram_handle"
              value={handle}
              onChange={(e) => {
                setHandle(e.target.value);
                setError(null);
              }}
              className="pl-8"
              disabled={createAudit.isPending}
            />
          </div>
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
          <Button type="submit" disabled={!isValid || createAudit.isPending} className="w-full">
            {createAudit.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting audit...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Run Free Audit
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
