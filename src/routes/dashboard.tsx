import { createFileRoute, Link, Outlet, useLocation } from "@tanstack/react-router";
import { Shield, LogOut, Bell, Search } from "lucide-react";
import { ParticleBackground } from "@/components/ParticleBackground";

export const Route = createFileRoute("/dashboard")({
  component: DashboardLayout,
});

const NAV = [
  { label: "Investigator", to: "/dashboard/investigator" as const },
  { label: "Supervisor", to: "/dashboard/supervisor" as const },
  { label: "Admin", to: "/dashboard/admin" as const },
];

function DashboardLayout() {
  const { pathname } = useLocation();

  return (
    <div className="relative min-h-screen">
      <ParticleBackground />

      <header className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-5 py-3">
          <Link to="/" className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-violet-glow" />
            <span className="font-display text-base font-semibold tracking-tight">Cyber Shield</span>
          </Link>

          <nav className="order-last flex w-full gap-2 overflow-x-auto sm:order-none sm:ml-6 sm:w-auto">
            {NAV.map((n) => (
              <Link
                key={n.to}
                to={n.to}
                className={`whitespace-nowrap rounded-xl border px-3.5 py-1.5 text-xs font-medium transition-all ${
                  pathname === n.to
                    ? "border-violet-glow/70 bg-accent/60 text-foreground shadow-[0_0_22px_-8px_rgba(168,85,247,0.9)]"
                    : "border-border text-muted-foreground hover:text-foreground"
                }`}
              >
                {n.label}
              </Link>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <button aria-label="Search" className="grid h-9 w-9 place-items-center rounded-xl border border-border text-muted-foreground transition-colors hover:text-foreground">
              <Search className="h-4 w-4" />
            </button>
            <button aria-label="Notifications" className="relative grid h-9 w-9 place-items-center rounded-xl border border-border text-muted-foreground transition-colors hover:text-foreground">
              <Bell className="h-4 w-4" />
              <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-violet-glow" />
            </button>
            <Link
              to="/login"
              className="flex items-center gap-2 rounded-xl border border-border px-3 py-2 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              <LogOut className="h-4 w-4" /> Sign out
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8">
        <Outlet />
      </main>
    </div>
  );
}
