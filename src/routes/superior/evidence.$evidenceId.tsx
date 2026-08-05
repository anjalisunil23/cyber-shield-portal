import { createFileRoute } from "@tanstack/react-router";
import { MOCK_EVIDENCE } from "@/data/mock/platform";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/evidence/$evidenceId")({ component: Page });

function Page() {
  const { evidenceId } = Route.useParams();
  const e = MOCK_EVIDENCE.find((x) => x.id === evidenceId) || MOCK_EVIDENCE[0];
  return (
    <PageScaffold crumbs={[{ label: "Evidence", to: "/superior/evidence" }, { label: e.name }]} title={e.name} subtitle={`${e.type} · ${e.size}`}>
      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Viewer" className="lg:col-span-2">
          <div className="grid h-64 place-items-center rounded-xl border border-dashed border-white/15 bg-black/30 text-sm text-slate-500">
            {e.type === "image" && "Image viewer mock"}
            {e.type === "video" && "Video player mock"}
            {e.type === "audio" && "Audio player mock"}
            {e.type === "pdf" && "PDF viewer mock"}
            {(e.type === "document" || e.type === "other") && "Document viewer mock"}
          </div>
        </Panel>
        <Panel title="Metadata">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-slate-500">Case</dt><dd className="text-cyan">{e.caseNumber}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">SHA256</dt><dd className="font-mono text-xs">{e.sha256}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Uploaded</dt><dd>{e.uploadedAt}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">By</dt><dd>{e.uploadedBy}</dd></div>
          </dl>
          <div className="mt-3 flex flex-wrap gap-1">{e.tags.map((t) => <StatusPill key={t} value={t} />)}</div>
          <div className="mt-4 rounded-xl border border-dashed border-cyan/30 bg-cyan/5 p-3 text-xs text-slate-400">AI panel placeholder — OCR / objects / transcript</div>
        </Panel>
      </div>
    </PageScaffold>
  );
}
