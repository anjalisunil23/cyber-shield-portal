import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  BrainCircuit,
  Sparkles,
  ShieldAlert,
  Search,
  CheckCircle2,
  AlertTriangle,
  FileText,
  RefreshCw,
  Share2,
  Printer,
  Download,
  Flame,
  Activity,
  Layers,
} from "lucide-react";
import { toast } from "sonner";
import { AIDisclaimer } from "@/components/dashboard/AIDisclaimer";
import { investigationApi } from "@/services/investigationApi";
import { apiMessage } from "@/services/apiClient";
import type {
  CaseRiskAssessment,
  CaseCorrelation,
  RAGSearchResult,
  InvestigationSummary,
} from "@/services/types";

export function CaseIntelligencePanel({
  caseId,
  caseNumber,
  onOpenEvidence,
}: {
  caseId: string;
  caseNumber: string;
  onOpenEvidence?: (evidenceId: string) => void;
}) {
  const qc = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [activeSearchResult, setActiveSearchResult] = useState<RAGSearchResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [generatedSummary, setGeneratedSummary] = useState<InvestigationSummary | null>(null);
  const [isSummarizing, setIsSummarizing] = useState(false);

  // Queries
  const riskQ = useQuery({
    queryKey: ["case-risk", caseId],
    queryFn: () => investigationApi.getCaseRisk(caseId),
    enabled: !!caseId,
  });

  const corrQ = useQuery({
    queryKey: ["case-correlations", caseId],
    queryFn: () => investigationApi.getCaseCorrelations(caseId),
    enabled: !!caseId,
  });

  const pipelineMutation = useMutation({
    mutationFn: () => investigationApi.runCasePipeline(caseId),
    onSuccess: (res) => {
      toast.success(
        `AI Pipeline executed! Found ${res.correlations_found} correlations, generated ${res.leads_generated} leads.`,
      );
      void qc.invalidateQueries({ queryKey: ["case-risk", caseId] });
      void qc.invalidateQueries({ queryKey: ["case-correlations", caseId] });
      void qc.invalidateQueries({ queryKey: ["case-graph", caseId] });
      void qc.invalidateQueries({ queryKey: ["leads", caseId] });
      void qc.invalidateQueries({ queryKey: ["timeline", caseId] });
      void qc.invalidateQueries({ queryKey: ["evidence", caseId] });
    },
    onError: (e) => toast.error(apiMessage(e, "Failed to execute pipeline")),
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await investigationApi.searchCaseEvidence(caseId, searchQuery.trim());
      setActiveSearchResult(res);
      toast.success(`Search completed: ${res.total_matches} matching evidence found`);
    } catch (err) {
      toast.error(apiMessage(err, "Search failed"));
    } finally {
      setIsSearching(false);
    }
  };

  const handleSummarize = async () => {
    setIsSummarizing(true);
    try {
      const summary = await investigationApi.getCaseSummary(caseId);
      setGeneratedSummary(summary);
      toast.success("AI Investigation Summary generated");
    } catch (err) {
      toast.error(apiMessage(err, "Failed to generate summary"));
    } finally {
      setIsSummarizing(false);
    }
  };

  const risk = riskQ.data;
  const correlations = corrQ.data || [];

  return (
    <div className="space-y-6 text-foreground">
      <AIDisclaimer />
      {/* Action Banner */}
      <div className="rounded-2xl border border-primary/30 bg-gradient-to-r from-card via-card to-primary/5 p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-primary/20 text-primary shadow-inner">
            <BrainCircuit className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-foreground flex items-center gap-2">
              Autonomous Intelligence Engine — Case {caseNumber}
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Multi-source cross-evidence correlation, entity resolution, timeline reconstruction,
              and transparent risk scoring.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            disabled={pipelineMutation.isPending}
            onClick={() => pipelineMutation.mutate()}
            className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-bold text-primary-foreground hover:bg-primary/90 transition-all shadow-md disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${pipelineMutation.isPending ? "animate-spin" : ""}`} />
            {pipelineMutation.isPending ? "Running Pipeline..." : "Run End-to-End Pipeline"}
          </button>
        </div>
      </div>

      {/* Grid: Risk Assessment & Correlations */}
      <div className="grid gap-6 lg:grid-cols-12">
        {/* Risk Assessment Engine Card */}
        <div className="lg:col-span-5 rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <Flame className="h-4 w-4 text-amber-500" /> Transparent Risk Assessment
            </h3>
            {risk && (
              <span
                className={`rounded-lg px-2.5 py-1 text-xs font-bold border ${
                  risk.risk_level === "CRITICAL"
                    ? "bg-red-500/15 border-red-500/30 text-red-500"
                    : risk.risk_level === "HIGH"
                      ? "bg-amber-500/15 border-amber-500/30 text-amber-400"
                      : risk.risk_level === "MEDIUM"
                        ? "bg-blue-500/15 border-blue-500/30 text-blue-400"
                        : "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
                }`}
              >
                {risk.risk_level}
              </span>
            )}
          </div>

          {/* Risk Score Meter */}
          <div className="rounded-xl border border-border bg-background p-4 text-center space-y-2">
            <p className="text-[11px] text-muted-foreground uppercase tracking-wider font-semibold">
              Investigative Priority Score
            </p>
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-4xl font-extrabold text-amber-400">
                {risk?.risk_score ?? "--"}
              </span>
              <span className="text-xs text-muted-foreground font-mono">/ 100</span>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 via-amber-500 to-red-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(5, risk?.risk_score || 0))}%` }}
              />
            </div>
          </div>

          {/* Factor Breakdown */}
          <div className="space-y-2">
            <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Risk Scoring Factors & Criteria
            </p>
            {risk?.factors && risk.factors.length > 0 ? (
              <div className="space-y-2">
                {risk.factors.map((f, i) => (
                  <div
                    key={i}
                    className="p-2.5 rounded-xl border border-border bg-background/80 space-y-1 text-xs"
                  >
                    <div className="flex items-center justify-between font-semibold">
                      <span className="text-foreground">{f.factor}</span>
                      <span className="rounded bg-emerald-500/10 px-1.5 py-0.2 text-[10px] text-emerald-500 font-bold">
                        +{f.points} pts
                      </span>
                    </div>
                    <p className="text-[11px] text-muted-foreground">{f.detail}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground italic">
                Upload evidence to trigger automated factor risk scoring.
              </p>
            )}
          </div>

          {/* Legal Disclaimer */}
          <div className="rounded-xl border border-border/80 bg-background/50 p-3 text-[10px] text-muted-foreground flex items-start gap-2">
            <ShieldAlert className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <span>
              {risk?.disclaimer ||
                "Cyber Shield Risk Assessment represents investigative priority and anomaly severity, not legal proof of guilt."}
            </span>
          </div>
        </div>

        {/* Cross-Source Correlations */}
        <div className="lg:col-span-7 rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                  <Share2 className="h-4 w-4 text-cyan" /> Cross-Source Entity Correlations (
                  {correlations.length})
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Entities verified across multiple distinct files (e.g., chat logs, call records,
                  CCTV frames, documents).
                </p>
              </div>
            </div>

            {correlations.length === 0 ? (
              <div className="rounded-xl border border-border bg-background p-10 text-center text-muted-foreground space-y-2">
                <Layers className="h-8 w-8 mx-auto opacity-50 text-cyan" />
                <p className="text-xs">No multi-source matches detected yet.</p>
                <p className="text-[11px]">
                  Click "Run End-to-End Pipeline" to correlate case evidence.
                </p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
                {correlations.map((corr, idx) => (
                  <div
                    key={idx}
                    className="rounded-xl border border-border bg-background p-3.5 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="rounded bg-cyan/10 border border-cyan/30 px-2 py-0.5 text-[10px] font-bold text-cyan uppercase">
                          {corr.entity_type}
                        </span>
                        <span className="font-bold text-foreground font-mono">
                          {corr.normalized_value}
                        </span>
                      </div>
                      <span className="rounded-md bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 text-[10px] font-semibold text-emerald-500">
                        {Math.round(corr.confidence_score * 100)}% Confidence
                      </span>
                    </div>

                    <p className="text-muted-foreground text-[11px] leading-relaxed">
                      {corr.explanation}
                    </p>

                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] text-muted-foreground font-medium">
                        Matching Files:
                      </span>
                      {corr.supporting_evidence_names.map((name, i) => (
                        <span
                          key={i}
                          className="rounded bg-card border border-border px-2 py-0.5 text-[10px] font-mono text-primary flex items-center gap-1"
                        >
                          <FileText className="h-2.5 w-2.5" /> {name}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Natural-Language Search / RAG Console */}
      <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
        <div>
          <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
            <Search className="h-4 w-4 text-primary" /> Natural-Language Evidence Intelligence
            Search (RAG)
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Query the case evidence repository in plain English. Answers are strictly grounded in
            stored evidence with verified citations.
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="e.g. 'Show evidence related to the phone number used in the evening calls' or 'What vehicle was spotted near Marine Drive?'"
            className="flex-1 rounded-xl border border-border bg-background px-4 py-2.5 text-xs text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none"
          />
          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="rounded-xl bg-primary px-5 py-2.5 text-xs font-bold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {isSearching ? "Searching..." : "Search"}
          </button>
        </form>

        {/* Search Results Display */}
        {activeSearchResult && (
          <div className="rounded-xl border border-cyan/30 bg-cyan/5 p-4 space-y-3 animate-in fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-cyan uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5" /> Grounded Evidence Intelligence Synthesis
              </span>
              <span className="text-[10px] text-muted-foreground font-mono">
                {activeSearchResult.total_matches} matches
              </span>
            </div>

            <div className="rounded-lg bg-card p-3 border border-border text-xs text-foreground leading-relaxed whitespace-pre-wrap">
              {activeSearchResult.answer}
            </div>

            {/* Citations */}
            {activeSearchResult.citations.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-[10px] uppercase font-bold text-muted-foreground">
                  Evidentiary Citations:
                </p>
                <div className="flex flex-wrap gap-2">
                  {activeSearchResult.citations.map((c, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => onOpenEvidence && onOpenEvidence(c.evidence_id)}
                      className="rounded-lg border border-primary/30 bg-primary/10 px-2.5 py-1 text-xs font-mono text-primary hover:bg-primary/20 transition-colors flex items-center gap-1.5"
                      title="Inspect evidence details"
                    >
                      <FileText className="h-3 w-3" />
                      <span>
                        {c.reference}: {c.evidence_name}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI Investigation Summary Generator */}
      <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <FileText className="h-4 w-4 text-emerald-500" /> AI-Assisted Case Investigation
              Summary
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Comprehensive case intelligence report clearly distinguishing investigator-verified
              facts from unverified AI recommendations.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={isSummarizing}
              onClick={handleSummarize}
              className="inline-flex items-center gap-1.5 rounded-xl border border-border bg-background px-3.5 py-2 text-xs font-semibold text-foreground hover:bg-muted transition-colors disabled:opacity-50"
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              {isSummarizing ? "Compiling..." : "Generate AI Summary"}
            </button>
            {generatedSummary && (
              <>
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      const payload = await investigationApi.exportCaseIntelligence(caseId);
                      const blob = new Blob([JSON.stringify(payload, null, 2)], {
                        type: "application/json",
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `${caseNumber}-intelligence.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                      toast.success("Intelligence export downloaded");
                    } catch (err) {
                      toast.error(apiMessage(err, "Export failed"));
                    }
                  }}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-border bg-background px-3.5 py-2 text-xs font-semibold text-foreground hover:bg-muted transition-colors"
                >
                  <Download className="h-3.5 w-3.5" /> Export JSON
                </button>
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                  <Printer className="h-3.5 w-3.5" /> Print / Export
                </button>
              </>
            )}
          </div>
        </div>

        {generatedSummary && (
          <div className="rounded-xl border border-border bg-background p-5 space-y-4 text-xs animate-in fade-in">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h4 className="text-sm font-bold text-foreground">{generatedSummary.title}</h4>
                <p className="text-muted-foreground text-[11px]">
                  Case: {generatedSummary.case_number} · Compiled: {generatedSummary.generated_at}
                </p>
              </div>
              <span className="rounded-md bg-muted px-2.5 py-1 text-xs font-mono uppercase text-primary">
                {generatedSummary.status}
              </span>
            </div>

            {/* Overview Summary text */}
            <p className="text-foreground leading-relaxed italic bg-card p-3 rounded-lg border border-border">
              "{generatedSummary.summary_text}"
            </p>

            {/* Columns: Verified Facts vs Unverified Recommendations */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-3.5 space-y-2">
                <h5 className="text-xs font-bold text-emerald-500 flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4" /> Officer-Verified Findings (
                  {generatedSummary.verified_findings.length})
                </h5>
                {generatedSummary.verified_findings.length === 0 ? (
                  <p className="text-[11px] text-muted-foreground italic">No leads verified yet.</p>
                ) : (
                  <div className="space-y-1.5">
                    {generatedSummary.verified_findings.map((f) => (
                      <div
                        key={f.id}
                        className="p-2 rounded bg-card border border-border text-[11px]"
                      >
                        <p className="font-semibold text-foreground">{f.title}</p>
                        <p className="text-muted-foreground mt-0.5">Note: {f.reviewer_note}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3.5 space-y-2">
                <h5 className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" /> Unverified AI Recommendations (
                  {generatedSummary.unverified_ai_leads.length})
                </h5>
                {generatedSummary.unverified_ai_leads.length === 0 ? (
                  <p className="text-[11px] text-muted-foreground italic">
                    All findings have been reviewed.
                  </p>
                ) : (
                  <div className="space-y-1.5">
                    {generatedSummary.unverified_ai_leads.map((f) => (
                      <div
                        key={f.id}
                        className="p-2 rounded bg-card border border-border text-[11px]"
                      >
                        <p className="font-semibold text-foreground">{f.title}</p>
                        <p className="text-muted-foreground mt-0.5">{f.why}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Disclaimer */}
            <p className="text-[10px] text-muted-foreground border-t border-border pt-2 italic">
              {generatedSummary.disclaimer}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
