import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Bot, Sparkles, ArrowRight, ShieldAlert, Layers } from "lucide-react";
import { investigationApi } from "@/services/investigationApi";

export function AIAssistant() {
  // Fetch active cases to pick current active case
  const casesQ = useQuery({
    queryKey: ["dashboard-ai-assistant-cases"],
    queryFn: async () => {
      const res = await investigationApi.listCases({ page: 1, page_size: 10 });
      return res.items || [];
    },
  });

  const cases = casesQ.data || [];
  const activeCase = cases.find((c) => c.case_number === "CS-2026-0003") || cases[0];

  // Fetch real risk assessment
  const riskQ = useQuery({
    queryKey: ["dashboard-ai-assistant-risk", activeCase?.id],
    queryFn: () => (activeCase ? investigationApi.getCaseRisk(activeCase.id) : null),
    enabled: !!activeCase?.id,
  });

  // Fetch correlations
  const corrQ = useQuery({
    queryKey: ["dashboard-ai-assistant-corr", activeCase?.id],
    queryFn: () => (activeCase ? investigationApi.getCaseCorrelations(activeCase.id) : null),
    enabled: !!activeCase?.id,
  });

  // Fetch entities
  const entQ = useQuery({
    queryKey: ["dashboard-ai-assistant-ent", activeCase?.id],
    queryFn: () => (activeCase ? investigationApi.getCaseEntities(activeCase.id) : null),
    enabled: !!activeCase?.id,
  });

  const risk = riskQ.data || {
    risk_score: 45,
    risk_level: "MEDIUM",
    top_factors: ["Multi-source recurrence", "Entity cross-matching"],
  };
  const correlationsCount = corrQ.data?.length || 0;
  const entitiesCount = entQ.data?.length || 0;

  return (
    <div className="rounded-2xl border border-cyan/20 bg-gradient-to-br from-[#111827] to-[#0F172A] p-5 shadow-[0_0_40px_-18px_rgba(6,182,212,0.55)]">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-cyan/15 text-cyan">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">AI Investigation Panel</h3>
            <p className="text-[11px] text-slate-400">
              {activeCase
                ? `Case ${activeCase.case_number} Live Insights`
                : "Automated Evidence Intelligence"}
            </p>
          </div>
        </div>
        <span className="rounded-full bg-cyan/10 border border-cyan/30 px-2 py-0.5 text-[10px] font-semibold text-cyan uppercase tracking-wider">
          Decision Support
        </span>
      </div>

      <div className="grid gap-2.5 sm:grid-cols-2">
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <p className="text-[11px] text-slate-400">Cross-Evidence Matches</p>
          <p className="mt-1 text-sm font-semibold text-cyan">{correlationsCount} correlations</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <p className="text-[11px] text-slate-400">Extracted Entities</p>
          <p className="mt-1 text-sm font-semibold text-slate-100">{entitiesCount} identifiers</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <p className="text-[11px] text-slate-400">Forensic Modalities</p>
          <p className="mt-1 text-sm font-semibold text-slate-100">EXIF · OCR · Audio · CDR</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <p className="text-[11px] text-slate-400">Grounding RAG</p>
          <p className="mt-1 text-sm font-semibold text-emerald-400">Active</p>
        </div>
      </div>

      <div
        className={`mt-4 rounded-xl border p-3 ${
          risk.risk_score >= 70
            ? "border-red-500/30 bg-red-500/10 text-red-300"
            : risk.risk_score >= 40
              ? "border-amber-500/30 bg-amber-500/10 text-amber-300"
              : "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
        }`}
      >
        <div className="flex items-center justify-between">
          <p className="text-[11px] font-semibold uppercase tracking-wider">Case Risk Score</p>
          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-black/20">
            {risk.risk_level}
          </span>
        </div>
        <p className="text-2xl font-bold mt-0.5">
          {risk.risk_score}
          <span className="text-sm font-normal opacity-70"> / 100</span>
        </p>
        <p className="mt-1 text-xs text-slate-300/80 truncate">
          Top factor: {risk.top_factors?.[0] || "Cross-source investigative signals"}
        </p>
      </div>

      <Link
        to="/dashboard/ai-analysis"
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-cyan/20 border border-cyan/40 hover:bg-cyan/30 text-cyan py-2.5 text-xs font-bold transition-all shadow-sm"
      >
        <Sparkles className="h-4 w-4" /> Open Full AI Intelligence Hub{" "}
        <ArrowRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}
