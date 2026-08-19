import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PageScaffold, Panel, PrimaryButton, StatusPill } from "@/components/ui-kit/PageKit";
import { investigationApi } from "@/services/investigationApi";
import type { InvestigationCase, EvidenceItem, NoteItem, TimelineItem } from "@/services/types";
import { Loader2 } from "lucide-react";

export const Route = createFileRoute("/investigator/cases/$caseId")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const [c, setCase] = useState<InvestigationCase | null>(null);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [notes, setNotes] = useState<NoteItem[]>([]);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const caseData = await investigationApi.getCase(caseId);
        setCase(caseData);

        const [evidenceData, notesData, timelineData] = await Promise.all([
          investigationApi.listEvidence(caseId),
          investigationApi.listNotes(caseId),
          investigationApi.listTimeline(caseId),
        ]);

        setEvidence(evidenceData.items || []);
        setNotes(notesData || []);
        setTimeline(timelineData || []);
      } catch (err) {
        console.error("Failed to load case data", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [caseId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#020617] text-slate-400">
        <Loader2 className="h-6 w-6 animate-spin mr-2" /> Loading case details...
      </div>
    );
  }

  if (!c) {
    return (
      <div className="min-h-screen bg-[#020617] p-8 text-center text-slate-400">
        Case not found or permission denied.
      </div>
    );
  }

  return (
    <PageScaffold
      crumbs={[{ label: "My Cases", to: "/investigator/cases" }, { label: c.case_number }]}
      title={c.title}
      subtitle={c.description || "No description provided"}
      actions={
        <Link to="/investigator/upload">
          <PrimaryButton>Upload evidence</PrimaryButton>
        </Link>
      }
    >
      <div className="mb-4 flex gap-2">
        <StatusPill value={c.priority} />
        <StatusPill value={c.status} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Evidence">
          <div className="space-y-2">
            {evidence.map((e) => (
              <Link
                key={e.id}
                to="/investigator/evidence/$evidenceId"
                params={{ evidenceId: e.id }}
                className="block text-sm text-purple-400 hover:text-purple-300 hover:underline"
              >
                {e.original_name}
              </Link>
            ))}
            {evidence.length === 0 && <p className="text-sm text-slate-500">No evidence attached yet</p>}
          </div>
        </Panel>
        <Panel title="Notes">
          <div className="space-y-3">
            {notes.map((n) => (
              <div key={n.id} className="mb-2 text-sm border-b border-white/5 pb-2">
                <p className="font-semibold text-purple-300">{n.title || "Quick Note"}</p>
                <p className="text-slate-300 whitespace-pre-wrap">{n.body}</p>
                <p className="text-[10px] text-slate-500 mt-1">
                  By {n.author?.full_name || "Agent"} on {new Date(n.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
            {notes.length === 0 && <p className="text-sm text-slate-500">No notes added yet</p>}
          </div>
        </Panel>
        <Panel title="Timeline" className="lg:col-span-2">
          <ol className="space-y-4">
            {timeline.map((t) => (
              <li key={t.id} className="border-l border-purple-500/40 pl-4 relative">
                <span className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full bg-purple-500 border border-[#020617]" />
                <p className="text-sm font-semibold text-slate-200">{t.title}</p>
                {t.description && <p className="text-xs text-slate-400 mt-0.5">{t.description}</p>}
                <p className="text-[10px] text-slate-500 mt-1">
                  {new Date(t.event_at).toLocaleString()}
                </p>
              </li>
            ))}
            {timeline.length === 0 && <p className="text-sm text-slate-500">No events in timeline yet</p>}
          </ol>
        </Panel>
      </div>
    </PageScaffold>
  );
}
