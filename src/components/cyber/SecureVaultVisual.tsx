import { Lock, Shield } from "lucide-react";
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion";

export function SecureVaultVisual() {
  const reduced = usePrefersReducedMotion();
  return (
    <div className="relative mx-auto mb-4 grid h-28 w-28 place-items-center">
      <div className="absolute inset-0 rounded-2xl border border-primary/30 bg-primary/10" />
      <div
        className={`absolute inset-2 rounded-xl border border-cyan/20 bg-card/80 ${reduced ? "" : "animate-float-slow"}`}
      />
      <Shield className="relative h-10 w-10 text-primary" strokeWidth={1.4} />
      <Lock className="absolute bottom-3 right-3 h-4 w-4 text-cyan" />
    </div>
  );
}
