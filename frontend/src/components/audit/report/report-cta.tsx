"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { FileDown, Mail } from "lucide-react";

export function ReportCta() {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex flex-col items-center gap-4 text-center">
          <h3 className="text-lg font-semibold">
            Ready to optimize your influencer marketing?
          </h3>
          <p className="text-sm text-muted-foreground max-w-md">
            Get expert help building and executing your influencer strategy
            across Central &amp; Eastern Europe.
          </p>
          <div className="flex gap-3">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" disabled>
                  <FileDown className="mr-2 h-4 w-4" />
                  Download PDF
                </Button>
              </TooltipTrigger>
              <TooltipContent>Coming soon</TooltipContent>
            </Tooltip>
            <Button asChild>
              <a href="mailto:hello@example.com">
                <Mail className="mr-2 h-4 w-4" />
                Get in Touch
              </a>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
