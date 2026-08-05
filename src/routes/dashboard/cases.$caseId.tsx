import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, Pin, Trash2, Upload } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge, formatLabel, priorityBadgeClass, statusBadgeClass } from "@/components/dashboard/Badge";
import { getToken } from "@/lib/auth";
import { apiMessage } from "@/services/apiClient";
import { investigationApi } from "@/services/investigationApi";
import type { CasePriority, CaseStatus } from "@/services/types";

export const Route = createFileRoute("/dashboard/cases/$caseId")({
  component: CaseDetailPage,
});

type Tab = "overview" | "evidence" | "notes" | "timeline" | "relationships" | "leads" | "reports";

function CaseDetailPage() {
  const { caseId } = Route.useParams();
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("overview");

  const caseQ = useQuery({ queryKey: ["case", caseId], queryFn: () => investigationApi.getCase(caseId) });
  const evidenceQ = useQuery({
    queryKey: ["evidence", caseId],
    queryFn: () => investigationApi.listEvidence(caseId),
    enabled: tab === "evidence" || tab === "overview",
  });
  const notesQ = useQuery({
    queryKey: ["notes", caseId],
    queryFn: () => investigationApi.listNotes(caseId),
    enabled: tab === "notes",
  });
  const timelineQ = useQuery({
    queryKey: ["timeline", caseId],
    queryFn: () => investigationApi.listTimeline(caseId),
    enabled: tab === "timeline" || tab === "overview",
  });
  const relQ = useQuery({
    queryKey: ["relationships", caseId],
    queryFn: () => investigationApi.listRelationships(caseId),
    enabled: tab === "relationships",
  });
  const leadsQ = useQuery({
    queryKey: ["leads", caseId],
    queryFn: () => investigationApi.listLeads(caseId),
    enabled: tab === "leads",
  });
  const reportsQ = useQuery({
    queryKey: ["reports", caseId],
    queryFn: () => investigationApi.listReports(caseId),
    enabled: tab === "reports",
  });

  const updateCase = useMutation({
    mutationFn: (body: { status?: CaseStatus; priority?: CasePriority; notes?: string }) =>
      investigationApi.updateCase(caseId, body),
    onSuccess: () => {
      toast.success("Case updated");
      void qc.invalidateQueries({ queryKey: ["case", caseId] });
      void qc.invalidateQueries({ queryKey: ["timeline", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  const upload = useMutation({
    mutationFn: (file: File) => investigationApi.uploadEvidence(caseId, file),
    onSuccess: () => {
      toast.success("Evidence uploaded");
      void qc.invalidateQueries({ queryKey: ["evidence", caseId] });
      void qc.invalidateQueries({ queryKey: ["timeline", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  const addNote = useMutation({
    mutationFn: (body: string) => investigationApi.createNote(caseId, { body }),
    onSuccess: () => {
      toast.success("Note added");
      void qc.invalidateQueries({ queryKey: ["notes", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  const addTimeline = useMutation({
    mutationFn: (title: string) => investigationApi.createTimeline(caseId, { title, event_type: "manual" }),
    onSuccess: () => {
      toast.success("Timeline event added");
      void qc.invalidateQueries({ queryKey: ["timeline", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  const addRel = useMutation({
    mutationFn: (payload: {
      source_label: string;
      target_label: string;
      source_id: string;
      target_id: string;
    }) =>
      investigationApi.createRelationship(caseId, {
        relationship_type: "other",
        source_kind: "other",
        target_kind: "other",
        ...payload,
      }),
    onSuccess: () => {
      toast.success("Relationship created");
      void qc.invalidateQueries({ queryKey: ["relationships", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  const addLead = useMutation({
    mutationFn: (title: string) => investigationApi.createLead(caseId, { title, priority: "medium" }),
    onSuccess: () => {
      toast.success("Lead created");
      void qc.invalidateQueries({ queryKey: ["leads", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  const genReport = useMutation({
    mutationFn: (format: string) => investigationApi.createReport(caseId, { format }),
    onSuccess: () => {
      toast.success("Report generated");
      void qc.invalidateQueries({ queryKey: ["reports", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  const c = caseQ.data;
  const tabs: Tab[] = ["overview", "evidence", "notes", "timeline", "relationships", "leads", "reports"];

  if (caseQ.isLoading) return <p className="text-sm text-slate-400">Loading case…</p>;
  if (!c) return <p className="text-sm text-red-400">Case not found</p>;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link to="/dashboard/cases" className="text-xs text-cyan hover:underline">
            ← Back to cases
          </Link>
          <h1 className="mt-1 text-2xl font-bold text-slate-50">{c.title}</h1>
          <p className="text-sm text-slate-400">
            {c.case_number} · Updated {new Date(c.updated_at).toLocaleString()}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge className={priorityBadgeClass(c.priority)}>{formatLabel(c.priority)}</Badge>
          <Badge className={statusBadgeClass(c.status)}>{formatLabel(c.status)}</Badge>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 border-b border-white/10 pb-2">
        {tabs.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium capitalize ${
              tab === t ? "bg-primary/20 text-primary" : "text-slate-400 hover:bg-white/5"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3 rounded-2xl border border-white/10 bg-[#111827]/90 p-5">
            <h3 className="text-sm font-semibold text-slate-100">Details</h3>
            <p className="text-sm text-slate-300 whitespace-pre-wrap">{c.description || "No description"}</p>
            <label className="block text-xs text-slate-400">
              Status
              <select
                value={c.status}
                onChange={(e) => updateCase.mutate({ status: e.target.value as CaseStatus })}
                className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"
              >
                {(["open", "under_review", "evidence_collection", "analysis", "completed", "archived"] as CaseStatus[]).map(
                  (s) => (
                    <option key={s} value={s}>
                      {formatLabel(s)}
                    </option>
                  ),
                )}
              </select>
            </label>
            <label className="block text-xs text-slate-400">
              Priority
              <select
                value={c.priority}
                onChange={(e) => updateCase.mutate({ priority: e.target.value as CasePriority })}
                className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"
              >
                {(["low", "medium", "high", "critical"] as CasePriority[]).map((p) => (
                  <option key={p} value={p}>
                    {formatLabel(p)}
                  </option>
                ))}
              </select>
            </label>
            <div>
              <p className="text-xs text-slate-400 mb-1">Assignees</p>
              <ul className="space-y-1 text-sm text-slate-200">
                {c.assignments.map((a) => (
                  <li key={a.id}>
                    {a.user?.full_name || a.user_id}
                    {a.is_primary ? " (primary)" : ""}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-[#111827]/90 p-5">
            <h3 className="text-sm font-semibold text-slate-100 mb-3">Recent timeline</h3>
            <ul className="space-y-3">
              {(timelineQ.data || []).slice(-8).reverse().map((e) => (
                <li key={e.id} className="border-l border-cyan/40 pl-3">
                  <p className="text-sm text-slate-200">{e.title}</p>
                  <p className="text-xs text-slate-500">{new Date(e.event_at).toLocaleString()}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {tab === "evidence" && (
        <div className="space-y-4">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-dashed border-cyan/40 px-4 py-3 text-sm text-cyan hover:bg-cyan/5">
            <Upload className="h-4 w-4" />
            {upload.isPending ? "Uploading…" : "Upload evidence"}
            <input
              type="file"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) upload.mutate(f);
              }}
            />
          </label>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {(evidenceQ.data?.items || []).map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/10 bg-[#111827]/90 p-4">
                <p className="truncate text-sm font-medium text-slate-100">{item.original_name}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {item.file_type} · {(item.file_size / 1024).toFixed(1)} KB
                  {item.is_duplicate ? " · duplicate" : ""}
                </p>
                <p className="mt-1 truncate font-mono text-[10px] text-slate-600">{item.sha256_hash}</p>
                <div className="mt-3 flex gap-2">
                  <a
                    href={`${investigationApi.downloadEvidenceUrl(item.id)}`}
                    onClick={async (e) => {
                      e.preventDefault();
                      const token = getToken();
                      const res = await fetch(investigationApi.downloadEvidenceUrl(item.id), {
                        headers: token ? { Authorization: `Bearer ${token}` } : {},
                      });
                      const blob = await res.blob();
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = item.original_name;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="inline-flex items-center gap-1 rounded-lg bg-white/5 px-2 py-1 text-xs text-slate-300 hover:bg-white/10"
                  >
                    <Download className="h-3 w-3" /> Download
                  </a>
                  <button
                    type="button"
                    className="inline-flex items-center gap-1 rounded-lg bg-red-500/10 px-2 py-1 text-xs text-red-400"
                    onClick={async () => {
                      try {
                        await investigationApi.deleteEvidence(item.id);
                        toast.success("Deleted");
                        void qc.invalidateQueries({ queryKey: ["evidence", caseId] });
                      } catch (err) {
                        toast.error(apiMessage(err));
                      }
                    }}
                  >
                    <Trash2 className="h-3 w-3" /> Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "notes" && (
        <NotesPanel
          notes={notesQ.data || []}
          onAdd={(body) => addNote.mutate(body)}
          onPin={async (id, pinned) => {
            await investigationApi.updateNote(id, { is_pinned: pinned });
            void qc.invalidateQueries({ queryKey: ["notes", caseId] });
          }}
          onDelete={async (id) => {
            await investigationApi.deleteNote(id);
            void qc.invalidateQueries({ queryKey: ["notes", caseId] });
          }}
        />
      )}

      {tab === "timeline" && (
        <div className="space-y-4">
          <QuickAdd placeholder="Manual timeline event…" onSubmit={(v) => addTimeline.mutate(v)} />
          <ol className="space-y-4">
            {(timelineQ.data || []).map((e) => (
              <li key={e.id} className="relative border-l border-white/15 pl-4">
                <span className="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-cyan" />
                <p className="text-sm font-medium text-slate-100">{e.title}</p>
                <p className="text-xs text-slate-500">
                  {e.event_type} · {new Date(e.event_at).toLocaleString()}
                </p>
                {e.description && <p className="mt-1 text-sm text-slate-400">{e.description}</p>}
              </li>
            ))}
          </ol>
        </div>
      )}

      {tab === "relationships" && (
        <div className="space-y-4">
          <RelForm onSubmit={(p) => addRel.mutate(p)} />
          <ul className="space-y-2">
            {(relQ.data || []).map((r) => (
              <li key={r.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-[#111827]/90 px-4 py-3 text-sm">
                <span>
                  <span className="text-cyan">{r.source_label}</span>
                  <span className="mx-2 text-slate-500">→</span>
                  <span className="text-emerald-400">{r.target_label}</span>
                </span>
                <button
                  type="button"
                  className="text-xs text-red-400"
                  onClick={async () => {
                    await investigationApi.deleteRelationship(r.id);
                    void qc.invalidateQueries({ queryKey: ["relationships", caseId] });
                  }}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === "leads" && (
        <div className="space-y-4">
          <QuickAdd placeholder="New investigation lead…" onSubmit={(v) => addLead.mutate(v)} />
          <ul className="space-y-2">
            {(leadsQ.data || []).map((l) => (
              <li key={l.id} className="rounded-xl border border-white/10 bg-[#111827]/90 px-4 py-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium text-slate-100">{l.title}</p>
                  <Badge className={statusBadgeClass(l.status)}>{formatLabel(l.status)}</Badge>
                </div>
                {l.description && <p className="mt-1 text-xs text-slate-400">{l.description}</p>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === "reports" && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => genReport.mutate("html")}
              className="rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-white"
            >
              Generate HTML summary
            </button>
            <button
              type="button"
              onClick={() => genReport.mutate("csv")}
              className="rounded-xl border border-white/15 px-3 py-2 text-xs text-slate-200"
            >
              Export CSV
            </button>
          </div>
          <ul className="space-y-2">
            {(reportsQ.data || []).map((r) => (
              <li key={r.id} className="rounded-xl border border-white/10 bg-[#111827]/90 p-4">
                <div className="flex items-center justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium text-slate-100">{r.title}</p>
                    <p className="text-xs text-slate-500">
                      {r.format} · {new Date(r.created_at).toLocaleString()}
                    </p>
                  </div>
                  <button
                    type="button"
                    className="text-xs text-cyan"
                    onClick={() => {
                      if (!r.content) return;
                      const w = window.open("", "_blank");
                      if (!w) return;
                      w.document.write(r.format === "csv" ? `<pre>${r.content}</pre>` : r.content);
                      w.document.close();
                      w.focus();
                      w.print();
                    }}
                  >
                    Print / PDF
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function QuickAdd({ placeholder, onSubmit }: { placeholder: string; onSubmit: (v: string) => void }) {
  const [v, setV] = useState("");
  return (
    <form
      className="flex gap-2"
      onSubmit={(e) => {
        e.preventDefault();
        if (!v.trim()) return;
        onSubmit(v.trim());
        setV("");
      }}
    >
      <input
        value={v}
        onChange={(e) => setV(e.target.value)}
        placeholder={placeholder}
        className="flex-1 rounded-xl border border-white/10 bg-[#111827] px-3 py-2 text-sm"
      />
      <button type="submit" className="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white">
        Add
      </button>
    </form>
  );
}

function NotesPanel({
  notes,
  onAdd,
  onPin,
  onDelete,
}: {
  notes: { id: string; title: string | null; body: string; is_pinned: boolean; updated_at: string; author?: { full_name: string } | null }[];
  onAdd: (body: string) => void;
  onPin: (id: string, pinned: boolean) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div className="space-y-4">
      <QuickAdd placeholder="Write a markdown note…" onSubmit={onAdd} />
      <ul className="space-y-3">
        {notes.map((n) => (
          <li key={n.id} className="rounded-2xl border border-white/10 bg-[#111827]/90 p-4">
            <div className="mb-2 flex items-center justify-between gap-2">
              <p className="text-xs text-slate-500">
                {n.author?.full_name || "Investigator"} · {new Date(n.updated_at).toLocaleString()}
                {n.is_pinned ? " · pinned" : ""}
              </p>
              <div className="flex gap-2">
                <button type="button" onClick={() => onPin(n.id, !n.is_pinned)} className="text-slate-400 hover:text-cyan">
                  <Pin className="h-3.5 w-3.5" />
                </button>
                <button type="button" onClick={() => onDelete(n.id)} className="text-slate-400 hover:text-red-400">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
            <pre className="whitespace-pre-wrap font-sans text-sm text-slate-200">{n.body}</pre>
          </li>
        ))}
      </ul>
    </div>
  );
}

function RelForm({
  onSubmit,
}: {
  onSubmit: (p: { source_label: string; target_label: string; source_id: string; target_id: string }) => void;
}) {
  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  return (
    <form
      className="grid gap-2 sm:grid-cols-[1fr_auto_1fr_auto]"
      onSubmit={(e) => {
        e.preventDefault();
        if (!source || !target) return;
        onSubmit({
          source_label: source,
          target_label: target,
          source_id: source.toLowerCase().replace(/\s+/g, "-"),
          target_id: target.toLowerCase().replace(/\s+/g, "-"),
        });
        setSource("");
        setTarget("");
      }}
    >
      <input value={source} onChange={(e) => setSource(e.target.value)} placeholder="Source (e.g. Evidence A)" className="rounded-xl border border-white/10 bg-[#111827] px-3 py-2 text-sm" />
      <span className="grid place-items-center text-slate-500">→</span>
      <input value={target} onChange={(e) => setTarget(e.target.value)} placeholder="Target (e.g. Device X)" className="rounded-xl border border-white/10 bg-[#111827] px-3 py-2 text-sm" />
      <button type="submit" className="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white">
        Link
      </button>
    </form>
  );
}
