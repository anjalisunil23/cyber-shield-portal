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
