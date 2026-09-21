import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, FileQuestion, Inbox, Loader2, Search } from "lucide-react";
import { Link, useRouterState } from "@tanstack/react-router";
import { useEffect, useMemo, useState, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";
import { PageHeader, Panel } from "@/components/layouts/DashboardWidgets";

export function HistoryNav({ className }: { className?: string }) {
  const locationKey = useRouterState({ select: (s) => s.location.href });
  const [canBack, setCanBack] = useState(false);
  const [canForward, setCanForward] = useState(false);

  useEffect(() => {
    const onPop = () => sessionStorage.setItem("cs_hist_pop", "1");
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  useEffect(() => {
    const idx = Number(window.history.state?.idx ?? 0);
    const popped = sessionStorage.getItem("cs_hist_pop") === "1";
    sessionStorage.setItem("cs_hist_pop", "0");
    let max = Number(sessionStorage.getItem("cs_hist_max") || "0");
    max = popped ? Math.max(max, idx) : idx;
    sessionStorage.setItem("cs_hist_max", String(max));
    setCanBack(idx > 0);
    setCanForward(idx < max);
  }, [locationKey]);

  return (
    <div className={cn("flex items-center", className)}>
      <button
        type="button"
        aria-label="Back"
        title="Back"
        disabled={!canBack}
        onClick={() => window.history.back()}
        className="grid h-9 w-9 place-items-center rounded-l-lg border border-border bg-card text-muted-foreground transition hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>
      <button
        type="button"
        aria-label="Forward"
        title="Forward"
        disabled={!canForward}
        onClick={() => window.history.forward()}
        className="-ml-px grid h-9 w-9 place-items-center rounded-r-lg border border-border bg-card text-muted-foreground transition hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  );
}

export function Breadcrumb({ items }: { items: { label: string; to?: string }[] }) {
  if (!items.length) return null;
  const parent = items.length > 1 ? items[items.length - 2] : null;
  const current = items[items.length - 1];
  return (
    <>
      <nav
        aria-label="Breadcrumb"
        className="mb-3 hidden flex-wrap items-center gap-1 text-xs text-muted-foreground sm:flex"
      >
        {items.map((item, i) => {
          const last = i === items.length - 1;
          return (
            <span key={`${item.label}-${i}`} className="inline-flex items-center gap-1">
              {i > 0 && <ChevronRight className="h-3 w-3 shrink-0 opacity-60" />}
              {item.to && !last ? (
                <Link to={item.to as "/"} className="max-w-[140px] truncate hover:text-foreground">
                  {item.label}
                </Link>
              ) : (
                <span className="max-w-[180px] truncate font-medium text-foreground">
                  {item.label}
                </span>
              )}
            </span>
          );
        })}
      </nav>
      <nav
        aria-label="Breadcrumb"
        className="mb-3 flex items-center gap-1 text-xs text-muted-foreground sm:hidden"
      >
        {parent?.to ? (
          <Link
            to={parent.to as "/"}
            className="inline-flex items-center gap-0.5 hover:text-foreground"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            {parent.label}
          </Link>
        ) : null}
        <span className="truncate font-medium text-foreground">
          {parent ? `/ ${current.label}` : current.label}
        </span>
      </nav>
    </>
  );
}

export function EmptyState({
  title = "Nothing here yet",
  description,
  action,
  visual,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
  visual?: ReactNode;
}) {
  return (
    <div className="glass-card flex flex-col items-center justify-center px-5 py-12 text-center">
      {visual ?? <Inbox className="mb-2 h-8 w-8 text-muted-foreground" />}
      <p className="text-sm font-medium text-foreground">{title}</p>
      {description ? (
        <p className="mt-1 max-w-sm text-xs text-muted-foreground">{description}</p>
      ) : null}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({
  message = "Something went wrong. Please try again.",
}: {
  message?: string;
}) {
  return (
    <div className="rounded-xl border border-destructive/20 bg-destructive/5 px-4 py-6 text-center text-sm text-destructive">
      <FileQuestion className="mx-auto mb-2 h-5 w-5" />
      {message}
    </div>
  );
}

export function LoadingBlock({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2" aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-11 animate-pulse rounded-lg bg-muted" />
      ))}
    </div>
  );
}

export function Toolbar({
  search,
  onSearch,
  placeholder = "Search…",
  filters,
  actions,
}: {
  search: string;
  onSearch: (v: string) => void;
  placeholder?: string;
  filters?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-4 flex flex-wrap items-center gap-2">
      <div className="relative min-w-[200px] flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-xl border border-border bg-card py-2.5 pl-10 pr-3 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:border-primary/60 focus:ring-2 focus:ring-primary/10 transition-all"
        />
      </div>
      {filters}
      {actions}
    </div>
  );
}

export function SelectFilter({
  value,
  onChange,
  options,
  label,
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
  label?: string;
}) {
  return (
    <select
      aria-label={label}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-xl border border-border bg-card px-3 py-2.5 text-xs text-foreground focus:border-primary/60 outline-none"
    >
      {options.map((o) => (
        <option key={o} value={o}>
          {o}
        </option>
      ))}
    </select>
  );
}

export function PrimaryButton({
  children,
  onClick,
  type = "button",
  className,
  disabled,
  loading,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  className?: string;
  disabled?: boolean;
  loading?: boolean;
} & Pick<ButtonHTMLAttributes<HTMLButtonElement>, "disabled">) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        "inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg bg-primary px-3.5 py-2 text-sm font-medium text-primary-foreground shadow-xs transition hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
        className,
      )}
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
      {children}
    </button>
  );
}

export function GhostButton({
  children,
  onClick,
  type = "button",
  className,
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  className?: string;
  disabled?: boolean;
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "inline-flex min-h-9 items-center justify-center rounded-lg border border-border bg-card px-3.5 py-2 text-sm text-foreground transition hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function Modal({
  open,
  title,
  children,
  onClose,
}: {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 backdrop-blur-xs p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="w-full max-w-lg rounded-2xl border border-border bg-card p-6 shadow-2xl text-foreground"
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
          <button
            type="button"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            ✕
          </button>
        </div>
        {children}
      </motion.div>
    </div>
  );
}

export function ConfirmDialog({
  open,
  title,
  message,
  onConfirm,
  onClose,
}: {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onClose: () => void;
}) {
  return (
    <Modal open={open} title={title} onClose={onClose}>
      <p className="text-sm text-muted-foreground">{message}</p>
      <div className="mt-5 flex justify-end gap-2">
        <GhostButton onClick={onClose}>Cancel</GhostButton>
        <PrimaryButton onClick={onConfirm}>Confirm</PrimaryButton>
      </div>
    </Modal>
  );
}

export type Column<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  className?: string;
};

export function DataTable<T extends { id: string }>({
  columns,
  rows,
  emptyTitle,
}: {
  columns: Column<T>[];
  rows: T[];
  emptyTitle?: string;
}) {
  if (!rows.length) return <EmptyState title={emptyTitle || "No records"} />;
  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-card">
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead className="sticky top-0 z-[1] border-b border-border bg-muted/70 text-[11px] font-medium uppercase tracking-wide text-muted-foreground backdrop-blur-sm">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                className={cn("whitespace-nowrap px-3 py-2.5 font-medium", c.className)}
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} className="border-b border-border/60 last:border-0 hover:bg-muted/40">
              {columns.map((c) => (
                <td key={c.key} className={cn("px-3 py-2.5 text-foreground", c.className)}>
                  {c.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Pagination({
  page,
  pages,
  onPage,
}: {
  page: number;
  pages: number;
  onPage: (p: number) => void;
}) {
  return (
    <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
      <span>
        Page {page} of {pages}
      </span>
      <div className="flex gap-2">
        <GhostButton
          className="px-3 py-1.5 text-xs"
          disabled={page <= 1}
          onClick={() => onPage(Math.max(1, page - 1))}
        >
          Previous
        </GhostButton>
        <GhostButton
          className="px-3 py-1.5 text-xs"
          disabled={page >= pages}
          onClick={() => onPage(Math.min(pages, page + 1))}
        >
          Next
        </GhostButton>
      </div>
    </div>
  );
}

export function useClientTable<T>(items: T[], pageSize = 8) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return items;
    return items.filter((item) => JSON.stringify(item).toLowerCase().includes(q));
  }, [items, search]);
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const safePage = Math.min(page, pages);
  const rows = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);
  return { search, setSearch, page: safePage, setPage, pages, rows, total: filtered.length };
}

export function StatusPill({ value }: { value: string }) {
  const v = value.toLowerCase();
  const tone =
    v.includes("active") || v.includes("done") || v.includes("completed")
      ? "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/15 dark:text-emerald-400"
      : v.includes("critical") || v.includes("suspend") || v.includes("high")
        ? "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/15 dark:text-rose-400"
        : v.includes("progress") || v.includes("review") || v.includes("pending")
          ? "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/15 dark:text-amber-300"
          : "border-slate-200 bg-slate-100 text-slate-700 dark:border-white/10 dark:bg-white/5 dark:text-slate-300";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium",
        tone,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" aria-hidden />
      {value.replaceAll("_", " ")}
    </span>
  );
}

export function PageScaffold({
  crumbs,
  title,
  subtitle,
  actions,
  children,
}: {
  crumbs: { label: string; to?: string }[];
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div>
      <Breadcrumb items={crumbs} />
      <PageHeader title={title} subtitle={subtitle} actions={actions} />
      {children}
    </div>
  );
}

export { PageHeader, Panel };
export { ChartCard } from "@/components/layouts/DashboardWidgets";
