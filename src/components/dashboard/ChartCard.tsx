import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function ChartCard({
  title,
  children,
  className,
  action,
}: {
  title: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn(
        "rounded-2xl border border-white/10 bg-[#111827]/90 p-5 backdrop-blur shadow-[0_0_40px_-20px_rgba(6,182,212,0.35)]",
        className,
      )}
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
        {action}
      </div>
      {children}
    </motion.div>
  );
}
