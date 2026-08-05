import type { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

export function FeatureCard({ icon: Icon, title }: { icon: LucideIcon; title: string }) {
  return (
    <motion.div
      whileHover={{ y: -3, scale: 1.02 }}
      className="flex items-center gap-3 rounded-2xl border border-white/[0.08] bg-[rgba(15,23,42,0.65)] px-4 py-3 backdrop-blur-md"
    >
      <span className="grid h-9 w-9 place-items-center rounded-xl border border-primary/30 bg-primary/10 text-cyan">
        <Icon className="h-4 w-4" />
      </span>
      <span className="text-sm font-medium text-slate-100">{title}</span>
    </motion.div>
  );
}
