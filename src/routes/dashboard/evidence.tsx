import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { investigationApi } from "@/services/investigationApi";

export const Route = createFileRoute("/dashboard/evidence")({
  component: EvidencePage,
});

function EvidencePage() {
  const casesQ = useQuery({
    queryKey: ["cases", "evidence-hub"],
    queryFn: () => investigationApi.listCases({ page_size: 50 }),
  });

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-foreground">Evidence</h1>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {(casesQ.data?.items || []).map((c) => (
          <Link
            key={c.id}
            to="/dashboard/cases/$caseId"
            params={{ caseId: c.id }}
            className="rounded-2xl border border-border bg-card p-5 transition hover:border-primary/40 shadow-sm"
          >
            <p className="text-xs text-primary font-mono font-semibold">{c.case_number}</p>
            <p className="mt-1 text-sm font-semibold text-foreground">{c.title}</p>
            <p className="mt-2 text-xs text-muted-foreground">Open case → Evidence tab</p>
          </Link>
        ))}
      </div>
      {!casesQ.data?.items.length && !casesQ.isLoading && (
        <p className="text-sm text-muted-foreground">Create a case first to attach evidence.</p>
      )}
    </div>
  );
}
