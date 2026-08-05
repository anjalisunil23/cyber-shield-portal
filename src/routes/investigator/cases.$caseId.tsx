import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_EVIDENCE, MOCK_NOTES, MOCK_TIMELINE } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/cases/$caseId")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const c = MOCK_CASES.find((x) => x.id === caseId) || MOCK_CASES[0];
  return (
    <PageScaffold crumbs={[{ label: "My Cases", to: "/investigator/cases" }, { label: c.caseNumber }]} title={c.title} subtitle={c.description} actions={<Link to={"/investigator/upload" as "/"}><PrimaryButton>Upload evidence</PrimaryButton></Link>}>
      <div className="mb-4 flex gap-2"><StatusPill value={c.priority} /><StatusPill value={c.status} /></div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Evidence">{MOCK_EVIDENCE.filter((e) => e.caseNumber === c.caseNumber).map((e) => <Link key={e.id} to={"/investigator/evidence/$evidenceId" as "/"} params={{ evidenceId: e.id } as never} className="block text-sm text-cyan hover:underline">{e.name}</Link>)}</Panel>
        <Panel title="Notes">{MOCK_NOTES.filter((n) => n.caseNumber === c.caseNumber).map((n) => <div key={n.id} className="mb-2 text-sm"><p className="font-medium text-slate-100">{n.title}</p><p className="text-slate-500">{n.body}</p></div>)}</Panel>
        <Panel title="Timeline" className="lg:col-span-2"><ol className="space-y-3">{MOCK_TIMELINE.map((t) => <li key={t.id} className="border-l border-cyan/40 pl-3"><p className="text-sm text-slate-100">{t.title}</p><p className="text-xs text-slate-500">{t.at}</p></li>)}</ol></Panel>
      </div>
    </PageScaffold>
  );
}
