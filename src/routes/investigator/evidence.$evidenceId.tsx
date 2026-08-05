import { createFileRoute } from "@tanstack/react-router";
import { MOCK_EVIDENCE } from "@/data/mock/platform";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/evidence/$evidenceId")({ component: Page });

function Page() {
  const { evidenceId } = Route.useParams();
  const e = MOCK_EVIDENCE.find((x) => x.id === evidenceId) || MOCK_EVIDENCE[0];
  return (
    <PageScaffold crumbs={[{ label: "Repository", to: "/investigator/evidence" }, { label: e.name }]} title="Evidence Viewer" subtitle={e.name}>
      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Preview" className="lg:col-span-2"><div className="grid h-72 place-items-center rounded-xl bg-black/40 text-slate-500">{e.type.toUpperCase()} viewer mock</div></Panel>
        <Panel title="Details">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-slate-500">Case</dt><dd className="text-cyan">{e.caseNumber}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Size</dt><dd>{e.size}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">SHA256</dt><dd className="font-mono text-[10px]">{e.sha256}</dd></div>
          </dl>
          <div className="mt-3 flex flex-wrap gap-1">{e.tags.map((t) => <StatusPill key={t} value={t} />)}</div>
        </Panel>
      </div>
    </PageScaffold>
  );
}
