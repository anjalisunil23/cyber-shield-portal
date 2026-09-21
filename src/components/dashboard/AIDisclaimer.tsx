import { ShieldAlert } from "lucide-react";

export const AI_DISCLAIMER =
  "Cyber Shield is an investigation support and decision-assistance platform. AI-generated findings are recommendations only and must be independently verified by authorized investigators.";

export function AIDisclaimer({ className = "" }: { className?: string }) {
  return (
    <div
      className={`rounded-xl border border-border/80 bg-background/60 p-3 text-[10px] text-muted-foreground flex items-start gap-2 ${className}`}
    >
      <ShieldAlert className="h-4 w-4 text-primary shrink-0 mt-0.5" />
      <span>{AI_DISCLAIMER}</span>
    </div>
  );
}
