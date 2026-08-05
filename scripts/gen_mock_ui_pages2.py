"""Generate remaining CyberShield mock UI pages."""
from pathlib import Path

ROOT = Path(r"d:/cybershield/cyber-shield-portal/src/routes")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print(rel)


# Run first script pages if not done - re-import by exec first file partially
exec(open(r"d:/cybershield/cyber-shield-portal/scripts/gen_mock_ui_pages.py", encoding="utf-8").read().split('print("batch1 ok")')[0] + 'print("batch1 ok")')

# ---- Major admin remaining ----
w(
    "major-admin/users.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_USERS } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, StatusPill, Toolbar, useClientTable, SelectFilter } from "@/components/ui-kit/PageKit";
import { useState } from "react";

export const Route = createFileRoute("/major-admin/users")({ component: Page });

function Page() {
  const [role, setRole] = useState("All roles");
  const filtered = MOCK_USERS.filter((u) => role === "All roles" || u.role === role);
  const table = useClientTable(filtered);
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Users" }]} title="Users" subtitle="Platform-wide directory">
      <Toolbar search={table.search} onSearch={table.setSearch} filters={<SelectFilter value={role} onChange={setRole} options={["All roles", "Major Admin", "Admin", "Superior Officer", "Investigator"]} />} />
      <DataTable rows={table.rows} columns={[
        { key: "n", header: "Name", render: (r) => <Link to={"/major-admin/users/$userId" as "/"} params={{ userId: r.id } as never} className="text-cyan hover:underline">{r.name}</Link> },
        { key: "e", header: "Email", render: (r) => r.email },
        { key: "r", header: "Role", render: (r) => r.role },
        { key: "d", header: "Department", render: (r) => r.department },
        { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/users.$userId.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_USERS, MOCK_AUDIT } from "@/data/mock/platform";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";
import { ProfileCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/major-admin/users/$userId")({ component: Page });

function Page() {
  const { userId } = Route.useParams();
  const user = MOCK_USERS.find((u) => u.id === userId) || MOCK_USERS[0];
  return (
    <PageScaffold crumbs={[{ label: "Users", to: "/major-admin/users" }, { label: user.name }]} title="User details" subtitle={user.email}>
      <div className="grid gap-4 lg:grid-cols-2">
        <ProfileCard name={user.name} email={user.email} role={user.role} department={user.department} />
        <Panel title="Account">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-slate-500">Status</dt><dd><StatusPill value={user.status} /></dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Phone</dt><dd>{user.phone || "—"}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Last login</dt><dd>{user.lastLogin}</dd></div>
          </dl>
        </Panel>
        <Panel title="Recent activity" className="lg:col-span-2">
          <ul className="space-y-2">{MOCK_AUDIT.slice(0,4).map((a) => <li key={a.id} className="text-sm text-slate-300"><span className="text-cyan">{a.action}</span> — {a.resource}</li>)}</ul>
        </Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/cases.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { MOCK_CASES } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, SelectFilter, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/cases")({ component: Page });

function Page() {
  const [status, setStatus] = useState("All");
  const items = MOCK_CASES.filter((c) => status === "All" || c.status === status);
  const table = useClientTable(items);
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Cases" }]} title="Cases" subtitle="Global case oversight">
      <Toolbar search={table.search} onSearch={table.setSearch} filters={<SelectFilter value={status} onChange={setStatus} options={["All", "Open", "Under Review", "Evidence Collection", "Analysis", "Completed"]} />} />
      <DataTable rows={table.rows} columns={[
        { key: "id", header: "Case", render: (r) => <span className="text-cyan">{r.caseNumber}</span> },
        { key: "t", header: "Title", render: (r) => r.title },
        { key: "p", header: "Priority", render: (r) => <StatusPill value={r.priority} /> },
        { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
        { key: "a", header: "Assignee", render: (r) => r.assignee },
        { key: "u", header: "Updated", render: (r) => r.updated },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/reports.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { MOCK_REPORTS } from "@/data/mock/platform";
import { PageScaffold, Toolbar, useClientTable, Pagination, EmptyState } from "@/components/ui-kit/PageKit";
import { ReportCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/major-admin/reports")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_REPORTS);
  const [preview, setPreview] = useState<string | null>(null);
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "System Reports" }]} title="System Reports" subtitle="Platform investigation report library">
      <Toolbar search={table.search} onSearch={table.setSearch} />
      {!table.rows.length ? <EmptyState /> : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {table.rows.map((r) => <ReportCard key={r.id} title={r.title} format={r.format} author={r.author} created={r.created} onPreview={() => setPreview(r.title)} />)}
        </div>
      )}
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
      {preview && <div className="mt-4 rounded-2xl border border-white/10 bg-[#111827]/90 p-6"><p className="text-sm font-semibold text-slate-100">Preview — {preview}</p><p className="mt-2 text-sm text-slate-400">Print-friendly mock report body. Export PDF / Print are UI-only.</p><div className="mt-4 flex gap-2"><button type="button" className="rounded-xl bg-primary px-4 py-2 text-sm text-white">Export PDF</button><button type="button" className="rounded-xl border border-white/10 px-4 py-2 text-sm" onClick={() => window.print()}>Print</button></div></div>}
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/analytics.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Radar, RadarChart, PolarGrid, PolarAngleAxis } from "recharts";
import { ChartCard, PageScaffold } from "@/components/ui-kit/PageKit";
import { PageHeader } from "@/components/layouts/DashboardWidgets";

export const Route = createFileRoute("/major-admin/analytics")({ component: Page });

const monthly = [{ m: "Mar", c: 12 }, { m: "Apr", c: 18 }, { m: "May", c: 15 }, { m: "Jun", c: 22 }, { m: "Jul", c: 28 }, { m: "Aug", c: 19 }];
const growth = [{ m: "Mar", u: 40 }, { m: "Apr", u: 48 }, { m: "May", u: 55 }, { m: "Jun", u: 61 }, { m: "Jul", u: 70 }, { m: "Aug", u: 78 }];
const radar = [{ subject: "CCU", A: 120 }, { subject: "DFL", A: 98 }, { subject: "DHQ", A: 86 }, { subject: "SOC", A: 65 }];

function Page() {
  return (
    <div>
      <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Analytics" }]} title="System Analytics" subtitle="Platform trends (mock)">
        <div className="grid gap-4 lg:grid-cols-2">
          <ChartCard title="Monthly cases"><div className="h-56"><ResponsiveContainer width="100%" height="100%"><BarChart data={monthly}><CartesianGrid strokeDasharray="3 3" stroke="#1f2937" /><XAxis dataKey="m" stroke="#64748b" fontSize={11} /><YAxis stroke="#64748b" fontSize={11} /><Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} /><Bar dataKey="c" fill="#3B82F6" radius={[6,6,0,0]} /></BarChart></ResponsiveContainer></div></ChartCard>
          <ChartCard title="User growth"><div className="h-56"><ResponsiveContainer width="100%" height="100%"><LineChart data={growth}><CartesianGrid strokeDasharray="3 3" stroke="#1f2937" /><XAxis dataKey="m" stroke="#64748b" fontSize={11} /><YAxis stroke="#64748b" fontSize={11} /><Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} /><Line type="monotone" dataKey="u" stroke="#06B6D4" strokeWidth={2} /></LineChart></ResponsiveContainer></div></ChartCard>
          <ChartCard title="Department load"><div className="h-56"><ResponsiveContainer width="100%" height="100%"><RadarChart data={radar}><PolarGrid stroke="#334155" /><PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} /><Radar dataKey="A" stroke="#3B82F6" fill="#3B82F644" /></RadarChart></ResponsiveContainer></div></ChartCard>
        </div>
      </PageScaffold>
    </div>
  );
}
''',
)

w(
    "major-admin/audit-logs.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_AUDIT } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/audit-logs")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_AUDIT, 6);
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Audit Logs" }]} title="Audit Logs" subtitle="Security and operational activity">
      <Toolbar search={table.search} onSearch={table.setSearch} placeholder="Search actions, actors…" />
      <DataTable rows={table.rows} columns={[
        { key: "a", header: "Action", render: (r) => <span className="text-cyan">{r.action}</span> },
        { key: "u", header: "Actor", render: (r) => r.actor },
        { key: "r", header: "Resource", render: (r) => r.resource },
        { key: "t", header: "Time", render: (r) => r.time },
        { key: "i", header: "IP", render: (r) => r.ip },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/roles.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/roles")({ component: Page });

const ROLES = [
  { role: "Major Admin", perms: ["Manage admins", "Departments", "Global audit", "Backups"] },
  { role: "Admin", perms: ["Create officers", "Manage users", "District cases", "Reports"] },
  { role: "Superior Officer", perms: ["Create cases", "Assign investigators", "Approve reports", "Close cases"] },
  { role: "Investigator", perms: ["Upload evidence", "Notes", "Manual leads", "Draft reports"] },
];

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Roles & Permissions" }]} title="Roles & Permissions" subtitle="RBAC matrix (UI mock)">
      <div className="grid gap-4 md:grid-cols-2">
        {ROLES.map((r) => (
          <Panel key={r.role} title={r.role}>
            <ul className="space-y-2">{r.perms.map((p) => <li key={p} className="flex items-center justify-between text-sm text-slate-300"><span>{p}</span><StatusPill value="Allowed" /></li>)}</ul>
          </Panel>
        ))}
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/settings.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/settings")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Platform Settings" }]} title="Platform Settings" subtitle="System configuration (UI only)">
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="General">
          <label className="block text-xs text-slate-400">Platform name<input defaultValue="CyberShield" className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" /></label>
          <label className="mt-3 block text-xs text-slate-400">Support email<input defaultValue="support@cybershield.gov" className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" /></label>
          <PrimaryButton className="mt-4">Save</PrimaryButton>
        </Panel>
        <Panel title="Security">
          <label className="flex items-center justify-between text-sm text-slate-300"><span>Require MFA for admins</span><input type="checkbox" defaultChecked className="accent-cyan" /></label>
          <label className="mt-3 flex items-center justify-between text-sm text-slate-300"><span>Session timeout (minutes)</span><input type="number" defaultValue={60} className="w-20 rounded-lg border border-white/10 bg-[#0b1220] px-2 py-1 text-sm" /></label>
        </Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/storage.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_STORAGE } from "@/data/mock/platform";
import { PageScaffold, Panel } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/storage")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Storage" }]} title="Storage Management" subtitle="Vault usage overview (mock)">
      <div className="grid gap-4 md:grid-cols-3">
        {MOCK_STORAGE.map((s) => (
          <Panel key={s.name} title={s.name}>
            <p className="text-2xl font-bold text-slate-50">{s.used}%</p>
            <p className="text-xs text-slate-500">of {s.total}</p>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-gradient-to-r from-primary to-cyan" style={{ width: `${s.used}%` }} /></div>
          </Panel>
        ))}
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "major-admin/backup.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { PageScaffold, Panel, PrimaryButton, GhostButton, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/backup")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Backup & Restore" }]} title="Backup & Restore" subtitle="Operational continuity controls (UI mock)">
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Latest backups">
          <ul className="space-y-3">{[
            ["Nightly full", "2026-08-03 02:00", "Success"],
            ["Incremental", "2026-08-02 14:00", "Success"],
            ["Config snapshot", "2026-08-01 09:00", "Success"],
          ].map(([n, t, s]) => <li key={n} className="flex items-center justify-between text-sm"><div><p className="text-slate-100">{n}</p><p className="text-xs text-slate-500">{t}</p></div><StatusPill value={s} /></li>)}</ul>
          <div className="mt-4 flex gap-2"><PrimaryButton>Run backup</PrimaryButton><GhostButton>Download last</GhostButton></div>
        </Panel>
        <Panel title="Restore">
          <p className="text-sm text-slate-400">Select a snapshot to restore into a staging environment. Destructive restore is disabled in UI mock.</p>
          <select className="mt-3 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>Nightly full — Aug 3</option><option>Incremental — Aug 2</option></select>
          <GhostButton className="mt-4">Preview restore plan</GhostButton>
        </Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

print("major-admin extras done")
