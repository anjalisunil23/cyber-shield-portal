import { Shield } from "lucide-react";
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion";
import { cn } from "@/lib/utils";

/** CSS 3D shield / core — no WebGL. */
export function ShieldCore({
  className,
  compact = false,
}: {
  className?: string;
  compact?: boolean;
}) {
  const reduced = usePrefersReducedMotion();

  return (
    <div
      className={cn(
        "relative mx-auto aspect-square w-full",
        compact ? "max-w-[280px]" : "max-w-[460px]",
        className,
      )}
    >
      <div className="absolute inset-[12%] rounded-full bg-primary/20 blur-3xl" />
      <div className={cn("cyber-scene absolute inset-0", reduced && "cyber-scene-static")}>
        <div className="cyber-ring cyber-ring-a" />
        <div className="cyber-ring cyber-ring-b" />
        <div className="cyber-ring cyber-ring-c" />
        <div className="cyber-core">
          <Shield
            className={cn(
              "text-white drop-shadow-[0_0_18px_rgba(59,130,246,0.85)]",
              compact ? "h-16 w-16" : "h-24 w-24",
            )}
            strokeWidth={1.15}
          />
        </div>
        {["Evidence", "Team", "Intel", "Comms"].map((label, i) => (
          <span key={label} className={`cyber-label cyber-label-${i}`}>
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}
