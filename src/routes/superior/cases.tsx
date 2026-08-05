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
