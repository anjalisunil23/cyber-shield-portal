import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AuthenticatedShell } from "@/components/layouts/AuthenticatedShell";
import { LoadingBlock, PageScaffold, Panel, Toolbar } from "@/components/ui-kit/PageKit";
import { investigationApi } from "@/services/investigationApi";
import type { SearchResult } from "@/services/types";

export const Route = createFileRoute("/search")({ component: Page });

function Page() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult>({
    cases: [],
    evidence: [],
    notes: [],
    investigators: [],
    reports: [],
  });

  const performSearch = async (query: string) => {
    if (!query.trim()) {
      setResults({ cases: [], evidence: [], notes: [], investigators: [], reports: [] });
      return;
    }
    setLoading(true);
    try {
      const data = await investigationApi.search(query);
      setResults(data);
    } catch {
      setResults({ cases: [], evidence: [], notes: [], investigators: [], reports: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(q);
    }, 400);
    return () => clearTimeout(timer);
  }, [q]);

  return (
    <AuthenticatedShell>
      <PageScaffold crumbs={[{ label: "Home", to: "/" }, { label: "Search" }]} title="Search">
        <Toolbar search={q} onSearch={setQ} placeholder="Search" />
        {loading ? (
          <LoadingBlock rows={6} />
        ) : (
          <div className="grid gap-4 md:grid-cols-2 mt-4">
            <Panel title={`Cases (${results.cases?.length || 0})`}>
              <ul className="space-y-1.5 text-sm">
                {(results.cases || []).map((c) => (
                  <li key={c.id} className="text-foreground border-b border-border/50 pb-1">
                    <span className="text-primary font-semibold text-xs mr-2">{c.case_number}</span>
                    {c.title}
                  </li>
                ))}
                {(!results.cases || results.cases.length === 0) && (
                  <span className="text-xs text-muted-foreground">No cases match</span>
                )}
              </ul>
            </Panel>
            <Panel title={`Evidence (${results.evidence?.length || 0})`}>
              <ul className="space-y-1.5 text-sm">
                {(results.evidence || []).map((e) => (
                  <li
                    key={e.id}
                    className="text-foreground border-b border-border/50 pb-1 flex justify-between"
                  >
                    <span>{e.original_name}</span>
                    <span className="text-xs text-muted-foreground uppercase">{e.file_type}</span>
                  </li>
                ))}
                {(!results.evidence || results.evidence.length === 0) && (
                  <span className="text-xs text-muted-foreground">No evidence matches</span>
                )}
              </ul>
            </Panel>
            <Panel title={`Notes (${results.notes?.length || 0})`}>
              <ul className="space-y-1.5 text-sm">
                {(results.notes || []).map((n) => (
                  <li key={n.id} className="text-foreground border-b border-border/50 pb-1">
                    <p className="font-semibold text-xs text-primary">{n.title || "Note"}</p>
                    <p className="text-xs text-muted-foreground truncate">{n.body}</p>
                  </li>
                ))}
                {(!results.notes || results.notes.length === 0) && (
                  <span className="text-xs text-muted-foreground">No notes match</span>
                )}
              </ul>
            </Panel>
            <Panel title={`Investigators (${results.investigators?.length || 0})`}>
              <ul className="space-y-1.5 text-sm">
                {(results.investigators || []).map((u) => (
                  <li
                    key={u.id}
                    className="text-foreground border-b border-border/50 pb-1 flex justify-between"
                  >
                    <span>{u.full_name}</span>
                    <span className="text-xs text-muted-foreground">{u.email}</span>
                  </li>
                ))}
                {(!results.investigators || results.investigators.length === 0) && (
                  <span className="text-xs text-muted-foreground">No investigators match</span>
                )}
              </ul>
            </Panel>
          </div>
        )}
      </PageScaffold>
    </AuthenticatedShell>
  );
}
