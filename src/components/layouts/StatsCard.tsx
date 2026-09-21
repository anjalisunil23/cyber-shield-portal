import type { LucideIcon } from "lucide-react";
import { useCountUp } from "@/hooks/useCountUp";
import { cn } from "@/lib/utils";

export function StatsCard({
  label,
  value,
  hint,
  icon: Icon,
  delay = 0,
  tone = "primary",
}: {
  label: string;
  value: number;
  hint?: string;
  icon: LucideIcon;
  delay?: number;
  tone?: "primary" | "cyan" | "emerald" | "amber" | "rose";
}) {
  const { ref, value: n } = useCountUp(value, 700);
  const tones = {
    primary: "bg-primary/10 text-primary",
    cyan: "bg-cyan/10 text-cyan",
    emerald: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    amber: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    rose: "bg-rose-500/10 text-rose-600 dark:text-rose-400",
  };

  return (
    <div className="glass-card glow-hover p-4" style={{ animationDelay: `${delay}s` }}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            <span ref={ref}>{n.toLocaleString()}</span>
          </p>
          {hint ? <p className="mt-1 text-[11px] text-muted-foreground">{hint}</p> : null}
        </div>
        <div className={cn("grid h-9 w-9 shrink-0 place-items-center rounded-lg", tones[tone])}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
}
