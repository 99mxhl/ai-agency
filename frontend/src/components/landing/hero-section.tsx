import { Badge } from "@/components/ui/badge";

export function HeroSection() {
  return (
    <div className="text-center space-y-6">
      <Badge variant="secondary" className="text-sm">
        Free AI-Powered Audit
      </Badge>
      <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
        Know your brand&apos;s
        <br />
        <span className="text-primary">influencer landscape</span>
      </h1>
      <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
        Get a comprehensive audit of your Instagram influencer marketing in
        minutes. Engagement scores, fraud detection, audience overlap — all
        powered by AI.
      </p>
      <div className="flex items-center justify-center gap-8 text-sm text-muted-foreground">
        <span>Fraud detection</span>
        <span className="h-1 w-1 rounded-full bg-muted-foreground" />
        <span>Audience overlap</span>
        <span className="h-1 w-1 rounded-full bg-muted-foreground" />
        <span>Engagement analysis</span>
      </div>
    </div>
  );
}
