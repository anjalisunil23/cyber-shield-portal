"""Investigator + common mock UI pages."""
from pathlib import Path

ROOT = Path(r"d:/cybershield/cyber-shield-portal/src/routes")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print(rel)


w(
    "investigator/cases.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, StatusPill, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/cases")({ component: Page });

function Page() {
  const mine = MOCK_CASES.filter((c) => c.assignee === "Alex Mercer" || c.assignee === "Sana Joseph");
  const table = useClientTable(mine.length ? mine : MOCK_CASES);
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "My Cases" }]} title="My Cases" subtitle="Cases assigned to you">
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "c", header: "Case", render: (r) => <Link to={"/investigator/cases/$caseId" as "/"} params={{ caseId: r.id } as never} className="text-cyan hover:underline">{r.caseNumber}</Link> },
        { key: "t", header: "Title", render: (r) => r.title },
        { key: "p", header: "Priority", render: (r) => <StatusPill value={r.priority} /> },
        { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
        { key: "u", header: "Updated", render: (r) => r.updated },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/cases.$caseId.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_EVIDENCE, MOCK_NOTES, MOCK_TIMELINE } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/cases/$caseId")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const c = MOCK_CASES.find((x) => x.id === caseId) || MOCK_CASES[0];
  return (
    <PageScaffold crumbs={[{ label: "My Cases", to: "/investigator/cases" }, { label: c.caseNumber }]} title={c.title} subtitle={c.description} actions={<Link to={"/investigator/upload" as "/"}><PrimaryButton>Upload evidence</PrimaryButton></Link>}>
      <div className="mb-4 flex gap-2"><StatusPill value={c.priority} /><StatusPill value={c.status} /></div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Evidence">{MOCK_EVIDENCE.filter((e) => e.caseNumber === c.caseNumber).map((e) => <Link key={e.id} to={"/investigator/evidence/$evidenceId" as "/"} params={{ evidenceId: e.id } as never} className="block text-sm text-cyan hover:underline">{e.name}</Link>)}</Panel>
        <Panel title="Notes">{MOCK_NOTES.filter((n) => n.caseNumber === c.caseNumber).map((n) => <div key={n.id} className="mb-2 text-sm"><p className="font-medium text-slate-100">{n.title}</p><p className="text-slate-500">{n.body}</p></div>)}</Panel>
        <Panel title="Timeline" className="lg:col-span-2"><ol className="space-y-3">{MOCK_TIMELINE.map((t) => <li key={t.id} className="border-l border-cyan/40 pl-3"><p className="text-sm text-slate-100">{t.title}</p><p className="text-xs text-slate-500">{t.at}</p></li>)}</ol></Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/upload.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { Upload } from "lucide-react";
import { useState } from "react";
import { MOCK_CASES } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/upload")({ component: Page });

function Page() {
  const [files, setFiles] = useState<string[]>([]);
  const [drag, setDrag] = useState(false);
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Upload Evidence" }]} title="Upload Evidence" subtitle="Drag & drop or browse files">
      <Panel>
        <label className="mb-3 block text-xs text-slate-400">Case
          <select className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{MOCK_CASES.map((c) => <option key={c.id}>{c.caseNumber} — {c.title}</option>)}</select>
        </label>
        <div
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => { e.preventDefault(); setDrag(false); const names = Array.from(e.dataTransfer.files).map((f) => f.name); setFiles((p) => [...p, ...names]); }}
          className={`grid place-items-center rounded-2xl border border-dashed px-6 py-16 text-center transition ${drag ? "border-cyan bg-cyan/10" : "border-white/15 bg-black/20"}`}
        >
          <Upload className="mb-3 h-10 w-10 text-cyan" />
          <p className="text-sm text-slate-200">Drop evidence files here</p>
          <p className="mt-1 text-xs text-slate-500">Images, video, audio, PDF, documents, exports</p>
          <label className="mt-4 inline-flex cursor-pointer rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white">
            Browse files
            <input type="file" multiple className="hidden" onChange={(e) => setFiles((p) => [...p, ...Array.from(e.target.files || []).map((f) => f.name)])} />
          </label>
        </div>
        {!!files.length && <ul className="mt-4 space-y-2">{files.map((f) => <li key={f} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300">{f}</li>)}</ul>}
        <PrimaryButton className="mt-4" onClick={() => setFiles([])}>Upload (UI mock)</PrimaryButton>
      </Panel>
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/evidence.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { MOCK_EVIDENCE } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, SelectFilter, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";
import { EvidenceCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/investigator/evidence")({ component: Page });

function Page() {
  const [view, setView] = useState<"grid" | "table">("grid");
  const [type, setType] = useState("All");
  const items = MOCK_EVIDENCE.filter((e) => type === "All" || e.type === type);
  const table = useClientTable(items, 6);
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Evidence Repository" }]} title="Evidence Repository" subtitle="Search, filter, and open evidence">
      <Toolbar search={table.search} onSearch={table.setSearch} filters={<><SelectFilter value={type} onChange={setType} options={["All", "image", "video", "audio", "pdf", "document"]} /><button type="button" className="rounded-xl border border-white/10 px-3 py-2 text-xs" onClick={() => setView(view === "grid" ? "table" : "grid")}>{view === "grid" ? "Table" : "Gallery"}</button></>} />
      {view === "grid" ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{table.rows.map((e) => <Link key={e.id} to={"/investigator/evidence/$evidenceId" as "/"} params={{ evidenceId: e.id } as never}><EvidenceCard item={e} /></Link>)}</div>
      ) : (
        <DataTable rows={table.rows} columns={[
          { key: "n", header: "File", render: (r) => <Link to={"/investigator/evidence/$evidenceId" as "/"} params={{ evidenceId: r.id } as never} className="text-cyan">{r.name}</Link> },
          { key: "t", header: "Type", render: (r) => r.type },
          { key: "c", header: "Case", render: (r) => r.caseNumber },
          { key: "s", header: "Size", render: (r) => r.size },
          { key: "d", header: "Uploaded", render: (r) => r.uploadedAt },
        ]} />
      )}
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/evidence.$evidenceId.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_EVIDENCE } from "@/data/mock/platform";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/evidence/$evidenceId")({ component: Page });

function Page() {
  const { evidenceId } = Route.useParams();
  const e = MOCK_EVIDENCE.find((x) => x.id === evidenceId) || MOCK_EVIDENCE[0];
  return (
    <PageScaffold crumbs={[{ label: "Repository", to: "/investigator/evidence" }, { label: e.name }]} title="Evidence Viewer" subtitle={e.name}>
      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Preview" className="lg:col-span-2"><div className="grid h-72 place-items-center rounded-xl bg-black/40 text-slate-500">{e.type.toUpperCase()} viewer mock</div></Panel>
        <Panel title="Details">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-slate-500">Case</dt><dd className="text-cyan">{e.caseNumber}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Size</dt><dd>{e.size}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">SHA256</dt><dd className="font-mono text-[10px]">{e.sha256}</dd></div>
          </dl>
          <div className="mt-3 flex flex-wrap gap-1">{e.tags.map((t) => <StatusPill key={t} value={t} />)}</div>
        </Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/notes.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_NOTES } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, Toolbar, useClientTable, Pagination } from "@/components/ui-kit/PageKit";
import { useState } from "react";
import { Pin } from "lucide-react";

export const Route = createFileRoute("/investigator/notes")({ component: Page });

function Page() {
  const [notes, setNotes] = useState(MOCK_NOTES);
  const table = useClientTable(notes);
  const [body, setBody] = useState("");
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Notes" }]} title="Notes" subtitle="Markdown-friendly investigation notes">
      <Panel title="Add note">
        <form className="space-y-2" onSubmit={(e) => { e.preventDefault(); if (!body.trim()) return; setNotes((p) => [{ id: `n${Date.now()}`, title: "Note", body, caseNumber: "CS-2026-0142", author: "You", pinned: false, updatedAt: "Today" }, ...p]); setBody(""); }}>
          <textarea value={body} onChange={(e) => setBody(e.target.value)} rows={3} placeholder="Write a note…" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <PrimaryButton type="submit">Save note</PrimaryButton>
        </form>
      </Panel>
      <div className="mt-4" /><Toolbar search={table.search} onSearch={table.setSearch} />
      <div className="space-y-3">{table.rows.map((n) => <div key={n.id} className="rounded-2xl border border-white/10 bg-[#111827]/90 p-4"><div className="mb-2 flex items-center justify-between text-xs text-slate-500"><span>{n.author} · {n.caseNumber} · {n.updatedAt}</span>{n.pinned && <Pin className="h-3.5 w-3.5 text-cyan" />}</div><p className="text-sm font-medium text-slate-100">{n.title}</p><pre className="mt-1 whitespace-pre-wrap font-sans text-sm text-slate-400">{n.body}</pre></div>)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/timeline.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_TIMELINE } from "@/data/mock/platform";
import { PageScaffold } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/timeline")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Timeline" }]} title="Timeline" subtitle="Case chronology">
      <ol className="space-y-4">{MOCK_TIMELINE.map((t) => <li key={t.id} className="relative border-l border-white/15 pl-4"><span className="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-primary" /><p className="text-sm font-medium text-slate-100">{t.title}</p><p className="text-xs text-slate-500">{t.at}</p><p className="text-sm text-slate-400">{t.detail}</p></li>)}</ol>
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/leads.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_LEADS } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, PrimaryButton, StatusPill, Toolbar, useClientTable, Panel } from "@/components/ui-kit/PageKit";
import { useState } from "react";

export const Route = createFileRoute("/investigator/leads")({ component: Page });

function Page() {
  const [items, setItems] = useState(MOCK_LEADS);
  const table = useClientTable(items);
  const [title, setTitle] = useState("");
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Manual Leads" }]} title="Manual Leads" subtitle="Track investigative threads">
      <Panel>
        <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); if (!title.trim()) return; setItems((p) => [{ id: `l${Date.now()}`, title, priority: "Medium", status: "Open", caseNumber: "CS-2026-0142", assignee: "You" }, ...p]); setTitle(""); }}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="New lead" className="flex-1 rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <PrimaryButton type="submit">Create</PrimaryButton>
        </form>
      </Panel>
      <div className="mt-4" /><Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "t", header: "Title", render: (r) => r.title },
        { key: "c", header: "Case", render: (r) => r.caseNumber },
        { key: "p", header: "Priority", render: (r) => <StatusPill value={r.priority} /> },
        { key: "s", header: "Status", render: (r) => <StatusPill value={r.status} /> },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/reports.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_REPORTS } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, Toolbar, useClientTable, Pagination } from "@/components/ui-kit/PageKit";
import { ReportCard } from "@/components/ui-kit/Cards";
import { useState } from "react";

export const Route = createFileRoute("/investigator/reports")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_REPORTS);
  const [draft, setDraft] = useState(false);
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Generate Report" }]} title="Generate Report" subtitle="Draft investigation summaries">
      <Panel title="New draft">
        <form className="flex flex-wrap gap-2" onSubmit={(e) => { e.preventDefault(); setDraft(true); }}>
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{MOCK_CASES.map((c) => <option key={c.id}>{c.caseNumber}</option>)}</select>
          <PrimaryButton type="submit">Generate draft</PrimaryButton>
        </form>
      </Panel>
      {draft && <Panel title="Draft preview" className="mt-4"><p className="text-sm text-slate-300">Draft report body (mock). Ready for superior review.</p><PrimaryButton className="mt-3" onClick={() => window.print()}>Print view</PrimaryButton></Panel>}
      <div className="mt-4" /><Toolbar search={table.search} onSearch={table.setSearch} />
      <div className="grid gap-3 sm:grid-cols-2">{table.rows.map((r) => <ReportCard key={r.id} {...r} />)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/tasks.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_TASKS } from "@/data/mock/platform";
import { PageScaffold, Toolbar, useClientTable, Pagination } from "@/components/ui-kit/PageKit";
import { TaskCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/investigator/tasks")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_TASKS);
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Tasks" }]} title="Tasks" subtitle="Pending investigative work">
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{table.rows.map((t) => <TaskCard key={t.id} item={t} />)}</div>
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

w(
    "investigator/settings.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/settings")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Settings" }]} title="Settings" subtitle="Account & notifications" actions={<Link to={"/profile" as "/"} className="text-sm text-cyan">Open profile →</Link>}>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="General"><input defaultValue="Alex Mercer" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" /><PrimaryButton className="mt-3">Save</PrimaryButton></Panel>
        <Panel title="Notifications"><label className="flex justify-between text-sm"><span>Evidence alerts</span><input type="checkbox" defaultChecked className="accent-cyan" /></label></Panel>
        <Panel title="Theme"><label className="flex justify-between text-sm"><span>Dark mode</span><input type="checkbox" defaultChecked className="accent-cyan" /></label></Panel>
        <Panel title="Security"><Link to={"/profile/security" as "/"} className="text-sm text-cyan">Change password →</Link></Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

# Common pages
w(
    "profile.tsx",
    '''
import { createFileRoute, Link, Outlet } from "@tanstack/react-router";
import { ProfileCard } from "@/components/ui-kit/Cards";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/profile")({ component: Page });

function Page() {
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100 sm:px-8">
      <div className="mx-auto max-w-4xl">
        <PageScaffold crumbs={[{ label: "Home", to: "/" }, { label: "Profile" }]} title="User Profile" subtitle="View and edit your account" actions={<Link to={"/profile/edit" as "/"} className="text-sm text-cyan">Edit profile</Link>}>
          <ProfileCard name="Alex Mercer" email="alex.mercer@agency.gov" role="Investigator" department="Cyber Crime Unit" />
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Panel title="Quick links"><ul className="space-y-2 text-sm"><li><Link to={"/profile/edit" as "/"} className="text-cyan">Edit profile</Link></li><li><Link to={"/profile/security" as "/"} className="text-cyan">Change password</Link></li><li><Link to={"/notifications" as "/"} className="text-cyan">Notifications</Link></li></ul></Panel>
            <Panel title="Session"><p className="text-sm text-slate-400">Signed in · mock session</p><PrimaryButton className="mt-3">Sign out UI</PrimaryButton></Panel>
          </div>
          <Outlet />
        </PageScaffold>
      </div>
    </div>
  );
}
''',
)

w(
    "profile.edit.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/profile/edit")({ component: Page });

function Page() {
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-xl">
        <PageScaffold crumbs={[{ label: "Profile", to: "/profile" }, { label: "Edit" }]} title="Edit Profile" actions={<Link to={"/profile" as "/"}><GhostButton>Cancel</GhostButton></Link>}>
          <Panel>
            <form className="space-y-3" onSubmit={(e) => e.preventDefault()}>
              <input defaultValue="Alex Mercer" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
              <input defaultValue="Cyber Crime Unit" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
              <input defaultValue="+91 98765 11103" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
              <PrimaryButton type="submit">Save</PrimaryButton>
            </form>
          </Panel>
        </PageScaffold>
      </div>
    </div>
  );
}
''',
)

w(
    "profile.security.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/profile/security")({ component: Page });

function Page() {
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-xl">
        <PageScaffold crumbs={[{ label: "Profile", to: "/profile" }, { label: "Security" }]} title="Change Password" actions={<Link to={"/profile" as "/"}><GhostButton>Back</GhostButton></Link>}>
          <Panel>
            <form className="space-y-3" onSubmit={(e) => e.preventDefault()}>
              <input type="password" placeholder="Current password" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
              <input type="password" placeholder="New password" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
              <input type="password" placeholder="Confirm password" className="w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
              <PrimaryButton type="submit">Update password</PrimaryButton>
            </form>
          </Panel>
        </PageScaffold>
      </div>
    </div>
  );
}
''',
)

w(
    "notifications.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { MOCK_NOTIFICATIONS } from "@/data/mock/platform";
import { PageScaffold, GhostButton, SelectFilter } from "@/components/ui-kit/PageKit";
import { NotificationCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/notifications")({ component: Page });

function Page() {
  const [items, setItems] = useState(MOCK_NOTIFICATIONS);
  const [filter, setFilter] = useState("All");
  const shown = items.filter((n) => filter === "All" || (filter === "Unread" ? !n.read : n.read));
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-3xl">
        <PageScaffold crumbs={[{ label: "App" }, { label: "Notifications" }]} title="Notification Center" subtitle="Alerts and unread items" actions={<GhostButton onClick={() => setItems((p) => p.map((n) => ({ ...n, read: true })))}>Mark all read</GhostButton>}>
          <div className="mb-4"><SelectFilter value={filter} onChange={setFilter} options={["All", "Unread", "Read"]} /></div>
          <div className="space-y-2">{shown.map((n) => <NotificationCard key={n.id} item={n} />)}</div>
        </PageScaffold>
      </div>
    </div>
  );
}
''',
)

w(
    "help.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { PageScaffold, Panel } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/help")({ component: Page });

const FAQS = [
  ["How do I upload evidence?", "Open Upload Evidence, select a case, then drag files into the dropzone."],
  ["Who can create admins?", "Only Major Admin can create Admin accounts."],
  ["Are AI features available?", "Not in Phase 1 — placeholders are shown across dashboards."],
];

function Page() {
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-3xl">
        <PageScaffold crumbs={[{ label: "App" }, { label: "Help Center" }]} title="Help Center" subtitle="Guides for investigators and admins">
          <div className="space-y-3">{FAQS.map(([q, a]) => <Panel key={q} title={q}><p className="text-sm text-slate-400">{a}</p></Panel>)}</div>
        </PageScaffold>
      </div>
    </div>
  );
}
''',
)

w(
    "search.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { MOCK_CASES, MOCK_EVIDENCE, MOCK_USERS, MOCK_NOTES } from "@/data/mock/platform";
import { PageScaffold, Panel, Toolbar } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/search")({ component: Page });

function Page() {
  const [q, setQ] = useState("phishing");
  const query = q.trim().toLowerCase();
  const results = useMemo(() => ({
    cases: MOCK_CASES.filter((c) => JSON.stringify(c).toLowerCase().includes(query)),
    evidence: MOCK_EVIDENCE.filter((e) => JSON.stringify(e).toLowerCase().includes(query)),
    notes: MOCK_NOTES.filter((n) => JSON.stringify(n).toLowerCase().includes(query)),
    users: MOCK_USERS.filter((u) => JSON.stringify(u).toLowerCase().includes(query)),
  }), [query]);
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-4xl">
        <PageScaffold crumbs={[{ label: "App" }, { label: "Global Search" }]} title="Global Search" subtitle="Cases, evidence, notes, investigators">
          <Toolbar search={q} onSearch={setQ} placeholder="Search everything…" />
          <div className="grid gap-4 md:grid-cols-2">
            <Panel title={`Cases (${results.cases.length})`}><ul className="space-y-1 text-sm">{results.cases.map((c) => <li key={c.id} className="text-slate-300">{c.caseNumber} — {c.title}</li>)}</ul></Panel>
            <Panel title={`Evidence (${results.evidence.length})`}><ul className="space-y-1 text-sm">{results.evidence.map((e) => <li key={e.id}>{e.name}</li>)}</ul></Panel>
            <Panel title={`Notes (${results.notes.length})`}><ul className="space-y-1 text-sm">{results.notes.map((n) => <li key={n.id}>{n.title}</li>)}</ul></Panel>
            <Panel title={`People (${results.users.length})`}><ul className="space-y-1 text-sm">{results.users.map((u) => <li key={u.id}>{u.name}</li>)}</ul></Panel>
          </div>
        </PageScaffold>
      </div>
    </div>
  );
}
''',
)

w(
    "activity.tsx",
    '''
import { createFileRoute } from "@tanstack/react-router";
import { MOCK_AUDIT } from "@/data/mock/platform";
import { DataTable, PageScaffold, Pagination, Toolbar, useClientTable } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/activity")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_AUDIT);
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <PageScaffold crumbs={[{ label: "App" }, { label: "Activity Logs" }]} title="Activity Logs" subtitle="Recent platform activity (mock)">
          <Toolbar search={table.search} onSearch={table.setSearch} />
          <DataTable rows={table.rows} columns={[
            { key: "a", header: "Action", render: (r) => <span className="text-cyan">{r.action}</span> },
            { key: "u", header: "Actor", render: (r) => r.actor },
            { key: "r", header: "Resource", render: (r) => r.resource },
            { key: "t", header: "Time", render: (r) => r.time },
          ]} />
          <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
        </PageScaffold>
      </div>
    </div>
  );
}
''',
)

w(
    "unauthorized.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { ShieldAlert } from "lucide-react";
import { PrimaryButton, GhostButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/unauthorized")({ component: Page });

function Page() {
  return (
    <div className="grid min-h-screen place-items-center bg-[#020617] px-4 text-center text-slate-100">
      <div>
        <ShieldAlert className="mx-auto mb-4 h-12 w-12 text-amber-400" />
        <h1 className="text-3xl font-bold">403 — Unauthorized</h1>
        <p className="mt-2 text-sm text-slate-400">You do not have permission to view this workspace.</p>
        <div className="mt-6 flex justify-center gap-2"><Link to={"/login" as "/"}><PrimaryButton>Login</PrimaryButton></Link><Link to={"/" as "/"}><GhostButton>Home</GhostButton></Link></div>
      </div>
    </div>
  );
}
''',
)

w(
    "reset-password.tsx",
    '''
import { createFileRoute, Link } from "@tanstack/react-router";
import { HudAuthCard, HudShell, hudInput } from "@/components/HudShell";
import { Shield } from "lucide-react";

export const Route = createFileRoute("/reset-password")({ component: Page });

function Page() {
  return (
    <HudShell>
      <div className="mx-auto flex min-h-screen max-w-md items-center px-5 py-10">
        <div className="w-full">
          <Link to="/" className="mb-8 inline-flex items-center gap-2 text-white/80"><Shield className="h-5 w-5" /><span className="text-sm font-semibold">Cyber Shield</span></Link>
          <HudAuthCard>
            <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
              <h1 className="text-lg font-semibold text-white">Reset password</h1>
              <input placeholder="Reset token" className={`${hudInput} w-full rounded-md bg-[#2a3340] px-3 py-3`} />
              <input type="password" placeholder="New password" className={`${hudInput} w-full rounded-md bg-[#2a3340] px-3 py-3`} />
              <input type="password" placeholder="Confirm password" className={`${hudInput} w-full rounded-md bg-[#2a3340] px-3 py-3`} />
              <button type="submit" className="w-full rounded-md bg-white py-3 text-sm font-bold text-[#0b1220]">Update password</button>
              <Link to="/login" className="block text-center text-sm text-white/70 hover:underline">Back to login</Link>
            </form>
          </HudAuthCard>
        </div>
      </div>
    </HudShell>
  );
}
''',
)

print("investigator + common done")
