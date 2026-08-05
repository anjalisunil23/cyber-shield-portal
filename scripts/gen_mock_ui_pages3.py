"""Admin, Superior, Investigator, and common mock UI pages."""
from pathlib import Path

ROOT = Path(r"d:/cybershield/cyber-shield-portal/src/routes")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print(rel)


# ========== ADMIN ==========
w(
    "admin/users.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_USERS } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, PrimaryButton, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/users")({ component: Page });

function Page() {
  const users = MOCK_USERS.filter((u) => u.role !== "Major Admin");
  const table = useClientTable(users);
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Users" }]} title="Users" subtitle="Organization directory" actions={<Link to={"/admin/users/create" as "/"}><PrimaryButton>Create user</PrimaryButton></Link>}>
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "n", header: "Name", render: (r) => r.name },
        { key: "e", header: "Email", render: (r) => r.email },
        { key: "r", header: "Role", render: (r) => r.role },
        { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
        { key: "a", header: "", render: (r) => <Link to={"/admin/users/$userId/edit" as "/"} params={{ userId: r.id } as never} className="text-xs text-cyan">Edit</Link> },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "admin/users.create.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/users/create")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Users", to: "/admin/users" }, { label: "Create" }]} title="Create User" subtitle="Add Superior Officer or Investigator" actions={<Link to={"/admin/users" as "/"}><GhostButton>Cancel</GhostButton></Link>}>
      <Panel>
        <form className="mx-auto grid max-w-xl gap-3" onSubmit={(e) => e.preventDefault()}>
          <input placeholder="Full name" className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <input placeholder="Email" type="email" className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>Investigator</option><option>Superior Officer</option></select>
          <input placeholder="Department" className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <PrimaryButton type="submit">Create (UI)</PrimaryButton>
        </form>
      </Panel>
    </PageScaffold>
  );
}
''',
)

w(
    "admin/users.$userId.edit.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_USERS } from "@/data/mock/platform";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/users/$userId/edit")({ component: Page });

function Page() {
  const { userId } = Route.useParams();
  const user = MOCK_USERS.find((u) => u.id === userId) || MOCK_USERS[2];
  return (
    <PageScaffold crumbs={[{ label: "Users", to: "/admin/users" }, { label: "Edit" }]} title={`Edit ${user.name}`} subtitle={user.email}>
      <Panel>
        <form className="mx-auto grid max-w-xl gap-3" onSubmit={(e) => e.preventDefault()}>
          <input defaultValue={user.name} className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <input defaultValue={user.department} className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <select defaultValue={user.status} className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>Active</option><option>Suspended</option></select>
          <div className="flex gap-2"><PrimaryButton type="submit">Save</PrimaryButton><Link to={"/admin/users" as "/"}><GhostButton>Back</GhostButton></Link></div>
        </form>
      </Panel>
    </PageScaffold>
  );
}
''',
)

w(
    "admin/superior-officers.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_USERS } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, PrimaryButton, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/superior-officers")({ component: Page });

function Page() {
  const rows = MOCK_USERS.filter((u) => u.role === "Superior Officer");
  const table = useClientTable(rows);
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Superior Officers" }]} title="Superior Officers" subtitle="Heads of investigation" actions={<Link to={"/admin/users/create" as "/"}><PrimaryButton>Create</PrimaryButton></Link>}>
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "n", header: "Name", render: (r) => r.name },
        { key: "e", header: "Email", render: (r) => r.email },
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
    "admin/investigators.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_USERS } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, PrimaryButton, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/investigators")({ component: Page });

function Page() {
  const rows = MOCK_USERS.filter((u) => u.role === "Investigator");
  const table = useClientTable(rows);
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Investigators" }]} title="Investigators" subtitle="Field investigation staff" actions={<Link to={"/admin/users/create" as "/"}><PrimaryButton>Create</PrimaryButton></Link>}>
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "n", header: "Name", render: (r) => r.name },
        { key: "e", header: "Email", render: (r) => r.email },
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
    "admin/cases.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, StatusPill, Toolbar, useClientTable, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/cases")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_CASES);
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Department Cases" }]} title="Department Cases" subtitle="Cases across your organization" actions={<Link to={"/admin/assignments" as "/"}><PrimaryButton>Case assignments</PrimaryButton></Link>}>
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "c", header: "Case", render: (r) => <span className="text-cyan">{r.caseNumber}</span> },
        { key: "t", header: "Title", render: (r) => r.title },
        { key: "p", header: "Priority", render: (r) => <StatusPill value={r.priority} /> },
        { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
        { key: "a", header: "Assignee", render: (r) => r.assignee },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "admin/evidence.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_EVIDENCE } from "@/data/mock/platform";
import { PageScaffold, Toolbar, useClientTable, Pagination, SelectFilter } from "@/components/ui-kit/PageKit";
import { EvidenceCard } from "@/components/ui-kit/Cards";
import { useState } from "react";

export const Route = createFileRoute("/admin/evidence")({ component: Page });

function Page() {
  const [cat, setCat] = useState("All");
  const items = MOCK_EVIDENCE.filter((e) => cat === "All" || e.type === cat);
  const table = useClientTable(items, 6);
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Evidence Categories" }]} title="Evidence Categories" subtitle="Browse evidence by type">
      <Toolbar search={table.search} onSearch={table.setSearch} filters={<SelectFilter value={cat} onChange={setCat} options={["All", "image", "video", "audio", "pdf", "document", "other"]} />} />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{table.rows.map((e) => <EvidenceCard key={e.id} item={e} />)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "admin/reports.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_REPORTS } from "@/data/mock/platform";
import { PageScaffold, Toolbar, useClientTable, Pagination } from "@/components/ui-kit/PageKit";
import { ReportCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/admin/reports")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_REPORTS);
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Reports" }]} title="Reports" subtitle="Generate and review investigation reports">
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <div className="grid gap-3 sm:grid-cols-2">{table.rows.map((r) => <ReportCard key={r.id} {...r} />)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "admin/analytics.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { Bar, BarChart, CartesianGrid, Pie, PieChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard, PageScaffold } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/analytics")({ component: Page });

const status = [{ name: "Open", value: 8 }, { name: "Review", value: 5 }, { name: "Completed", value: 12 }];
const perf = [{ d: "CCU", v: 42 }, { d: "DFL", v: 28 }, { d: "DHQ", v: 15 }];
const COLORS = ["#3B82F6", "#F59E0B", "#10B981"];

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Analytics" }]} title="Analytics" subtitle="Department performance (mock)">
      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Case status"><div className="h-56"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={status} dataKey="value" nameKey="name" outerRadius={80}>{status.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}</Pie><Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} /></PieChart></ResponsiveContainer></div></ChartCard>
        <ChartCard title="Department performance"><div className="h-56"><ResponsiveContainer width="100%" height="100%"><BarChart data={perf}><CartesianGrid strokeDasharray="3 3" stroke="#1f2937" /><XAxis dataKey="d" stroke="#64748b" fontSize={11} /><YAxis stroke="#64748b" fontSize={11} /><Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} /><Bar dataKey="v" fill="#06B6D4" radius={[6,6,0,0]} /></BarChart></ResponsiveContainer></div></ChartCard>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "admin/assignments.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_USERS } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, DataTable, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/assignments")({ component: Page });

function Page() {
  const investigators = MOCK_USERS.filter((u) => u.role === "Investigator");
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Case Assignments" }]} title="Case Assignments" subtitle="Assign investigators to open cases">
      <Panel title="Assign">
        <form className="grid gap-3 sm:grid-cols-3" onSubmit={(e) => e.preventDefault()}>
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{MOCK_CASES.map((c) => <option key={c.id}>{c.caseNumber}</option>)}</select>
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{investigators.map((u) => <option key={u.id}>{u.name}</option>)}</select>
          <PrimaryButton type="submit">Assign (UI)</PrimaryButton>
        </form>
      </Panel>
      <DataTable rows={MOCK_CASES} columns={[
        { key: "c", header: "Case", render: (r) => r.caseNumber },
        { key: "t", header: "Title", render: (r) => r.title },
        { key: "a", header: "Assignee", render: (r) => r.assignee },
        { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
      ]} />
    </PageScaffold>
  );
}
''',
)

w(
    "admin/settings.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/admin/settings")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Admin", to: "/admin/dashboard" }, { label: "Settings" }]} title="Settings" subtitle="Account and notification preferences">
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="General"><label className="block text-xs text-slate-400">Display name<input defaultValue="District Admin" className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" /></label><PrimaryButton className="mt-4">Save</PrimaryButton></Panel>
        <Panel title="Notifications"><label className="flex items-center justify-between text-sm"><span>Email digests</span><input type="checkbox" defaultChecked className="accent-cyan" /></label><label className="mt-3 flex items-center justify-between text-sm"><span>Case assignment alerts</span><input type="checkbox" defaultChecked className="accent-cyan" /></label></Panel>
        <Panel title="Theme"><label className="flex items-center justify-between text-sm"><span>Dark mode</span><input type="checkbox" defaultChecked className="accent-cyan" /></label></Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

print("admin done")

# ========== SUPERIOR ==========
CASE_LIST = '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { MOCK_CASES } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, PrimaryButton, SelectFilter, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";
import { CaseCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("__PATH__")({ component: Page });

function Page() {
  const [view, setView] = useState<"table" | "grid">("table");
  const [status, setStatus] = useState("All");
  const items = MOCK_CASES.filter((c) => status === "All" || c.status === status);
  const table = useClientTable(items);
  return (
    <PageScaffold crumbs={[{ label: "__ROLE__", to: "__HOME__" }, { label: "Cases" }]} title="__TITLE__" subtitle="Investigation case management" actions={<><Ghostish /><Link to={"__CREATE__" as "/"}><PrimaryButton>Create case</PrimaryButton></Link></>}>
      <Toolbar search={table.search} onSearch={table.setSearch} filters={<><SelectFilter value={status} onChange={setStatus} options={["All", "Open", "Under Review", "Evidence Collection", "Analysis", "Completed"]} /><button type="button" onClick={() => setView(view === "table" ? "grid" : "table")} className="rounded-xl border border-white/10 px-3 py-2 text-xs">{view === "table" ? "Grid" : "Table"}</button></>} />
      {view === "table" ? (
        <>
          <DataTable rows={table.rows} columns={[
            { key: "c", header: "Case", render: (r) => <Link to={"__DETAIL__" as "/"} params={{ caseId: r.id } as never} className="text-cyan hover:underline">{r.caseNumber}</Link> },
            { key: "t", header: "Title", render: (r) => r.title },
            { key: "p", header: "Priority", render: (r) => <StatusPill value={r.priority} /> },
            { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
            { key: "a", header: "Assignee", render: (r) => r.assignee },
          ]} />
          <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
        </>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{table.rows.map((c) => <CaseCard key={c.id} item={c} onOpen={() => location.assign(`__DETAIL_OPEN__${c.id}`)} />)}</div>
      )}
    </PageScaffold>
  );
}
function Ghostish() { return null; }
'''

# Fix superior cases - write properly without broken Ghostish
w(
    "superior/cases.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { MOCK_CASES } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, PrimaryButton, SelectFilter, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";
import { CaseCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/superior/cases")({ component: Page });

function Page() {
  const [view, setView] = useState<"table" | "grid">("table");
  const [status, setStatus] = useState("All");
  const items = MOCK_CASES.filter((c) => status === "All" || c.status === status);
  const table = useClientTable(items);
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "All Cases" }]} title="All Cases" subtitle="Create, assign, and monitor investigations" actions={<Link to={"/superior/cases/create" as "/"}><PrimaryButton>Create case</PrimaryButton></Link>}>
      <Toolbar search={table.search} onSearch={table.setSearch} filters={<><SelectFilter value={status} onChange={setStatus} options={["All", "Open", "Under Review", "Evidence Collection", "Analysis", "Completed"]} /><button type="button" onClick={() => setView(view === "table" ? "grid" : "table")} className="rounded-xl border border-white/10 px-3 py-2 text-xs">{view === "table" ? "Grid" : "Table"}</button></>} />
      {view === "table" ? (
        <>
          <DataTable rows={table.rows} columns={[
            { key: "c", header: "Case", render: (r) => <Link to={"/superior/cases/$caseId" as "/"} params={{ caseId: r.id } as never} className="text-cyan hover:underline">{r.caseNumber}</Link> },
            { key: "t", header: "Title", render: (r) => r.title },
            { key: "p", header: "Priority", render: (r) => <StatusPill value={r.priority} /> },
            { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
            { key: "a", header: "Assignee", render: (r) => r.assignee },
          ]} />
          <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
        </>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{table.rows.map((c) => <Link key={c.id} to={"/superior/cases/$caseId" as "/"} params={{ caseId: c.id } as never}><CaseCard item={c} /></Link>)}</div>
      )}
    </PageScaffold>
  );
}
''',
)

print("partial superior")
