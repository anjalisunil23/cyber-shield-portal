import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Plus, Trash2, UserCheck } from "lucide-react";
import { PageScaffold, Panel, PrimaryButton, StatusPill, GhostButton } from "@/components/ui-kit/PageKit";
import { useCaseList, useEvidenceList, deleteEvidenceItem, useTaskList } from "@/data/mock/platformState";
import { MOCK_NOTES, MOCK_TIMELINE } from "@/data/mock/platform";
import { UploadEvidenceModal } from "@/components/superior/UploadEvidenceModal";
import { AssignTaskModal } from "@/components/superior/AssignTaskModal";

export const Route = createFileRoute("/superior/cases/$caseId")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const cases = useCaseList();
  const evidenceList = useEvidenceList();
  const taskList = useTaskList();
  const navigate = useNavigate();

  const c = cases.find((x) => x.id === caseId || x.caseNumber === caseId) || cases[0];
  const caseEvidence = evidenceList.filter((e) => e.caseNumber === c.caseNumber);
  const caseTasks = taskList.filter((t) => t.caseNumber === c.caseNumber);

  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isAssignTaskOpen, setIsAssignTaskOpen] = useState(false);

  const handleDeleteEvidence = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete evidence "${name}" from case ${c.caseNumber}?`)) {
      deleteEvidenceItem(id);
    }
  };

  return (
    <PageScaffold
      crumbs={[{ label: "Cases", to: "/superior/cases" }, { label: c.caseNumber }]}
      title={c.title}
      subtitle={c.description}
      actions={
        <div className="flex flex-wrap gap-2">
          <Link to={"/superior/cases/$caseId/assign" as "/"} params={{ caseId: c.id } as never}>
            <PrimaryButton>
              <UserCheck className="mr-1.5 inline h-4 w-4" /> Assign Case / Task
            </PrimaryButton>
          </Link>
          <GhostButton onClick={() => setIsUploadOpen(true)}>
            <Plus className="mr-1.5 inline h-4 w-4" /> Add Evidence
          </GhostButton>
        </div>
      }
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <StatusPill value={c.priority} />
        <StatusPill value={c.status} />
        <span className="rounded-lg border border-cyan/30 bg-cyan/10 px-2.5 py-1 text-xs text-cyan">
          Assigned Investigator: {c.assignee}
        </span>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Evidence Panel with Add & Delete */}
        <Panel
          title={`Evidence (${caseEvidence.length})`}
          actions={
            <button
              type="button"
              onClick={() => setIsUploadOpen(true)}
              className="text-xs font-medium text-cyan hover:underline"
            >
              + Upload
            </button>
          }
        >
          {caseEvidence.length === 0 ? (
            <p className="text-xs text-slate-500">No evidence uploaded for this case yet.</p>
          ) : (
            <ul className="divide-y divide-white/5">
              {caseEvidence.map((e) => (
                <li key={e.id} className="flex items-center justify-between py-2 text-sm">
                  <div
                    onClick={() => navigate({ to: "/superior/evidence/$evidenceId", params: { evidenceId: e.id } })}
                    className="cursor-pointer hover:text-cyan"
                  >
                    <p className="font-medium text-slate-200">{e.name}</p>
                    <p className="text-xs text-slate-500">
                      {e.type} · {e.size} · Uploaded by {e.uploadedBy}
                    </p>
                  </div>
                  <button
                    type="button"
                    title="Delete evidence"
                    onClick={() => handleDeleteEvidence(e.id, e.name)}
                    className="rounded p-1 text-slate-500 hover:bg-rose-500/20 hover:text-rose-400"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Panel>

        {/* Assigned Investigation Tasks */}
        <Panel
          title={`Assigned Tasks (${caseTasks.length})`}
          actions={
            <button
              type="button"
              onClick={() => setIsAssignTaskOpen(true)}
              className="text-xs font-medium text-cyan hover:underline"
            >
              + Assign Task
            </button>
          }
        >
          {caseTasks.length === 0 ? (
            <p className="text-xs text-slate-500">No investigation tasks assigned for this case.</p>
          ) : (
            <ul className="space-y-2">
              {caseTasks.map((t) => (
                <li key={t.id} className="rounded-xl border border-white/5 bg-black/20 p-3 text-xs">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-slate-200">{t.title}</p>
                    <StatusPill value={t.status} />
                  </div>
                  <div className="mt-2 flex items-center justify-between text-slate-400">
                    <span>Assignee: {t.assignee || c.assignee}</span>
                    <span>Due: {t.due}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Panel>

        <Panel title="Notes" className="lg:col-span-2">
          {MOCK_NOTES.filter((n) => n.caseNumber === c.caseNumber).map((n) => (
            <div key={n.id} className="mb-3 rounded-xl border border-white/5 bg-black/20 p-3">
              <p className="text-sm font-medium text-slate-100">{n.title}</p>
              <p className="mt-1 text-xs text-slate-400">{n.body}</p>
              <p className="mt-2 text-[10px] text-slate-500">Author: {n.author} · {n.updatedAt}</p>
            </div>
          ))}
        </Panel>

        <Panel title="Timeline" className="lg:col-span-2">
          <ol className="space-y-3">
            {MOCK_TIMELINE.map((t) => (
              <li key={t.id} className="border-l border-cyan/40 pl-3">
                <p className="text-sm text-slate-100">{t.title}</p>
                <p className="text-xs text-slate-500">{t.at} — {t.detail}</p>
              </li>
            ))}
          </ol>
        </Panel>
      </div>

      <UploadEvidenceModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        defaultCaseNumber={c.caseNumber}
      />

      <AssignTaskModal
        isOpen={isAssignTaskOpen}
        onClose={() => setIsAssignTaskOpen(false)}
        defaultCaseNumber={c.caseNumber}
        defaultInvestigator={c.assignee}
      />
    </PageScaffold>
  );
}
