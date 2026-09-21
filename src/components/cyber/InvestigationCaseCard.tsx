import { Link } from "@tanstack/react-router";
import { StatusPill } from "@/components/ui-kit/PageKit";
import type { InvestigationCase } from "@/services/types";

function relativeUpdated(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.max(0, Math.round(diff / 60000));
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 48) return `${hrs}h ago`;
  return new Date(iso).toLocaleDateString();
}

export function InvestigationCaseCard({
  item,
  to,
  leadName,
}: {
  item: InvestigationCase;
  to: "/dashboard/cases/$caseId" | "/superior/cases/$caseId" | "/investigator/cases/$caseId";
  leadName?: string;
}) {
  const lead =
    leadName ||
    item.investigator_lead?.full_name ||
    item.assignments?.find((a) => a.is_primary)?.user?.full_name ||
    item.assignments?.[0]?.user?.full_name ||
    "—";

  return (
    <Link
      to={to}
      params={{ caseId: item.id }}
      className="glass-card glow-hover group block p-4 text-left"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="font-mono text-[11px] font-semibold text-cyan">{item.case_number}</p>
        <StatusPill value={item.priority} />
      </div>
      <p className="mt-2 line-clamp-2 text-sm font-semibold text-foreground">{item.title}</p>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
        <div>
          <dt className="text-muted-foreground">Status</dt>
          <dd className="mt-0.5">
            <StatusPill value={item.status} />
          </dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Lead</dt>
          <dd className="mt-0.5 truncate text-foreground">{lead}</dd>
        </div>
        <div className="col-span-2">
          <dt className="text-muted-foreground">Updated</dt>
          <dd className="mt-0.5 text-foreground">{relativeUpdated(item.updated_at)}</dd>
        </div>
      </dl>
      <span className="mt-3 inline-flex text-xs font-medium text-primary group-hover:underline">
        Open case
      </span>
    </Link>
  );
}
