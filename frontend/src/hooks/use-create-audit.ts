"use client";

import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { AuditCreate, AuditStatus } from "@/types/audit";

export function useCreateAudit() {
  return useMutation({
    mutationFn: (data: AuditCreate) =>
      api.post<AuditStatus>("/audits", data),
  });
}
