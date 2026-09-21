import { Link, Outlet, useNavigate, useRouterState } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, LogOut, Shield } from "lucide-react";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Toaster } from "sonner";
import { RoleTopNavbar } from "@/components/layouts/RoleTopNavbar";
import { NAV_GROUP_LABEL, ROLE_NAV, type NavGroup, type NavItem } from "@/config/roleNav";
import { clearToken, getToken, isAuthenticated } from "@/lib/auth";
import {
  homeForRole,
  ROLE_LABEL,
  roleFromAccessToken,
  normalizeRole,
  type AppRole,
} from "@/lib/roles";
import { useTheme } from "@/lib/theme";
import { cn } from "@/lib/utils";
import { useUnreadChatCount } from "@/hooks/useUnreadChatCount";
import { LoadingBlock } from "@/components/ui-kit/PageKit";
import { CyberAtmosphere } from "@/components/cyber/CyberAtmosphere";

const GROUP_ORDER: NavGroup[] = ["main", "work", "manage", "system"];

export function RoleShell({
  role,
  breadcrumbs,
  children,
}: {
  role: AppRole;
  breadcrumbs?: ReactNode;
  children?: ReactNode;
}) {
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [ready, setReady] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { resolvedTheme } = useTheme();
  const nav = ROLE_NAV[role];
  const unreadChatCount = useUnreadChatCount();
  const isChat = pathname.endsWith("/messages");

  useEffect(() => {
    if (!isAuthenticated()) {
      void navigate({ to: "/login" });
      return;
    }
    const tokenRole = normalizeRole(roleFromAccessToken(getToken()));
    const componentRole = normalizeRole(role);
    if (tokenRole !== componentRole) {
      window.location.assign(homeForRole(tokenRole));
      return;
    }
    setReady(true);
  }, [navigate, role]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const grouped = useMemo(() => {
    const map = new Map<NavGroup, NavItem[]>();
    for (const item of nav) {
      const g = item.group || "main";
      const list = map.get(g) || [];
      list.push(item);
      map.set(g, list);
    }
    return GROUP_ORDER.map((g) => ({ group: g, items: map.get(g) || [] })).filter(
      (x) => x.items.length,
    );
  }, [nav]);

  function logout() {
    clearToken();
    void navigate({ to: "/login" });
  }

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-8">
        <div className="w-full max-w-sm">
          <LoadingBlock rows={4} />
        </div>
      </div>
    );
  }

  const sidebar = (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between gap-2 border-b border-sidebar-border px-3 py-3">
        <Link to={ROLE_NAV[role][0].to as "/"} className="flex min-w-0 items-center gap-2">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-primary to-cyan shadow-[0_0_18px_-4px_rgba(59,130,246,0.8)]">
            <Shield className="h-4 w-4 text-primary-foreground" />
          </span>
          {!collapsed && (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-foreground">Cyber Shield</p>
              <p className="truncate text-[10px] text-muted-foreground">{ROLE_LABEL[role]}</p>
            </div>
          )}
        </Link>
        <button
          type="button"
          onClick={() => setCollapsed((v) => !v)}
          className="hidden h-8 w-8 place-items-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground lg:grid"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      <nav className="flex-1 space-y-4 overflow-y-auto px-2 py-3">
        {grouped.map(({ group, items }) => (
          <div key={group}>
            {!collapsed && (
              <p className="mb-1 px-2 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                {NAV_GROUP_LABEL[group]}
              </p>
            )}
            <div className="space-y-0.5">
              {items.map((item) => {
                const active = item.exact ? pathname === item.to : pathname.startsWith(item.to);
                const isMessages =
                  item.label.toLowerCase().includes("message") || item.to.includes("messages");
                return (
                  <Link
                    key={item.to}
                    to={item.to as "/"}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[13px] font-medium transition",
                      active
                        ? "bg-primary/15 text-foreground shadow-[inset_0_0_0_1px_rgb(59_130_246_/_0.35)]"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground",
                      collapsed && "justify-center px-2",
                    )}
                    title={item.label}
                  >
                    <div className="relative shrink-0">
                      <item.icon className="h-4 w-4" />
                      {isMessages && unreadChatCount > 0 && collapsed && (
                        <span className="absolute -right-1.5 -top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[9px] font-semibold text-primary-foreground">
                          {unreadChatCount > 99 ? "99+" : unreadChatCount}
                        </span>
                      )}
                    </div>
                    {!collapsed && (
                      <>
                        <span className="truncate">{item.label}</span>
                        {isMessages && unreadChatCount > 0 && (
                          <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1.5 text-[10px] font-semibold text-primary-foreground">
                            {unreadChatCount > 99 ? "99+" : unreadChatCount}
                          </span>
                        )}
                      </>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-sidebar-border p-2">
        <button
          type="button"
          onClick={logout}
          className={cn(
            "flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-[13px] text-muted-foreground transition hover:bg-destructive/10 hover:text-destructive",
            collapsed && "justify-center px-2",
          )}
        >
          <LogOut className="h-4 w-4" />
          {!collapsed && "Sign out"}
        </button>
      </div>
    </div>
  );

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background text-foreground">
      <CyberAtmosphere />
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 hidden border-r border-sidebar-border bg-sidebar/85 text-sidebar-foreground backdrop-blur-xl transition-[width] duration-200 lg:block",
          collapsed ? "w-[72px]" : "w-60",
        )}
      >
        {sidebar}
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/50"
            aria-label="Close menu"
            onClick={() => setMobileOpen(false)}
          />
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            transition={{ duration: 0.2 }}
            className="relative h-full w-72 border-r border-sidebar-border bg-sidebar/95 text-sidebar-foreground shadow-xl backdrop-blur-xl"
          >
            {sidebar}
          </motion.aside>
        </div>
      )}

      <div
        className={cn("transition-[padding] duration-200", collapsed ? "lg:pl-[72px]" : "lg:pl-60")}
      >
        <RoleTopNavbar onMenu={() => setMobileOpen(true)} role={role} />
        {breadcrumbs && (
          <div className="border-b border-border/40 px-4 py-1.5 text-xs text-muted-foreground sm:px-5">
            {breadcrumbs}
          </div>
        )}
        <main
          className={cn(
            "relative z-[1]",
            isChat
              ? "h-[calc(100dvh-3.25rem)] overflow-hidden p-0"
              : "min-h-[calc(100dvh-3.25rem)] px-4 py-4 sm:px-5",
          )}
        >
          {children ?? <Outlet />}
        </main>
      </div>
      <Toaster theme={resolvedTheme} position="top-right" richColors />
    </div>
  );
}
