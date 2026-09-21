import { BrainCircuit, FileStack, MessageSquare, Users } from "lucide-react";
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion";

type Counts = {
  evidence?: number;
  team?: number;
  activity?: number;
  intelligence?: boolean;
};

/** Case overview node map: case → evidence / team / activity / AI. */
export function CaseOrbit({
  caseNumber,
  counts,
  onSelect,
}: {
  caseNumber: string;
  counts?: Counts;
  onSelect?: (key: "evidence" | "team" | "activity" | "intelligence") => void;
}) {
  const reduced = usePrefersReducedMotion();
  const nodes = [
    {
      key: "evidence" as const,
      label: "Evidence",
      hint: counts?.evidence != null ? `${counts.evidence}` : "—",
      Icon: FileStack,
      pos: "left-[4%] top-[38%] sm:left-[8%]",
    },
    {
      key: "team" as const,
      label: "Team",
      hint: counts?.team != null ? `${counts.team}` : "—",
      Icon: Users,
      pos: "right-[4%] top-[18%] sm:right-[10%]",
    },
    {
      key: "activity" as const,
      label: "Activity",
      hint: counts?.activity != null ? `${counts.activity}` : "—",
      Icon: MessageSquare,
      pos: "left-[10%] bottom-[8%] sm:left-[18%]",
    },
    {
      key: "intelligence" as const,
      label: "Intelligence",
      hint: counts?.intelligence ? "Ready" : "—",
      Icon: BrainCircuit,
      pos: "right-[8%] bottom-[10%] sm:right-[16%]",
    },
  ];

  return (
    <div className="glass-card relative h-[280px] overflow-hidden sm:h-[320px]">
      <div className="cyber-grid absolute inset-0 opacity-40" />
      <svg className="absolute inset-0 h-full w-full" viewBox="0 0 400 300" aria-hidden>
        <g stroke="rgb(59 130 246 / 0.35)" strokeWidth="1" fill="none">
          <line x1="200" y1="150" x2="70" y2="150" />
          <line x1="200" y1="150" x2="330" y2="80" />
          <line x1="200" y1="150" x2="90" y2="250" />
          <line x1="200" y1="150" x2="320" y2="240" />
        </g>
      </svg>
      <div className="absolute left-1/2 top-1/2 z-[1] -translate-x-1/2 -translate-y-1/2">
        <div className={reduced ? "" : "animate-float-slow"}>
          <div className="grid h-20 w-20 place-items-center rounded-2xl border border-primary/40 bg-primary/15 shadow-[0_0_30px_-8px_rgba(59,130,246,0.7)]">
            <p className="px-1 text-center text-[10px] font-semibold leading-tight text-primary">
              {caseNumber}
            </p>
          </div>
        </div>
      </div>
      {nodes.map((n) => (
        <button
          key={n.key}
          type="button"
          onClick={() => onSelect?.(n.key)}
          className={`absolute z-[1] flex items-center gap-2 rounded-xl border border-border/80 bg-card/90 px-2.5 py-1.5 text-left shadow-sm backdrop-blur-sm transition hover:border-primary/50 hover:shadow-[0_0_20px_-8px_rgba(59,130,246,0.6)] ${n.pos}`}
        >
          <n.Icon className="h-3.5 w-3.5 text-cyan" />
          <span>
            <span className="block text-[11px] font-medium text-foreground">{n.label}</span>
            <span className="block text-[10px] text-muted-foreground">{n.hint}</span>
          </span>
        </button>
      ))}
    </div>
  );
}
