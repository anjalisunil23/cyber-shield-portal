import type { ReactNode } from "react";
import { Fingerprint } from "lucide-react";
import { CyberAtmosphere } from "@/components/cyber/CyberAtmosphere";
import { ShieldCore } from "@/components/cyber/ShieldCore";

/** Shared cyber-HUD visual stage. */
export function HudVisualStage({ compact = false }: { compact?: boolean }) {
  return (
    <div
      className={`relative grid place-items-center ${compact ? "min-h-[320px]" : "min-h-[480px]"} w-full`}
    >
      <ShieldCore compact={compact} />
    </div>
  );
}

/** Page shell with cyber HUD atmosphere. */
export function HudShell({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`login-hud relative min-h-screen overflow-hidden text-white ${className}`}>
      <CyberAtmosphere />
      <div className="relative z-10">{children}</div>
    </div>
  );
}

/** Fingerprint-framed auth card used on login/register. */
export function HudAuthCard({ children }: { children: ReactNode }) {
  return (
    <div className="relative rounded-xl border border-white/20 bg-[#07111f]/70 px-6 pb-8 pt-12 shadow-[0_0_60px_rgba(30,80,180,0.28)] backdrop-blur-md sm:px-8">
      <div className="absolute left-1/2 top-0 flex h-16 w-16 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-cyan/40 bg-[#0a1528] shadow-[0_0_24px_rgba(6,182,212,0.35)]">
        <Fingerprint className="h-8 w-8 text-white" strokeWidth={1.4} />
      </div>
      {children}
    </div>
  );
}

export const hudField =
  "flex w-full items-center gap-3 rounded-md bg-[#2a3340] px-3 py-3 text-sm text-white outline-none placeholder:text-white/45";

export const hudInput =
  "w-full bg-transparent text-sm text-white outline-none placeholder:text-white/45";
