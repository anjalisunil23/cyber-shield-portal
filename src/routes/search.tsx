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
