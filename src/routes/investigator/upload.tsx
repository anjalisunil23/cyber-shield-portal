import { createFileRoute } from "@tanstack/react-router";
import { Upload } from "lucide-react";
import { useState } from "react";
import { MOCK_CASES } from "@/data/mock/platform";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/investigator/upload")({ component: Page });

function Page() {
  const [files, setFiles] = useState<string[]>([]);
  const [drag, setDrag] = useState(false);
  return (
    <PageScaffold crumbs={[{ label: "Investigator", to: "/investigator/dashboard" }, { label: "Upload Evidence" }]} title="Upload Evidence" subtitle="Drag & drop or browse files">
      <Panel>
        <label className="mb-3 block text-xs text-slate-400">Case
          <select className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{MOCK_CASES.map((c) => <option key={c.id}>{c.caseNumber} — {c.title}</option>)}</select>
        </label>
        <div
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => { e.preventDefault(); setDrag(false); const names = Array.from(e.dataTransfer.files).map((f) => f.name); setFiles((p) => [...p, ...names]); }}
          className={`grid place-items-center rounded-2xl border border-dashed px-6 py-16 text-center transition ${drag ? "border-cyan bg-cyan/10" : "border-white/15 bg-black/20"}`}
        >
          <Upload className="mb-3 h-10 w-10 text-cyan" />
          <p className="text-sm text-slate-200">Drop evidence files here</p>
          <p className="mt-1 text-xs text-slate-500">Images, video, audio, PDF, documents, exports</p>
          <label className="mt-4 inline-flex cursor-pointer rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white">
            Browse files
            <input type="file" multiple className="hidden" onChange={(e) => setFiles((p) => [...p, ...Array.from(e.target.files || []).map((f) => f.name)])} />
          </label>
        </div>
        {!!files.length && <ul className="mt-4 space-y-2">{files.map((f) => <li key={f} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300">{f}</li>)}</ul>}
        <PrimaryButton className="mt-4" onClick={() => setFiles([])}>Upload (UI mock)</PrimaryButton>
      </Panel>
    </PageScaffold>
  );
}
