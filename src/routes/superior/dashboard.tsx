import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Briefcase, CheckCircle2, FileStack, FileText, Users } from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, BarChart, Bar, CartesianGrid, XAxis, YAxis } from "recharts";
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

export const Route = createFileRoute("/superior/dashboard")({
  component: SuperiorDashboard,
});

const COLORS = ["#3B82F6", "#06B6D4", "#F59E0B", "#EF4444"];

function SuperiorDashboard() {
  const navigate = useNavigate();
  const stats = useQuery({ queryKey: ["dashboard"], queryFn: () => investigationApi.dashboardStats() });
  const cases = useQuery({ queryKey: ["cases"], queryFn: () => investigationApi.listCases({ page_size: 20 }) });
  const users = useQuery({ queryKey: ["users"], queryFn: () => investigationApi.listUsers() });

  if (stats.isLoading) return <SkeletonGrid count={6} />;
  const d = stats.data;
  const highPriority = (cases.data?.items || []).filter((c) => c.priority === "high" || c.priority === "critical").length;
  const investigators = (users.data?.items || []).filter((u) => u.role === "investigator").length;

  return (
    <div className="space-y-6">
      <PageHeader title="Superior Officer Dashboard" subtitle="Head of investigation — assign, review, and close cases" />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatsCard label="My Cases" value={cases.data?.total || 0} icon={Briefcase} />
        <StatsCard label="Pending Reviews" value={d?.active_cases || 0} icon={FileText} tone="amber" delay={0.08} />
        <StatsCard label="High Priority" value={highPriority} icon={AlertTriangle} tone="rose" delay={0.12} />
        <StatsCard label="Evidence Count" value={d?.evidence_uploaded || 0} icon={FileStack} tone="cyan" delay={0.16} />
        <StatsCard label="Pending Reports" value={d?.reports || 0} icon={FileText} delay={0.2} />
        <StatsCard label="Investigators" value={investigators} icon={Users} tone="emerald" delay={0.24} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Investigation Progress">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={d?.monthly_cases || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
        <ChartCard title="Priority Distribution">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={d?.priority_distribution || []} dataKey="count" nameKey="priority" outerRadius={80}>
                  {(d?.priority_distribution || []).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Assigned Cases">
          <ul className="space-y-2">
            {(cases.data?.items || []).slice(0, 8).map((c) => (
              <li key={c.id} className="flex justify-between gap-2 text-sm">
                <span className="truncate text-slate-200">{c.title}</span>
                <span className="shrink-0 text-xs text-cyan">{c.priority}</span>
              </li>
            ))}
          </ul>
        </Panel>
        <Panel title="Latest Uploads">
          <ul className="space-y-2">
            {(d?.latest_uploads || []).map((e) => (
              <li key={e.id} className="text-sm text-slate-300">
                {e.original_name}
              </li>
            ))}
            {!d?.latest_uploads?.length && <p className="text-sm text-slate-500">No uploads yet</p>}
          </ul>
        </Panel>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <QuickActionCard label="Create Case" description="Open a new investigation" icon={Briefcase} onClick={() => void navigate({ to: "/superior/cases" })} />
        <QuickActionCard label="Assign Investigator" description="Delegate case ownership" icon={Users} onClick={() => void navigate({ to: "/superior/investigators" })} />
        <QuickActionCard label="Review Evidence" description="Evidence review queue" icon={FileStack} onClick={() => void navigate({ to: "/superior/evidence" })} />
        <QuickActionCard label="Generate Report" description="Investigation summary" icon={FileText} onClick={() => void navigate({ to: "/superior/reports" })} />
        <QuickActionCard label="Close Case" description="Complete and archive" icon={CheckCircle2} onClick={() => void navigate({ to: "/superior/cases" })} />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <AiPlaceholderCard title="AI Suggestions" blurb="Review AI findings placeholder — Phase 2." />
        <AiPlaceholderCard title="Timeline Reconstruction" blurb="Automated timeline reserved." />
        <AiPlaceholderCard title="Face Detection" blurb="Will attach to evidence records later." />
        <AiPlaceholderCard title="Risk Assessment" blurb="Case risk score placeholder." />
      </div>
    </div>
  );
}
