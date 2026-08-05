"""Generate CyberShield mock UI route pages (no backend)."""
from pathlib import Path

ROOT = Path(r"d:/cybershield/cyber-shield-portal/src/routes")

COMMON_IMPORTS = '''import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Plus } from "lucide-react";
import {
  Breadcrumb,
  DataTable,
  EmptyState,
  GhostButton,
  Modal,
  PageScaffold,
  Pagination,
  PrimaryButton,
  SelectFilter,
  StatusPill,
  Toolbar,
  useClientTable,
  Panel,
} from "@/components/ui-kit/PageKit";
import { CaseCard, EvidenceCard, NotificationCard, ProfileCard, RelationshipCard, ReportCard, TaskCard } from "@/components/ui-kit/Cards";
'''


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)


# ---------- Major Admin pages ----------

write(
    "major-admin/admins.tsx",
    COMMON_IMPORTS
    + '''
import { MOCK_USERS } from "@/data/mock/platform";

export const Route = createFileRoute("/major-admin/admins")({ component: Page });

function Page() {
  const admins = MOCK_USERS.filter((u) => u.role === "Admin" || u.role === "Major Admin");
  const table = useClientTable(admins);
  const [open, setOpen] = useState(false);
  return (
    <PageScaffold
      crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Admins" }]}
      title="Admins"
      subtitle="Create, edit, and suspend Admin accounts"
      actions={<PrimaryButton onClick={() => setOpen(true)}><Plus className="mr-1 inline h-4 w-4" /> Create Admin</PrimaryButton>}
    >
      <Toolbar search={table.search} onSearch={table.setSearch} placeholder="Search admins…" actions={<Link to={"/major-admin/admins/create" as "/"}><GhostButton>Full create form</GhostButton></Link>} />
      <DataTable
        rows={table.rows}
        columns={[
          { key: "name", header: "Name", render: (r) => <span className="font-medium text-slate-100">{r.name}</span> },
          { key: "email", header: "Email", render: (r) => r.email },
          { key: "dept", header: "Department", render: (r) => r.department },
          { key: "status", header: "Status", render: (r) => <StatusPill value={r.status} /> },
          { key: "login", header: "Last login", render: (r) => r.lastLogin },
          { key: "actions", header: "", render: (r) => <Link to={"/major-admin/admins/$adminId/edit" as "/"} params={{ adminId: r.id } as never} className="text-xs text-cyan hover:underline">Edit</Link> },
        ]}
      />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
      <Modal open={open} title="Quick create Admin" onClose={() => setOpen(false)}>
        <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); setOpen(false); }}>
          <input required placeholder="Full name" className="w-full rounded-xl border border-white/10 bg-[#111827] px-3 py-2 text-sm" />
          <input required type="email" placeholder="Email" className="w-full rounded-xl border border-white/10 bg-[#111827] px-3 py-2 text-sm" />
          <input placeholder="Department" className="w-full rounded-xl border border-white/10 bg-[#111827] px-3 py-2 text-sm" />
          <PrimaryButton type="submit" className="w-full">Save (UI only)</PrimaryButton>
        </form>
      </Modal>
    </PageScaffold>
  );
}
''',
)

write(
    "major-admin/admins.create.tsx",
    '''import { createFileRoute, Link } from "@tanstack/react-router";
import { PageScaffold, PrimaryButton, GhostButton, Panel } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/admins/create")({ component: Page });

function Page() {
  return (
    <PageScaffold
      crumbs={[{ label: "Admins", to: "/major-admin/admins" }, { label: "Create" }]}
      title="Create Admin"
      subtitle="Provision a new organization Admin"
      actions={<Link to={"/major-admin/admins" as "/"}><GhostButton>Cancel</GhostButton></Link>}
    >
      <Panel>
        <form className="mx-auto grid max-w-2xl gap-4" onSubmit={(e) => e.preventDefault()}>
          {["Full name", "Email", "Phone", "Department", "Temporary password"].map((label) => (
            <label key={label} className="block text-xs text-slate-400">
              {label}
              <input className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm text-slate-100" />
            </label>
          ))}
          <PrimaryButton type="submit">Create Admin (UI)</PrimaryButton>
        </form>
      </Panel>
    </PageScaffold>
  );
}
''',
)

write(
    "major-admin/admins.$adminId.edit.tsx",
    '''import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_USERS } from "@/data/mock/platform";
import { PageScaffold, PrimaryButton, GhostButton, Panel, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/admins/$adminId/edit")({ component: Page });

function Page() {
  const { adminId } = Route.useParams();
  const user = MOCK_USERS.find((u) => u.id === adminId) || MOCK_USERS[0];
  return (
    <PageScaffold
      crumbs={[{ label: "Admins", to: "/major-admin/admins" }, { label: "Edit" }]}
      title={`Edit ${user.name}`}
      subtitle={user.email}
      actions={<StatusPill value={user.status} />}
    >
      <Panel>
        <form className="mx-auto grid max-w-2xl gap-4" onSubmit={(e) => e.preventDefault()}>
          <label className="text-xs text-slate-400">Full name<input defaultValue={user.name} className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" /></label>
          <label className="text-xs text-slate-400">Department<input defaultValue={user.department} className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" /></label>
          <label className="text-xs text-slate-400">Status
            <select defaultValue={user.status} className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">
              <option>Active</option><option>Suspended</option>
            </select>
          </label>
          <div className="flex gap-2">
            <PrimaryButton type="submit">Save changes</PrimaryButton>
            <Link to={"/major-admin/admins" as "/"}><GhostButton>Back</GhostButton></Link>
          </div>
        </form>
      </Panel>
    </PageScaffold>
  );
}
''',
)

# Continue generating in same script - departments, users, etc.
PAGES = []

# major-admin departments
write(
    "major-admin/departments.tsx",
    '''import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_DEPARTMENTS } from "@/data/mock/platform";
import { PageScaffold, Toolbar, useClientTable, Pagination, PrimaryButton, DataTable, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/departments")({ component: Page });

function Page() {
  const table = useClientTable(MOCK_DEPARTMENTS);
  return (
    <PageScaffold crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Departments" }]} title="Departments" subtitle="Investigation units across the platform" actions={<PrimaryButton>Add department</PrimaryButton>}>
      <Toolbar search={table.search} onSearch={table.setSearch} />
      <DataTable rows={table.rows} columns={[
        { key: "name", header: "Name", render: (r) => <Link to={"/major-admin/departments/$deptId" as "/"} params={{ deptId: r.id } as never} className="font-medium text-cyan hover:underline">{r.name}</Link> },
        { key: "code", header: "Code", render: (r) => r.code },
        { key: "officers", header: "Officers", render: (r) => r.officers },
        { key: "cases", header: "Cases", render: (r) => r.cases },
        { key: "status", header: "Status", render: (r) => <StatusPill value={r.status} /> },
      ]} />
      <Pagination page={table.page} pages={table.pages} onPage={table.setPage} />
    </PageScaffold>
  );
}
''',
)

write(
    "major-admin/departments.$deptId.tsx",
    '''import { createFileRoute } from "@tanstack/react-router";
import { MOCK_DEPARTMENTS, MOCK_USERS, MOCK_CASES } from "@/data/mock/platform";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/departments/$deptId")({ component: Page });

function Page() {
  const { deptId } = Route.useParams();
  const dept = MOCK_DEPARTMENTS.find((d) => d.id === deptId) || MOCK_DEPARTMENTS[0];
  return (
    <PageScaffold crumbs={[{ label: "Departments", to: "/major-admin/departments" }, { label: dept.name }]} title={dept.name} subtitle={dept.description} actions={<StatusPill value={dept.status} />}>
      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Overview"><dl className="space-y-2 text-sm"><div className="flex justify-between"><dt className="text-slate-500">Code</dt><dd>{dept.code}</dd></div><div className="flex justify-between"><dt className="text-slate-500">Officers</dt><dd>{dept.officers}</dd></div><div className="flex justify-between"><dt className="text-slate-500">Cases</dt><dd>{dept.cases}</dd></div></dl></Panel>
        <Panel title="People" className="lg:col-span-2"><ul className="space-y-2">{MOCK_USERS.slice(0,4).map(u => <li key={u.id} className="flex justify-between text-sm"><span>{u.name}</span><span className="text-cyan text-xs">{u.role}</span></li>)}</ul></Panel>
        <Panel title="Recent cases" className="lg:col-span-3"><ul className="space-y-2">{MOCK_CASES.slice(0,4).map(c => <li key={c.id} className="text-sm text-slate-300">{c.caseNumber} — {c.title}</li>)}</ul></Panel>
      </div>
    </PageScaffold>
  );
}
''',
)

print("batch1 ok")
