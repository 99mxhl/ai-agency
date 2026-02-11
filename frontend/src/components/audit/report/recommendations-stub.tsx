import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Sparkles } from "lucide-react";

export function RecommendationsStub() {
  return (
    <Alert>
      <Sparkles className="h-4 w-4" />
      <AlertTitle>AI-Powered Recommendations</AlertTitle>
      <AlertDescription>
        Personalized influencer marketing recommendations based on your brand
        audit are coming soon. We&apos;re training our models to deliver
        actionable insights tailored to your brand.
      </AlertDescription>
    </Alert>
  );
}
