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
