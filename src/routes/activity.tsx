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
