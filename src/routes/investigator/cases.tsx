import { createFileRoute, Link } from "@tanstack/react-router";
import { useCallback, useEffect, useState } from "react";
import { InvestigationCaseCard } from "@/components/cyber/InvestigationCaseCard";
import {
  DataTable,
  EmptyState,
  LoadingBlock,
  PageScaffold,
  Pagination,
  StatusPill,
  Toolbar,
} from "@/components/ui-kit/PageKit";
import { investigationApi } from "@/services/investigationApi";
import type { InvestigationCase } from "@/services/types";
import { LayoutGrid, List, Shield } from "lucide-react";

export const Route = createFileRoute("/investigator/cases")({ component: Page });

function Page() {
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [view, setView] = useState<"grid" | "table">("grid");

  const loadCases = useCallback(async () => {
    setLoading(true);
    try {
      const me = await investigationApi.me().catch(() => null);
      if (me?.id) setCurrentUserId(me.id);

      const data = await investigationApi.listCases({
        page: 1,
        page_size: 100,
        q: searchQuery || undefined,
      });
      let allList = data?.items || [];

      if (searchQuery.trim()) {
        const qLower = searchQuery.toLowerCase().trim();
        allList = allList.filter(
          (c) =>
            c.case_number.toLowerCase().includes(qLower) ||
            c.title.toLowerCase().includes(qLower) ||
            (c.description && c.description.toLowerCase().includes(qLower)),
        );
      }

      allList.sort((a, b) => {
        const pOrder: Record<string, number> = { critical: 4, high: 3, medium: 2, low: 1 };
        const pDiff = (pOrder[b.priority] || 0) - (pOrder[a.priority] || 0);
        if (pDiff !== 0) return pDiff;
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      });

      const pageSize = 15;
      const totalPgs = Math.ceil(allList.length / pageSize) || 1;
      const pagedItems = allList.slice((page - 1) * pageSize, page * pageSize);

      setCases(pagedItems);
      setTotalPages(totalPgs);
    } catch {
      setCases([]);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  }, [page, searchQuery]);

  useEffect(() => {
    loadCases();
  }, [loadCases]);

  return (
    <PageScaffold
      crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Cases" }]}
      title="Cases"
    >
      <Toolbar
        search={searchQuery}
        onSearch={setSearchQuery}
        placeholder="Search cases"
        filters={
          <button
            type="button"
            onClick={() => setView(view === "table" ? "grid" : "table")}
            className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-border bg-card px-3 text-xs text-muted-foreground hover:text-foreground"
          >
            {view === "table" ? (
              <LayoutGrid className="h-3.5 w-3.5" />
            ) : (
              <List className="h-3.5 w-3.5" />
            )}
            {view === "table" ? "Cards" : "Table"}
          </button>
        }
      />
      {loading ? (
        <LoadingBlock rows={8} />
      ) : cases.length === 0 ? (
        <EmptyState title={searchQuery ? "No cases found." : "No cases assigned."} />
      ) : view === "grid" ? (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {cases.map((c) => (
              <InvestigationCaseCard
                key={c.id}
                item={c}
                to="/dashboard/cases/$caseId"
                leadName={
                  c.investigator_lead?.full_name ||
                  (c.investigator_lead_id === currentUserId ? "You" : undefined)
                }
              />
            ))}
          </div>
          <Pagination page={page} pages={totalPages} onPage={setPage} />
        </>
      ) : (
        <>
          <DataTable
            rows={cases}
            columns={[
              {
                key: "case_number",
                header: "Case",
                render: (r) => (
                  <Link
                    to="/dashboard/cases/$caseId"
                    params={{ caseId: r.id }}
                    className="font-medium text-primary hover:underline"
                  >
                    {r.case_number}
                  </Link>
                ),
              },
              {
                key: "title",
                header: "Title",
                render: (r) => <span className="font-medium text-foreground">{r.title}</span>,
              },
              {
                key: "lead",
                header: "Lead",
                render: (r) => {
                  const isLead = r.investigator_lead_id === currentUserId;
                  const leadName = r.investigator_lead?.full_name || (isLead ? "You" : "—");
                  return (
                    <span className="inline-flex items-center gap-1 text-xs text-foreground">
                      <Shield className="h-3 w-3 text-muted-foreground" />
                      {leadName}
                    </span>
                  );
                },
              },
              {
                key: "priority",
                header: "Priority",
                render: (r) => <StatusPill value={r.priority} />,
              },
              { key: "status", header: "Status", render: (r) => <StatusPill value={r.status} /> },
              {
                key: "updated_at",
                header: "Updated",
                render: (r) => new Date(r.updated_at).toLocaleDateString(),
              },
            ]}
          />
          <Pagination page={page} pages={totalPages} onPage={setPage} />
        </>
      )}
    </PageScaffold>
  );
}
