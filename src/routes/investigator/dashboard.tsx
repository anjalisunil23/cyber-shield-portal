import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Briefcase, FileStack, GitBranch, NotebookPen, Timer, Upload } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from "recharts";
import {
  AiPlaceholderCard,
  ChartCard,
  PageHeader,
  Panel,
  QuickActionCard,
  SkeletonGrid,
} from "@/components/layouts/DashboardWidgets";
import { StatsCard } from "@/components/layouts/StatsCard";
import { investigationApi } from "@/services/investigationApi";

export const Route = createFileRoute("/investigator/dashboard")({
  component: InvestigatorDashboard,
});

function InvestigatorDashboard() {
  const navigate = useNavigate();
  const stats = useQuery({ queryKey: ["dashboard"], queryFn: () => investigationApi.dashboardStats() });
  const cases = useQuery({ queryKey: ["cases"], queryFn: () => investigationApi.listCases({ page_size: 20 }) });
  const activity = useQuery({ queryKey: ["activity"], queryFn: () => investigationApi.activity(1) });

  if (stats.isLoading) return <SkeletonGrid count={6} />;
  const d = stats.data;

  return (
    <div className="space-y-6">
      <PageHeader title="Investigator Workspace" subtitle="Upload evidence, add notes, and advance assigned cases" />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatsCard label="Assigned Cases" value={cases.data?.total || 0} icon={Briefcase} />
        <StatsCard label="Evidence Uploaded" value={d?.evidence_uploaded || 0} icon={FileStack} tone="cyan" delay={0.08} />
        <StatsCard label="Notes" value={(activity.data?.items || []).filter((a) => a.description.toLowerCase().includes("note")).length} icon={NotebookPen} tone="emerald" delay={0.12} />
        <StatsCard label="Pending Tasks" value={d?.active_cases || 0} icon={Timer} tone="amber" delay={0.16} />
        <StatsCard label="Manual Leads" value={0} hint="Create from a case" icon={GitBranch} delay={0.2} />
        <StatsCard label="Recent Activity" value={activity.data?.total || 0} icon={Timer} tone="primary" delay={0.24} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Evidence Upload Statistics">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={d?.evidence_types || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="type" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="count" fill="#06B6D4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
        <ChartCard title="Investigation Timeline">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={d?.monthly_cases || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Area type="monotone" dataKey="count" stroke="#3B82F6" fill="#3B82F633" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Assigned Cases">
          <ul className="space-y-2">
            {(cases.data?.items || []).slice(0, 8).map((c) => (
              <li key={c.id} className="text-sm text-slate-200">
                {c.case_number} — {c.title}
              </li>
            ))}
            {!cases.data?.items?.length && <p className="text-sm text-slate-500">No assigned cases yet</p>}
          </ul>
        </Panel>
        <Panel title="Recent Activity">
          <ul className="space-y-2">
            {(activity.data?.items || []).slice(0, 8).map((a) => (
              <li key={a.id} className="text-sm text-slate-300">
                {a.description}
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <QuickActionCard label="Upload Evidence" description="Attach files to a case" icon={Upload} onClick={() => void navigate({ to: "/investigator/upload" })} />
        <QuickActionCard label="Add Notes" description="Markdown investigation notes" icon={NotebookPen} onClick={() => void navigate({ to: "/investigator/notes" })} />
        <QuickActionCard label="Create Manual Lead" description="Track a new lead" icon={GitBranch} onClick={() => void navigate({ to: "/investigator/leads" })} />
        <QuickActionCard label="View Timeline" description="Chronological case events" icon={Timer} onClick={() => void navigate({ to: "/investigator/timeline" })} />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <AiPlaceholderCard title="OCR Results" blurb="Reserved on evidence.ocr_text" />
        <AiPlaceholderCard title="Speech-to-Text" blurb="Reserved on evidence.speech_transcript" />
        <AiPlaceholderCard title="Object Detection" blurb="Reserved on evidence.detected_objects" />
        <AiPlaceholderCard title="AI Leads" blurb="Manual leads only in Phase 1" />
      </div>
    </div>
  );
}
