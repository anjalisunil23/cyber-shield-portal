import { useState } from "react";
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Edit3,
  Sparkles,
  Clock,
  UserCheck,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { toast } from "sonner";
import { investigationApi } from "@/services/investigationApi";
import { apiMessage } from "@/services/apiClient";
import type { LeadItem } from "@/services/types";

export function AIExplanationCard({ lead, onRefresh }: { lead: LeadItem; onRefresh: () => void }) {
  const [showReviewModal, setShowReviewModal] = useState<"verify" | "reject" | "modify" | null>(
    null,
  );
  const [reason, setReason] = useState("");
  const [modTitle, setModTitle] = useState(lead.title);
  const [modDesc, setModDesc] = useState(lead.description || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const meta = (lead.metadata_json as Record<string, unknown>) || {};
  const isAI = Boolean(meta.ai_generated);
  const reviewState =
    (typeof meta.human_review_state === "string" ? meta.human_review_state : "") ||
    (lead.status === "approved"
      ? "VERIFIED"
      : lead.status === "rejected"
        ? "REJECTED"
        : "PENDING_REVIEW");
  const confidence =
    (typeof meta.confidence_pct === "string" ? meta.confidence_pct : "") ||
    (meta.confidence_score
      ? `${Math.round(Number(meta.confidence_score) * 100)}%`
      : "Not Available");
  const riskScore = typeof meta.risk_score === "number" ? meta.risk_score : null;
  const riskLevel = typeof meta.risk_level === "string" ? meta.risk_level : "UNSCORED";
  const whyExplanation =
    (typeof meta.why_explanation === "string" ? meta.why_explanation : "") ||
    lead.justification ||
    "No AI explanation recorded for this lead.";
  const factors: { factor: string; points: number }[] = Array.isArray(meta.factors)
    ? (meta.factors as { factor: string; points: number }[])
    : [];
  const supportingEvidence: string[] =
    (meta.supporting_evidence_names as string[] | undefined) ||
    (meta.supporting_evidence_ids as string[] | undefined) ||
    lead.related_evidence_ids ||
    [];
  const reviewHistory = meta.review_history as Record<string, unknown> | undefined;

  const handleAction = async () => {
    if (!showReviewModal) return;
    setIsSubmitting(true);
    try {
      if (showReviewModal === "verify") {
        await investigationApi.verifyLead(lead.id, reason || undefined);
        toast.success("Lead verified by investigator");
      } else if (showReviewModal === "reject") {
        await investigationApi.rejectLead(lead.id, reason || undefined);
        toast.success("Lead rejected");
      } else if (showReviewModal === "modify") {
        await investigationApi.modifyLead(lead.id, {
          title: modTitle.trim(),
          description: modDesc.trim(),
          reason: reason || undefined,
        });
        toast.success("Lead modified and updated");
      }
      setShowReviewModal(null);
      setReason("");
      onRefresh();
    } catch (err) {
      toast.error(apiMessage(err, "Action failed"));
    } finally {
      setIsSubmitting(false);
    }
  };

  const reviewStateBadge = () => {
    switch (reviewState) {
      case "VERIFIED":
        return (
          <span className="rounded-md bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-bold text-emerald-500 flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" /> VERIFIED
          </span>
        );
      case "REJECTED":
        return (
          <span className="rounded-md bg-red-500/15 border border-red-500/30 px-2 py-0.5 text-[10px] font-bold text-red-500 flex items-center gap-1">
            <XCircle className="h-3 w-3" /> REJECTED
          </span>
        );
      case "MODIFIED":
        return (
          <span className="rounded-md bg-blue-500/15 border border-blue-500/30 px-2 py-0.5 text-[10px] font-bold text-blue-400 flex items-center gap-1">
            <Edit3 className="h-3 w-3" /> MODIFIED
          </span>
        );
      default:
        return (
          <span className="rounded-md bg-amber-500/15 border border-amber-500/30 px-2 py-0.5 text-[10px] font-bold text-amber-400 flex items-center gap-1">
            <Clock className="h-3 w-3" /> PENDING REVIEW
          </span>
        );
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-card p-4 space-y-3.5 transition-colors hover:border-primary/40 shadow-sm text-foreground">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="space-y-1 max-w-[80%]">
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="text-sm font-bold text-foreground">{lead.title}</h4>
            {reviewStateBadge()}
            {isAI && (
              <span className="rounded-md bg-primary/10 border border-primary/20 px-2 py-0.5 text-[10px] font-bold text-primary flex items-center gap-1">
                <Sparkles className="h-3 w-3" /> AI GENERATED
              </span>
            )}
          </div>
          {lead.description && <p className="text-xs text-muted-foreground">{lead.description}</p>}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="rounded-lg bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 text-xs font-bold text-amber-500">
            Risk: {riskLevel}
            {riskScore != null ? ` (${riskScore}/100)` : ""}
          </span>
          <span className="rounded-lg bg-muted px-2 py-1 text-xs font-mono text-muted-foreground">
            {confidence} conf
          </span>
        </div>
      </div>

      {/* Why was this generated? Section */}
      <div className="rounded-xl border border-border bg-background p-3 space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-[10px] font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
            <ShieldAlert className="h-3.5 w-3.5" /> Why was this investigative lead generated?
          </p>
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-[10px] text-muted-foreground hover:text-foreground flex items-center gap-0.5"
          >
            {isExpanded ? "Less detail" : "More factors"}
            {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </button>
        </div>
        <p className="text-xs text-foreground leading-relaxed">{whyExplanation}</p>

        {/* Explainability Factors */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          {factors.map((f, i) => (
            <span
              key={i}
              className="rounded-md bg-card border border-border/80 px-2 py-0.5 text-[10px] font-medium text-foreground flex items-center gap-1"
            >
              <span className="text-emerald-500 font-bold">+{f.points}</span> {f.factor}
            </span>
          ))}
        </div>
      </div>

      {/* Supporting Evidence Chips */}
      {supportingEvidence.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-muted-foreground text-[11px]">Supporting Evidence:</span>
          {supportingEvidence.map((evName, idx) => (
            <span
              key={idx}
              className="rounded-lg bg-primary/5 border border-primary/20 px-2 py-0.5 text-[10px] font-mono text-primary flex items-center gap-1"
            >
              <FileText className="h-3 w-3" /> {evName}
            </span>
          ))}
        </div>
      )}

      {/* Review History / Audit Trail */}
      {lead.review_comment && (
        <div className="rounded-lg bg-muted/40 p-2.5 border border-border text-xs space-y-1">
          <div className="flex items-center justify-between text-[10px] text-muted-foreground">
            <span className="font-semibold flex items-center gap-1">
              <UserCheck className="h-3 w-3 text-primary" /> Investigator Decision Record
            </span>
            {(typeof reviewHistory?.timestamp === "string" ||
              typeof reviewHistory?.timestamp === "number") && (
              <span>{new Date(reviewHistory.timestamp).toLocaleString()}</span>
            )}
          </div>
          <p className="text-foreground text-[11px] italic">"{lead.review_comment}"</p>
        </div>
      )}

      {/* Human Oversight Action Buttons */}
      <div className="pt-2 border-t border-border flex flex-wrap items-center justify-between gap-2">
        <span className="text-[11px] text-muted-foreground italic">
          Investigator Oversight Action:
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowReviewModal("verify")}
            className="inline-flex items-center gap-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 px-3 py-1.5 text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/25 transition-colors"
          >
            <CheckCircle2 className="h-3.5 w-3.5" /> Verify Lead
          </button>
          <button
            type="button"
            onClick={() => setShowReviewModal("reject")}
            className="inline-flex items-center gap-1 rounded-lg bg-red-500/15 border border-red-500/30 px-3 py-1.5 text-xs font-semibold text-red-500 hover:bg-red-500/25 transition-colors"
          >
            <XCircle className="h-3.5 w-3.5" /> Reject
          </button>
          <button
            type="button"
            onClick={() => {
              setModTitle(lead.title);
              setModDesc(lead.description || "");
              setShowReviewModal("modify");
            }}
            className="inline-flex items-center gap-1 rounded-lg bg-muted border border-border px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted/80 transition-colors"
          >
            <Edit3 className="h-3.5 w-3.5" /> Modify
          </button>
        </div>
      </div>

      {/* Decision Input Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-150">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-foreground flex items-center gap-2">
              {showReviewModal === "verify" && (
                <>
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" /> Verify AI Investigative Lead
                </>
              )}
              {showReviewModal === "reject" && (
                <>
                  <XCircle className="h-5 w-5 text-red-500" /> Reject / Dismiss AI Finding
                </>
              )}
              {showReviewModal === "modify" && (
                <>
                  <Edit3 className="h-5 w-5 text-primary" /> Modify Lead with Investigator Context
                </>
              )}
            </h3>

            {showReviewModal === "modify" && (
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1">
                    Updated Lead Title
                  </label>
                  <input
                    type="text"
                    value={modTitle}
                    onChange={(e) => setModTitle(e.target.value)}
                    className="w-full rounded-xl border border-border bg-background p-2.5 text-xs text-foreground"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1">
                    Updated Description
                  </label>
                  <textarea
                    rows={2}
                    value={modDesc}
                    onChange={(e) => setModDesc(e.target.value)}
                    className="w-full rounded-xl border border-border bg-background p-2.5 text-xs text-foreground"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-muted-foreground mb-1">
                Investigator Rationale / Review Reason
              </label>
              <textarea
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Enter justification notes for the audit trail..."
                className="w-full rounded-xl border border-border bg-background p-2.5 text-xs text-foreground placeholder-muted-foreground"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowReviewModal(null)}
                className="rounded-xl border border-border px-4 py-2 text-xs font-semibold text-foreground hover:bg-muted"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isSubmitting}
                onClick={handleAction}
                className={`rounded-xl px-4 py-2 text-xs font-bold transition-colors disabled:opacity-50 ${
                  showReviewModal === "verify"
                    ? "bg-emerald-500 text-slate-950 hover:bg-emerald-400"
                    : showReviewModal === "reject"
                      ? "bg-red-500 text-white hover:bg-red-400"
                      : "bg-primary text-primary-foreground hover:bg-primary/90"
                }`}
              >
                {isSubmitting ? "Saving..." : "Confirm Decision"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
