import { createFileRoute } from "@tanstack/react-router";
import {
  Users, KeyRound, ServerCog, ScrollText, PieChart, Settings2,
  ShieldAlert, Activity, BellDot,
} from "lucide-react";
import { ActionGrid, ActivityPanel, DashboardHeader, StatGrid } from "@/components/dashboard/DashboardKit";

export const Route = createFileRoute("/dashboard/admin")({
  head: () => ({
    meta: [
      { title: "Admin Dashboard — Cyber Shield" },
      { name: "description", content: "Manage accounts and roles, audit logs, system uptime, usage reports and platform settings." },
      { property: "og:title", content: "Admin Dashboard — Cyber Shield" },
      { property: "og:description", content: "Account management, permissions, audit logging and system configuration." },
    ],
  }),
  component: AdminDashboard,
});

const STATS = [
  { label: "Active accounts", value: "87", hint: "11 supervisors · 14 forensic", Icon: Users },
  { label: "System uptime", value: "99.98%", hint: "Rolling 30 days", Icon: Activity },
  { label: "Audit events", value: "24.6k", hint: "Logged in last 7 days", Icon: ScrollText },
  { label: "Open incidents", value: "2", hint: "1 awaiting vendor response", Icon: ShieldAlert },
];

const ACTIONS = [
  { title: "Manage accounts", desc: "Create, suspend and deprovision investigator, supervisor and forensic officer accounts.", Icon: Users },
  { title: "Roles & permissions", desc: "Assign and modify role-based permissions with least-privilege defaults.", Icon: KeyRound },
  { title: "Uptime & technical issues", desc: "Monitor service health, respond to incidents and track resolution.", Icon: ServerCog },
  { title: "Audit logs", desc: "Maintain an immutable log of every case-related action for evidentiary integrity.", Icon: ScrollText },
  { title: "System usage reports", desc: "Generate platform-wide reports on activity, adoption and storage.", Icon: PieChart },
  { title: "System settings", desc: "Configure retention, integrations, thresholds and platform-wide defaults.", Icon: Settings2 },
  { title: "Notification preferences", desc: "Define which events notify which roles, and through which channels.", Icon: BellDot },
];

const ACTIVITY = [
  { primary: "New account · Forensic Officer S. Patel", secondary: "Provisioned with forensic-analysis role", tag: "Created" },
  { primary: "Permission change · CASE-ADMIN group", secondary: "Export rights restricted to supervisors", tag: "Updated" },
  { primary: "Audit export", secondary: "7-day log bundle generated for compliance review", tag: "Export" },
  { primary: "Incident INC-114", secondary: "Storage latency degraded — mitigated, monitoring", tag: "Monitor" },
];

function AdminDashboard() {
  return (
    <>
      <DashboardHeader
        eyebrow="Administration"
        title="Accounts, integrity and platform health"
        subtitle="Control who has access to what, keep the audit trail intact and keep the platform running for every investigation team."
      />
      <StatGrid stats={STATS} />
      <ActionGrid
        title="Functionalities"
        description="Everything an admin can do inside Cyber Shield."
        actions={ACTIONS}
      />
      <ActivityPanel title="System log" items={ACTIVITY} />
    </>
  );
}
