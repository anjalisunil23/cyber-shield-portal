import { Bell, Menu, Search, User } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { ROLE_LABEL, type AppRole } from "@/lib/roles";
import { investigationApi } from "@/services/investigationApi";
import type { SearchResult } from "@/services/types";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { HistoryNav } from "@/components/ui-kit/PageKit";

export function RoleTopNavbar({ onMenu, role }: { onMenu: () => void; role: AppRole }) {
  const [q, setQ] = useState("");
  const [debounced, setDebounced] = useState("");
  const me = useQuery({ queryKey: ["me"], queryFn: () => investigationApi.me() });
  const unread = useQuery({ queryKey: ["unread"], queryFn: () => investigationApi.unreadCount() });

  useEffect(() => {
    const t = setTimeout(() => setDebounced(q.trim()), 300);
    return () => clearTimeout(t);
  }, [q]);

  const search = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => investigationApi.search(debounced),
    enabled: debounced.length >= 2,
  });

  const initials = (me.data?.full_name || "CS")
    .split(" ")
    .map((p: string) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="sticky top-0 z-30 flex items-center gap-2 border-b border-border/70 bg-background/70 px-3 py-2 backdrop-blur-xl sm:gap-3 sm:px-5">
      <button
        type="button"
        onClick={onMenu}
        className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-card text-foreground hover:bg-muted lg:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-4 w-4" />
      </button>

      <HistoryNav />

      <div className="relative min-w-0 flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search"
          aria-label="Search"
          className="h-9 w-full rounded-lg border border-border bg-card py-2 pl-9 pr-3 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:border-primary/50 focus:ring-2 focus:ring-primary/10"
        />
        {debounced.length >= 2 && (
          <div className="absolute left-0 right-0 top-[calc(100%+6px)] z-50 max-h-80 overflow-y-auto rounded-xl border border-border bg-card p-2 shadow-lg">
            {search.isLoading && (
              <p className="px-2 py-2 text-xs text-muted-foreground">Searching…</p>
            )}
            {search.data && <SearchGroups result={search.data} onClose={() => setQ("")} />}
          </div>
        )}
      </div>

      <div className="flex items-center gap-1.5">
        <ThemeToggle />

        <Link
          to="/notifications"
          aria-label="Notifications"
          className="relative grid h-9 w-9 place-items-center rounded-lg border border-border bg-card text-foreground transition hover:bg-muted"
        >
          <Bell className="h-4 w-4" />
          {(unread.data?.count || 0) > 0 && (
            <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-primary" />
          )}
        </Link>

        <Link
          to="/profile"
          className="flex items-center gap-2 rounded-lg border border-border bg-card px-1.5 py-1 sm:px-2"
          aria-label="Profile"
        >
          <div className="grid h-7 w-7 place-items-center rounded-full bg-primary text-[11px] font-semibold text-primary-foreground">
            {initials || <User className="h-3.5 w-3.5" />}
          </div>
          <div className="hidden leading-tight sm:block">
            <p className="max-w-[140px] truncate text-xs font-medium text-foreground">
              {me.data?.full_name || "Account"}
            </p>
            <p className="text-[10px] text-muted-foreground">{ROLE_LABEL[role]}</p>
          </div>
        </Link>
      </div>
    </header>
  );
}

function SearchGroups({ result, onClose }: { result: SearchResult; onClose: () => void }) {
  return (
    <div className="space-y-3 text-sm">
      <Group title="Cases">
        {result.cases.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={onClose}
            className="block w-full rounded-lg px-2 py-1.5 text-left text-foreground hover:bg-muted"
          >
            {c.case_number} — {c.title}
          </button>
        ))}
        {!result.cases.length && <Empty />}
      </Group>
      <Group title="Evidence">
        {result.evidence.map((e) => (
          <div key={e.id} className="rounded-lg px-2 py-1.5 text-muted-foreground">
            {e.original_name}
          </div>
        ))}
        {!result.evidence.length && <Empty />}
      </Group>
    </div>
  );
}

function Group({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <p className="mb-1 px-2 text-[10px] uppercase tracking-wide text-muted-foreground">{title}</p>
      {children}
    </div>
  );
}

function Empty() {
  return <p className="px-2 text-xs text-muted-foreground">No matches</p>;
}
