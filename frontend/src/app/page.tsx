import { HeroSection } from "@/components/landing/hero-section";
import { AuditForm } from "@/components/landing/audit-form";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-10 px-4 py-20">
      <HeroSection />
      <AuditForm />
    </main>
  );
}
