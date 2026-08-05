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
