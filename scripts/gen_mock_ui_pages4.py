"""Superior, investigator, common pages."""
from pathlib import Path

ROOT = Path(r"d:/cybershield/cyber-shield-portal/src/routes")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print(rel)


w(
    "superior/cases.create.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/cases/create")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Cases", to: "/superior/cases" }, { label: "Create" }]} title="Create Case" subtitle="Open a new investigation" actions={<Link to={"/superior/cases" as "/"}><GhostButton>Cancel</GhostButton></Link>}>
      <Panel>
        <form className="mx-auto grid max-w-2xl gap-3" onSubmit={(e) => e.preventDefault()}>
          <input required placeholder="Title" className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <textarea placeholder="Description" rows={4} className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>Low</option><option>Medium</option><option>High</option><option>Critical</option></select>
            <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>Open</option><option>Under Review</option></select>
          </div>
          <PrimaryButton type="submit">Create case (UI)</PrimaryButton>
        </form>
      </Panel>
    </PageScaffold>
  );
}
''',
)

w(
    "superior/cases.$caseId.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_EVIDENCE, MOCK_NOTES, MOCK_TIMELINE } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, StatusPill, GhostButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/cases/$caseId")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const c = MOCK_CASES.find((x) => x.id === caseId) || MOCK_CASES[0];
  return (
    <PageScaffold crumbs={[{ label: "Cases", to: "/superior/cases" }, { label: c.caseNumber }]} title={c.title} subtitle={c.description} actions={<div className="flex gap-2"><Link to={"/superior/cases/$caseId/assign" as "/"} params={{ caseId: c.id } as never}><PrimaryButton>Assign</PrimaryButton></Link><GhostButton>Close case</GhostButton></div>}>
      <div className="mb-4 flex flex-wrap gap-2"><StatusPill value={c.priority} /><StatusPill value={c.status} /><span className="text-xs text-slate-500">Assignee: {c.assignee}</span></div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Evidence">{MOCK_EVIDENCE.filter((e) => e.caseNumber === c.caseNumber).map((e) => <p key={e.id} className="text-sm text-slate-300">{e.name}</p>)}</Panel>
        <Panel title="Notes">{MOCK_NOTES.filter((n) => n.caseNumber === c.caseNumber).map((n) => <div key={n.id} className="mb-2"><p className="text-sm font-medium text-slate-100">{n.title}</p><p className="text-xs text-slate-500">{n.body}</p></div>)}</Panel>
        <Panel title="Timeline" className="lg:col-span-2"><ol className="space-y-3">{MOCK_TIMELINE.map((t) => <li key={t.id} className="border-l border-cyan/40 pl-3"><p className="text-sm text-slate-100">{t.title}</p><p className="text-xs text-slate-500">{t.at} — {t.detail}</p></li>)}</ol></Panel>
        <Panel title="Attachments / Reports" className="lg:col-span-2"><p className="text-sm text-slate-400">Use Reports tab to generate investigation summaries for this case.</p><Link to={"/superior/reports" as "/"} className="mt-2 inline-block text-sm text-cyan">Open reports →</Link></Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "superior/cases.$caseId.assign.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_USERS } from "@/data/mock/platform";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/cases/$caseId/assign")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const c = MOCK_CASES.find((x) => x.id === caseId) || MOCK_CASES[0];
  const investigators = MOCK_USERS.filter((u) => u.role === "Investigator");
  return (
    <PageScaffold crumbs={[{ label: c.caseNumber, to: `/superior/cases/${c.id}` }, { label: "Assign" }]} title="Assign Investigator" subtitle={c.title}>
      <Panel>
        <form className="mx-auto grid max-w-lg gap-3" onSubmit={(e) => e.preventDefault()}>
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{investigators.map((u) => <option key={u.id}>{u.name}</option>)}</select>
          <label className="flex items-center gap-2 text-sm text-slate-300"><input type="checkbox" defaultChecked className="accent-cyan" /> Primary assignee</label>
          <div className="flex gap-2"><PrimaryButton type="submit">Assign (UI)</PrimaryButton><Link to={"/superior/cases/$caseId" as "/"} params={{ caseId: c.id } as never}><GhostButton>Back</GhostButton></Link></div>
        </form>
      </Panel>
    </PageScaffold>
  );
}
''',
)

w(
    "superior/evidence.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_EVIDENCE } from "@/data/mock/platform";
import { PageScaffold, Toolbar, useClientTable, Pagination } from "@/components/ui-kit/PageKit";
import { EvidenceCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/superior/evidence")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_EVIDENCE, 6);
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Evidence Review" }]} title="Evidence Review" subtitle="Inspect uploads across cases">
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{table.rows.map((e) => <Link key={e.id} to={"/superior/evidence/$evidenceId" as "/"} params={{ evidenceId: e.id } as never}><EvidenceCard item={e} /></Link>)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "superior/evidence.$evidenceId.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_EVIDENCE } from "@/data/mock/platform";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/evidence/$evidenceId")({ component: Page });

function Page() {
  const { evidenceId } = Route.useParams();
  const e = MOCK_EVIDENCE.find((x) => x.id === evidenceId) || MOCK_EVIDENCE[0];
  return (
    <PageScaffold crumbs={[{ label: "Evidence", to: "/superior/evidence" }, { label: e.name }]} title={e.name} subtitle={`${e.type} · ${e.size}`}>
      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Viewer" className="lg:col-span-2">
          <div className="grid h-64 place-items-center rounded-xl border border-dashed border-white/15 bg-black/30 text-sm text-slate-500">
            {e.type === "image" && "Image viewer mock"}
            {e.type === "video" && "Video player mock"}
            {e.type === "audio" && "Audio player mock"}
            {e.type === "pdf" && "PDF viewer mock"}
            {(e.type === "document" || e.type === "other") && "Document viewer mock"}
          </div>
        </Panel>
        <Panel title="Metadata">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-slate-500">Case</dt><dd className="text-cyan">{e.caseNumber}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">SHA256</dt><dd className="font-mono text-xs">{e.sha256}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Uploaded</dt><dd>{e.uploadedAt}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">By</dt><dd>{e.uploadedBy}</dd></div>
          </dl>
          <div className="mt-3 flex flex-wrap gap-1">{e.tags.map((t) => <StatusPill key={t} value={t} />)}</div>
          <div className="mt-4 rounded-xl border border-dashed border-cyan/30 bg-cyan/5 p-3 text-xs text-slate-400">AI panel placeholder — OCR / objects / transcript</div>
        </Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "superior/timeline.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_TIMELINE } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";
import { useState } from "react";

export const Route = createFileRoute("/superior/timeline")({ component: Page });

function Page() {
  const [events, setEvents] = useState(MOCK_TIMELINE);
  const [title, setTitle] = useState("");
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Timeline" }]} title="Timeline" subtitle="Chronological investigation events">
      <Panel title="Add manual event">
        <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); if (!title.trim()) return; setEvents((prev) => [...prev, { id: `tl-${Date.now()}`, title, detail: "Manual entry", at: new Date().toISOString().slice(0, 16).replace("T", " "), type: "manual" }]); setTitle(""); }}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Event title" className="flex-1 rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <PrimaryButton type="submit">Add</PrimaryButton>
        </form>
      </Panel>
      <ol className="mt-4 space-y-4">{events.map((t) => <li key={t.id} className="relative border-l border-white/15 pl-4"><span className="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-cyan" /><p className="text-sm font-medium text-slate-100">{t.title}</p><p className="text-xs text-slate-500">{t.at}</p><p className="text-sm text-slate-400">{t.detail}</p></li>)}</ol>
    </PageScaffold>
  );
}
''',
)

w(
    "superior/relationships.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_RELATIONSHIPS } from "@/data/mock/platform";
import { PageScaffold, PrimaryButton, Panel } from "@/components/ui-kit/PageKit";
import { RelationshipCard } from "@/components/ui-kit/Cards";
import { useState } from "react";

export const Route = createFileRoute("/superior/relationships")({ component: Page });

function Page() {
  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  const [items, setItems] = useState(MOCK_RELATIONSHIPS);
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Relationship Map" }]} title="Relationship Map" subtitle="Manual entity links (AI later)">
      <Panel title="Add relationship">
        <form className="grid gap-2 sm:grid-cols-[1fr_auto_1fr_auto]" onSubmit={(e) => { e.preventDefault(); if (!source || !target) return; setItems((p) => [...p, { id: `r${Date.now()}`, source, target, type: "Manual" }]); setSource(""); setTarget(""); }}>
          <input value={source} onChange={(e) => setSource(e.target.value)} placeholder="Source" className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <span className="grid place-items-center text-slate-500">→</span>
          <input value={target} onChange={(e) => setTarget(e.target.value)} placeholder="Target" className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <PrimaryButton type="submit">Link</PrimaryButton>
        </form>
      </Panel>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">{items.map((r) => <RelationshipCard key={r.id} source={r.source} target={r.target} type={r.type} />)}</div>
    </PageScaffold>
  );
}
''',
)

w(
    "superior/leads.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_LEADS } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, PrimaryButton, StatusPill, Toolbar, useClientTable, Panel } from "@/components/ui-kit/PageKit";
import { useState } from "react";

export const Route = createFileRoute("/superior/leads")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_LEADS);
  const [title, setTitle] = useState("");
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Manual Leads" }]} title="Manual Leads" subtitle="No AI generation — investigator-created leads">
      <Panel title="New lead">
        <form className="flex gap-2" onSubmit={(e) => e.preventDefault()}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Lead title" className="flex-1 rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <PrimaryButton type="submit">Create</PrimaryButton>
        </form>
      </Panel>
      <div className="mt-4" />
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "t", header: "Title", render: (r) => r.title },
        { key: "c", header: "Case", render: (r) => <span className="text-cyan">{r.caseNumber}</span> },
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
    "superior/reports.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_REPORTS, MOCK_CASES } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, Toolbar, useClientTable, Pagination } from "@/components/ui-kit/PageKit";
import { ReportCard } from "@/components/ui-kit/Cards";
import { useState } from "react";

export const Route = createFileRoute("/superior/reports")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_REPORTS);
  const [preview, setPreview] = useState(false);
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Reports" }]} title="Reports" subtitle="Generate, preview, print">
      <Panel title="Generate report">
        <form className="flex flex-wrap gap-2" onSubmit={(e) => { e.preventDefault(); setPreview(true); }}>
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{MOCK_CASES.map((c) => <option key={c.id}>{c.caseNumber}</option>)}</select>
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>HTML</option><option>PDF</option><option>CSV</option></select>
          <PrimaryButton type="submit">Generate</PrimaryButton>
        </form>
      </Panel>
      {preview && <Panel title="Report preview" className="mt-4"><p className="text-sm text-slate-300">Investigation Summary — mock content suitable for print/PDF export.</p><div className="mt-3 flex gap-2"><PrimaryButton onClick={() => window.print()}>Print / PDF</PrimaryButton></div></Panel>}
      <div className="mt-4" /><Toolbar search={table.search} onSearch={table.setSearch} />
      <div className="grid gap-3 sm:grid-cols-2">{table.rows.map((r) => <ReportCard key={r.id} {...r} />)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "superior/tasks.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_TASKS } from "@/data/mock/platform";
import { PageScaffold, Toolbar, useClientTable, Pagination } from "@/components/ui-kit/PageKit";
import { TaskCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/superior/tasks")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_TASKS);
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Tasks" }]} title="Tasks" subtitle="Investigation follow-ups">
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{table.rows.map((t) => <TaskCard key={t.id} item={t} />)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "superior/investigators.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_USERS } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/investigators")({ component: Page });

function Page() {
  const rows = MOCK_USERS.filter((u) => u.role === "Investigator");
  const table = useClientTable(rows);
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Investigators" }]} title="Investigators" subtitle="Team available for assignment">
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
    "superior/analytics.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { Area, AreaChart, CartesianGrid, Pie, PieChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard, PageScaffold } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/analytics")({ component: Page });

const progress = [{ m: "W1", v: 4 }, { m: "W2", v: 7 }, { m: "W3", v: 6 }, { m: "W4", v: 9 }];
const priority = [{ name: "Critical", value: 2 }, { name: "High", value: 5 }, { name: "Medium", value: 8 }, { name: "Low", value: 3 }];
const COLORS = ["#EF4444", "#F59E0B", "#3B82F6", "#64748b"];

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Investigation Analytics" }]} title="Investigation Analytics" subtitle="Progress and priority (mock)">
      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Timeline activity"><div className="h-56"><ResponsiveContainer width="100%" height="100%"><AreaChart data={progress}><CartesianGrid strokeDasharray="3 3" stroke="#1f2937" /><XAxis dataKey="m" stroke="#64748b" fontSize={11} /><YAxis stroke="#64748b" fontSize={11} /><Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} /><Area type="monotone" dataKey="v" stroke="#06B6D4" fill="#06B6D433" /></AreaChart></ResponsiveContainer></div></ChartCard>
        <ChartCard title="Priority distribution"><div className="h-56"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={priority} dataKey="value" nameKey="name" outerRadius={80}>{priority.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}</Pie><Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} /></PieChart></ResponsiveContainer></div></ChartCard>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "superior/settings.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/settings")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Settings" }]} title="Settings" subtitle="Preferences">
      <Panel title="Account"><label className="block text-xs text-slate-400">Display name<input defaultValue="Ravi Menon" className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" /></label><PrimaryButton className="mt-4">Save</PrimaryButton></Panel>
    </PageScaffold>
  );
}
''',
)

print("superior done")
