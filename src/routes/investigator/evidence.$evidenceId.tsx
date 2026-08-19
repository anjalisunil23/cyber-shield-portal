import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PageScaffold, Panel, StatusPill } from "@/components/ui-kit/PageKit";
import { investigationApi } from "@/services/investigationApi";
import type { EvidenceItem } from "@/services/types";
import { Download, Loader2 } from "lucide-react";

export const Route = createFileRoute("/investigator/evidence/$evidenceId")({ component: Page });

function Page() {
  const { evidenceId } = Route.useParams();
  const [e, setEvidence] = useState<EvidenceItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    investigationApi.getEvidence(evidenceId)
      .then((data) => {
        setEvidence(data);
      })
      .catch((err) => {
        console.error("Failed to load evidence details", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [evidenceId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#020617] text-slate-400">
        <Loader2 className="h-6 w-6 animate-spin mr-2" /> Loading evidence...
      </div>
    );
  }

  if (!e) {
    return (
      <div className="min-h-screen bg-[#020617] p-8 text-center text-slate-400">
        Evidence item not found or permission denied.
      </div>
    );
  }

  const downloadUrl = investigationApi.downloadEvidenceUrl(e.id);

  return (
    <PageScaffold
      crumbs={[{ label: "Repository", to: "/investigator/evidence" }, { label: e.original_name }]}
      title="Evidence Viewer"
      subtitle={e.original_name}
    >
      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Preview" className="lg:col-span-2">
          <div className="flex flex-col items-center justify-center h-72 rounded-xl bg-black/40 text-slate-400 border border-white/5 p-6">
            <span className="font-bold text-sm uppercase text-purple-400 tracking-wider mb-2">
              {e.file_type} File
            </span>
            <p className="text-xs text-slate-500 mb-4">{e.mime_type || "Unknown MIME Type"}</p>
            <a
              href={downloadUrl}
              download={e.original_name}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-xs transition"
            >
              <Download className="h-4 w-4" /> Download Original File
            </a>
          </div>
        </Panel>
        <Panel title="Details">
          <dl className="space-y-2.5 text-sm">
            <div className="flex justify-between border-b border-white/5 pb-1.5">
              <dt className="text-slate-500">File size</dt>
              <dd className="font-medium">{(e.file_size / 1024).toFixed(1)} KB</dd>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-1.5">
              <dt className="text-slate-500">File Type</dt>
              <dd className="font-medium uppercase">{e.file_type}</dd>
            </div>
            <div className="flex flex-col border-b border-white/5 pb-1.5">
              <dt className="text-slate-500 mb-1">SHA256 Hash</dt>
              <dd className="font-mono text-[10px] break-all bg-black/30 p-1.5 rounded border border-white/5 text-purple-300">
                {e.sha256_hash}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Duplicate</dt>
              <dd>{e.is_duplicate ? "Yes (hashed match)" : "No"}</dd>
            </div>
          </dl>
          {e.tags && e.tags.length > 0 && (
            <div className="mt-4 border-t border-white/5 pt-3">
              <span className="text-xs text-slate-500 block mb-1.5">Tags</span>
              <div className="flex flex-wrap gap-1">
                {e.tags.map((t) => (
                  <StatusPill key={t} value={t} />
                ))}
              </div>
            </div>
          )}
        </Panel>
      </div>
    </PageScaffold>
  );
}
