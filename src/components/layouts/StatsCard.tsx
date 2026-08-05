import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { useCountUp } from "@/hooks/useCountUp";
import { cn } from "@/lib/utils";

export function StatsCard({
  label,
  value,
  hint = "Live",
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
  const { ref, value: n } = useCountUp(value, 1100);
  const tones = {
    primary: "border-primary/30 bg-primary/10 text-primary",
    cyan: "border-cyan/30 bg-cyan/10 text-cyan",
    emerald: "border-emerald-400/30 bg-emerald-400/10 text-emerald-400",
    amber: "border-amber-400/30 bg-amber-400/10 text-amber-400",
    rose: "border-rose-400/30 bg-rose-400/10 text-rose-400",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ y: -4, scale: 1.01 }}
      className="rounded-2xl border border-white/10 bg-[#111827]/90 p-5 shadow-[0_0_30px_-18px_rgba(59,130,246,0.45)] backdrop-blur"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-50">
            <span ref={ref}>{n.toLocaleString()}</span>
          </p>
        </div>
        <div className={cn("grid h-10 w-10 place-items-center rounded-xl border", tones[tone])}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className="mt-3 text-xs text-slate-500">{hint}</p>
    </motion.div>
  );
}
