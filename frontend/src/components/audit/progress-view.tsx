"use client";

import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PIPELINE_STEPS } from "@/types/audit";
import { Check, Loader2, Circle } from "lucide-react";

interface ProgressViewProps {
  progress: number;
  currentStep: string | null;
  handle?: string;
}

export function ProgressView({ progress, currentStep, handle }: ProgressViewProps) {
  return (
    <div className="mx-auto w-full max-w-lg space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">
          Auditing {handle ? `@${handle}` : "brand"}...
        </h1>
        <p className="text-muted-foreground">
          This usually takes 1-3 minutes. Feel free to bookmark this page.
        </p>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center justify-between">
            <span>Progress</span>
            <span className="text-sm font-normal text-muted-foreground">
              {progress}%
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Progress value={progress} className="h-2" />

          <ol className="space-y-3">
            {PIPELINE_STEPS.map((step) => {
              const isComplete = progress > step.progress;
              const isCurrent = currentStep === step.status;

              return (
                <li key={step.status} className="flex items-center gap-3 text-sm">
                  {isComplete ? (
                    <Check className="h-4 w-4 text-emerald-500 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="h-4 w-4 animate-spin text-primary shrink-0" />
                  ) : (
                    <Circle className="h-4 w-4 text-muted-foreground/40 shrink-0" />
                  )}
                  <span
                    className={
                      isComplete
                        ? "text-muted-foreground"
                        : isCurrent
                          ? "font-medium"
                          : "text-muted-foreground/60"
                    }
                  >
                    {step.label}
                  </span>
                </li>
              );
            })}
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
