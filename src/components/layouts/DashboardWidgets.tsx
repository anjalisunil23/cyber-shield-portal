import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function ChartCard({
  title,
  children,
  action,
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <div className="mb-4 flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
        {action}
      </div>
      {children}
    </motion.div>
  );
}

export function QuickActionCard({
  label,
  description,
  icon: Icon,
  onClick,
}: {
  label: string;
  description?: string;
  icon: LucideIcon;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-xl border border-border bg-card/80 p-3.5 text-left transition hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-[0_0_24px_-10px_rgba(59,130,246,0.55)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <div className="mb-2 grid h-9 w-9 place-items-center rounded-lg bg-primary/10 text-primary">
        <Icon className="h-4 w-4" />
      </div>
      <p className="text-sm font-medium text-foreground">{label}</p>
      {description ? <p className="mt-0.5 text-xs text-muted-foreground">{description}</p> : null}
    </button>
  );
}

export function AiPlaceholderCard({ title, blurb }: { title: string; blurb: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-border bg-card/60 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-cyan">Phase 2 · AI</p>
      <p className="mt-2 text-sm font-medium text-foreground">{title}</p>
      <p className="mt-1 text-xs text-muted-foreground">{blurb}</p>
    </div>
  );
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-[1.75rem]">
          {title}
        </h1>
        {subtitle ? <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

export function Panel({
  title,
  children,
  className = "",
  actions,
}: {
  title?: string;
  children: ReactNode;
  className?: string;
  actions?: ReactNode;
}) {
  return (
    <div className={`glass-card p-4 ${className}`}>
      {title && (
        <div className="mb-3 flex items-center justify-between gap-2">
          <h3 className="text-sm font-medium text-foreground">{title}</h3>
          {actions}
        </div>
      )}
      {children}
    </div>
  );
}

export function SkeletonGrid({ count = 4 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="h-28 animate-pulse rounded-2xl border border-border/50 bg-muted/60"
        />
      ))}
    </div>
  );
}
