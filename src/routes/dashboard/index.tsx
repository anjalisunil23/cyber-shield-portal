import { createFileRoute, Link } from "@tanstack/react-router";
import { Briefcase, ShieldCheck, Settings2, ArrowRight } from "lucide-react";
import { DashboardHeader } from "@/components/dashboard/DashboardKit";

export const Route = createFileRoute("/dashboard/")({
  head: () => ({
    meta: [
      { title: "Dashboards — Cyber Shield" },
      { name: "description", content: "Choose your Cyber Shield workspace: investigator, supervisor or admin." },
      { property: "og:title", content: "Dashboards — Cyber Shield" },
      { property: "og:description", content: "Role-based workspaces for investigators, supervisors and administrators." },
    ],
  }),
  component: DashboardIndex,
});

const ROLES = [
  { to: "/dashboard/investigator" as const, label: "Investigator", desc: "Cases, notes, evidence metadata, forensic requests and AI report review.", Icon: Briefcase },
  { to: "/dashboard/supervisor" as const, label: "Supervisor", desc: "Report approvals, caseload and forensic workload monitoring, AI feedback.", Icon: ShieldCheck },
  { to: "/dashboard/admin" as const, label: "Admin", desc: "Accounts, roles and permissions, audit logs, uptime and system settings.", Icon: Settings2 },
];

function DashboardIndex() {
  return (
    <>
      <DashboardHeader
        eyebrow="Workspaces"
        title="Choose your dashboard"
        subtitle="Each role sees only the functionality and data its permissions allow."
      />
      <div className="mt-8 grid gap-5 md:grid-cols-3">
        {ROLES.map(({ to, label, desc, Icon }, i) => (
          <Link
            key={to}
            to={to}
            className="glass-card glow-hover animate-rise-in group p-6"
            style={{ animationDelay: `${0.06 * i}s` }}
          >
            <div
              className="grid h-12 w-12 place-items-center rounded-xl border border-violet-glow/35 bg-surface/60 transition-transform group-hover:scale-110"
              style={{ boxShadow: "0 0 24px -8px rgba(168,85,247,0.9)" }}
            >
              <Icon className="h-6 w-6 text-violet-glow" />
            </div>
            <h2 className="mt-5 text-lg font-semibold">{label}</h2>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{desc}</p>
            <span className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-violet-glow">
              Open <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </span>
          </Link>
        ))}
      </div>
    </>
  );
}
