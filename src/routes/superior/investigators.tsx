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
