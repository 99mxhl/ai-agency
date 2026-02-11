"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { AuditResult } from "@/types/audit";

const TERMINAL_STATUSES = new Set(["completed", "failed"]);

export function useAudit(id: string) {
  return useQuery({
    queryKey: ["audit", id],
    queryFn: () => api.get<AuditResult>(`/audits/${id}`),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status && TERMINAL_STATUSES.has(status)) return false;
      return 2000;
    },
  });
}
