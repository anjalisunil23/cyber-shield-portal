import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useCallback, useEffect, useState } from "react";
import { InvestigationCaseCard } from "@/components/cyber/InvestigationCaseCard";
import {
  DataTable,
  EmptyState,
  LoadingBlock,
  PageScaffold,
  Pagination,
  PrimaryButton,
  SelectFilter,
  StatusPill,
  Toolbar,
} from "@/components/ui-kit/PageKit";
import { investigationApi } from "@/services/investigationApi";
import type { InvestigationCase, CaseStatus } from "@/services/types";
import { LayoutGrid, List } from "lucide-react";

export const Route = createFileRoute("/superior/cases/")({ component: Page });

function Page() {
  const navigate = useNavigate();
  const [view, setView] = useState<"table" | "grid">("grid");
  const [status, setStatus] = useState("All");
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");

  const loadCases = useCallback(async () => {
    setLoading(true);
    try {
      const data = await investigationApi.listCases({
        page,
        page_size: 15,
        status:
          status === "All" ? undefined : (status.toLowerCase().replace(/ /g, "_") as CaseStatus),
        q: searchQuery || undefined,
      });
      setCases(data.items || []);
      setTotalPages(data.pages || 1);
    } catch (err) {
      console.error("Failed to load cases", err);
      setCases([]);
    } finally {
      setLoading(false);
    }
  }, [page, status, searchQuery]);

  useEffect(() => {
    loadCases();
  }, [loadCases]);

  return (
    <PageScaffold
      crumbs={[{ label: "Superior", to: "/superior/dashboard" }, { label: "Cases" }]}
      title="Cases"
      actions={
        <PrimaryButton onClick={() => void navigate({ to: "/superior/cases/create" })}>
          Create case
        </PrimaryButton>
      }
    >
      <Toolbar
        search={searchQuery}
        onSearch={setSearchQuery}
        filters={
          <>
            <SelectFilter
              value={status}
              onChange={setStatus}
              options={[
                "All",
                "Open",
                "Under Review",
                "Evidence Collection",
                "Analysis",
                "Completed",
                "Archived",
              ]}
            />
            <button
              type="button"
              onClick={() => setView(view === "table" ? "grid" : "table")}
              className="inline-flex items-center gap-1.5 rounded-xl border border-border px-3 py-2 text-xs bg-card text-muted-foreground hover:text-foreground transition-colors"
            >
              {view === "table" ? (
                <LayoutGrid className="h-3.5 w-3.5" />
              ) : (
                <List className="h-3.5 w-3.5" />
              )}
              {view === "table" ? "Cards" : "Table"}
            </button>
          </>
        }
      />
      {loading ? (
        <LoadingBlock rows={8} />
      ) : cases.length === 0 ? (
        <EmptyState title="No cases found." />
      ) : view === "table" ? (
        <>
          <DataTable
            rows={cases}
            columns={[
              {
                key: "case_number",
                header: "Case",
                render: (r) => (
                  <Link
                    to="/superior/cases/$caseId"
                    params={{ caseId: r.id }}
                    className="text-primary hover:underline font-semibold"
                  >
                    {r.case_number}
                  </Link>
                ),
              },
              { key: "title", header: "Title", render: (r) => r.title },
              {
                key: "priority",
                header: "Priority",
                render: (r) => <StatusPill value={r.priority} />,
              },
              { key: "status", header: "Status", render: (r) => <StatusPill value={r.status} /> },
              {
                key: "assignee",
                header: "Assigned To",
                render: (r) =>
                  r.assignments && r.assignments.length > 0
                    ? r.assignments.map((a) => a.user?.full_name).join(", ")
                    : "Unassigned",
              },
            ]}
          />
          <Pagination page={page} pages={totalPages} onPage={setPage} />
        </>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {cases.map((c) => (
            <InvestigationCaseCard key={c.id} item={c} to="/superior/cases/$caseId" />
          ))}
        </div>
      )}
    </PageScaffold>
  );
}
