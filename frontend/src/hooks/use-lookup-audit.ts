"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { AuditResult } from "@/types/audit";

export function useLookupAudit(handle: string | null) {
  return useQuery({
    queryKey: ["audit-lookup", handle],
    queryFn: () => api.get<AuditResult>(`/audits/lookup?handle=${handle}`),
    enabled: !!handle,
  });
}
