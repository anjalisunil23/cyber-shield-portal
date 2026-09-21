import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { PageScaffold, Panel } from "@/components/ui-kit/PageKit";
import { AIExplanationCard } from "@/components/dashboard/AIExplanationCard";
import { AIDisclaimer } from "@/components/dashboard/AIDisclaimer";
import { investigationApi } from "@/services/investigationApi";
import type { LeadItem } from "@/services/types";

export const Route = createFileRoute("/investigator/leads")({ component: Page });

function Page() {
  const qc = useQueryClient();
  const casesQ = useQuery({
    queryKey: ["cases"],
    queryFn: () => investigationApi.listCases({ page_size: 100 }),
  });

  const leadsQ = useQuery({
    queryKey: ["investigator-leads", casesQ.data?.items?.map((c) => c.id).join(",")],
    enabled: !!casesQ.data?.items,
    queryFn: async () => {
      const rows: { caseNumber: string; caseId: string; lead: LeadItem }[] = [];
      for (const c of casesQ.data?.items || []) {
        const leads = await investigationApi.listLeads(c.id);
        for (const lead of leads) {
          rows.push({ caseNumber: c.case_number, caseId: c.id, lead });
        }
      }
      return rows;
    },
  });

  const rows = leadsQ.data || [];

  return (
    <PageScaffold
      crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Leads" }]}
      title="Leads"
    >
      <AIDisclaimer className="mb-4" />
      {leadsQ.isLoading || casesQ.isLoading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading leads from assigned cases…
        </div>
      ) : rows.length === 0 ? (
        <Panel>
          <p className="text-sm text-muted-foreground">
            No leads yet. Open a case, run the AI pipeline, or create a manual lead from the case
            workspace.
          </p>
        </Panel>
      ) : (
        <div className="space-y-4">
          {rows.map(({ caseNumber, caseId, lead }) => (
            <div key={lead.id} className="space-y-2">
              <Link
                to="/investigator/cases/$caseId"
                params={{ caseId }}
                className="text-xs font-semibold text-primary hover:underline"
              >
                {caseNumber}
              </Link>
              <AIExplanationCard
                lead={lead}
                onRefresh={() => {
                  void qc.invalidateQueries({ queryKey: ["investigator-leads"] });
                  void qc.invalidateQueries({ queryKey: ["leads"] });
                }}
              />
            </div>
          ))}
        </div>
      )}
    </PageScaffold>
  );
}
