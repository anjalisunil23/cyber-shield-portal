import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_EVIDENCE, MOCK_NOTES, MOCK_TIMELINE } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, StatusPill, GhostButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/cases/$caseId")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const c = MOCK_CASES.find((x) => x.id === caseId) || MOCK_CASES[0];
  return (
    <PageScaffold crumbs={[{ label: "Cases", to: "/superior/cases" }, { label: c.caseNumber }]} title={c.title} subtitle={c.description} actions={<div className="flex gap-2"><Link to={"/superior/cases/$caseId/assign" as "/"} params={{ caseId: c.id } as never}><PrimaryButton>Assign</PrimaryButton></Link><GhostButton>Close case</GhostButton></div>}>
      <div className="mb-4 flex flex-wrap gap-2"><StatusPill value={c.priority} /><StatusPill value={c.status} /><span className="text-xs text-slate-500">Assignee: {c.assignee}</span></div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Evidence">{MOCK_EVIDENCE.filter((e) => e.caseNumber === c.caseNumber).map((e) => <p key={e.id} className="text-sm text-slate-300">{e.name}</p>)}</Panel>
        <Panel title="Notes">{MOCK_NOTES.filter((n) => n.caseNumber === c.caseNumber).map((n) => <div key={n.id} className="mb-2"><p className="text-sm font-medium text-slate-100">{n.title}</p><p className="text-xs text-slate-500">{n.body}</p></div>)}</Panel>
        <Panel title="Timeline" className="lg:col-span-2"><ol className="space-y-3">{MOCK_TIMELINE.map((t) => <li key={t.id} className="border-l border-cyan/40 pl-3"><p className="text-sm text-slate-100">{t.title}</p><p className="text-xs text-slate-500">{t.at} — {t.detail}</p></li>)}</ol></Panel>
        <Panel title="Attachments / Reports" className="lg:col-span-2"><p className="text-sm text-slate-400">Use Reports tab to generate investigation summaries for this case.</p><Link to={"/superior/reports" as "/"} className="mt-2 inline-block text-sm text-cyan">Open reports →</Link></Panel>
      </div>
    </PageScaffold>
  );
}
