import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Bell,
  Briefcase,
  CheckCircle2,
  Clock,
  FileStack,
  GitBranch,
  ShieldAlert,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from "recharts";
import { ChartCard, PageHeader, SkeletonGrid } from "@/components/layouts/DashboardWidgets";
import { StatsCard } from "@/components/layouts/StatsCard";
import { investigationApi } from "@/services/investigationApi";
import { useTheme } from "@/lib/theme";

export const Route = createFileRoute("/investigator/dashboard")({
  component: InvestigatorDashboard,
});

function InvestigatorDashboard() {
  const navigate = useNavigate();
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === "dark";

  const stats = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => investigationApi.dashboardStats(),
  });
  const cases = useQuery({
    queryKey: ["cases"],
    queryFn: () => investigationApi.listCases({ page_size: 50 }),
  });
  const notifsQ = useQuery({
    queryKey: ["notifications"],
    queryFn: () => investigationApi.listNotifications(),
  });

  if (stats.isLoading) return <SkeletonGrid count={6} />;
  const d = stats.data;
  const caseItems = cases.data?.items || [];

  const totalAssigned = cases.data?.total || caseItems.length;
  const inProgressCount = caseItems.filter((c) =>
    ["in_progress", "evidence_collection", "analysis", "open"].includes(c.status),
  ).length;
  const changesRequestedCount = caseItems.filter((c) => c.status === "changes_requested").length;
  const approvedCount = caseItems.filter((c) =>
    ["approved", "completed", "closed", "archived"].includes(c.status),
  ).length;
  const unreadNotifs = (notifsQ.data || []).filter((n) => !n.is_read).length;

  const chartGridStroke = isDark ? "#1f2937" : "#e2e8f0";
  const chartAxisStroke = "#64748b";
  const chartTooltipStyle = {
    backgroundColor: "var(--card)",
    borderColor: "var(--border)",
    borderRadius: "0.75rem",
    boxShadow: isDark
      ? "0 10px 15px -3px rgba(0, 0, 0, 0.5)"
      : "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
    color: "var(--foreground)",
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatsCard label="Cases" value={totalAssigned} icon={Briefcase} />
        <StatsCard label="In progress" value={inProgressCount} icon={Clock} tone="cyan" />
        <StatsCard
          label="Changes requested"
          value={changesRequestedCount}
          icon={AlertTriangle}
          tone="amber"
        />
        <StatsCard label="Closed" value={approvedCount} icon={CheckCircle2} tone="emerald" />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatsCard
          label="Evidence"
          value={d?.evidence_uploaded || 0}
          icon={FileStack}
          tone="cyan"
        />
        <StatsCard
          label="Leads to review"
          value={d?.lead_review?.pending || 0}
          icon={GitBranch}
          tone="amber"
        />
        <StatsCard
          label="High risk"
          value={(d?.risk_distribution?.high || 0) + (d?.risk_distribution?.critical || 0)}
          icon={ShieldAlert}
          tone="rose"
        />
        <StatsCard label="Unread" value={unreadNotifs} icon={Bell} />
      </div>

      {/* Feedback Banner if Changes Requested */}
      {changesRequestedCount > 0 && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-amber-900 dark:text-amber-100 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm font-medium">
            {changesRequestedCount} case{changesRequestedCount > 1 ? "s" : ""} need revision
          </p>
          <button
            type="button"
            onClick={() => void navigate({ to: "/investigator/cases" })}
            className="rounded-lg bg-amber-500 px-3 py-1.5 text-xs font-semibold text-slate-950 hover:bg-amber-400"
          >
            Review
          </button>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Evidence types">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={d?.evidence_types || []}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartGridStroke} />
                <XAxis dataKey="type" stroke={chartAxisStroke} fontSize={11} />
                <YAxis stroke={chartAxisStroke} fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  itemStyle={{ color: "var(--foreground)" }}
                />
                <Bar dataKey="count" fill={isDark ? "#06B6D4" : "#0284c7"} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
        <ChartCard title="Cases by month">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={d?.monthly_cases || []}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartGridStroke} />
                <XAxis dataKey="month" stroke={chartAxisStroke} fontSize={11} />
                <YAxis stroke={chartAxisStroke} fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  itemStyle={{ color: "var(--foreground)" }}
                />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#2563EB"
                  fill={isDark ? "#3B82F633" : "#2563EB20"}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Active Assigned Cases Roster */}
      <div className="rounded-xl border border-border bg-card p-4 space-y-3">
        <div className="flex items-center justify-between gap-2">
          <h3 className="text-sm font-medium text-foreground">Recent cases</h3>
          <button
            type="button"
            onClick={() => void navigate({ to: "/investigator/cases" })}
            className="text-xs font-medium text-primary hover:underline"
          >
            View all
          </button>
        </div>

        {caseItems.length === 0 ? (
          <p className="py-6 text-center text-xs text-muted-foreground">No cases assigned.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-foreground">
              <thead>
                <tr className="border-b border-border text-muted-foreground uppercase text-[10px] tracking-wider">
                  <th className="pb-2.5 font-semibold">Case</th>
                  <th className="pb-2.5 font-semibold">Title</th>
                  <th className="pb-2.5 font-semibold">Priority</th>
                  <th className="pb-2.5 font-semibold">Status</th>
                  <th className="pb-2.5 font-semibold">Updated</th>
                  <th className="pb-2.5 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40">
                {caseItems.slice(0, 6).map((c) => (
                  <tr key={c.id} className="hover:bg-muted/30 transition-colors">
                    <td className="py-2.5 font-bold text-primary">
                      <button
                        type="button"
                        onClick={() =>
                          void navigate({
                            to: "/dashboard/cases/$caseId",
                            params: { caseId: c.id },
                          })
                        }
                        className="hover:underline text-left"
                      >
                        {c.case_number}
                      </button>
                    </td>
                    <td className="py-2.5 font-medium max-w-xs truncate">{c.title}</td>
                    <td className="py-2.5">
                      <span
                        className={`inline-block rounded px-2 py-0.5 text-[10px] font-bold uppercase ${
                          c.priority === "critical"
                            ? "bg-rose-500/15 text-rose-500"
                            : c.priority === "high"
                              ? "bg-amber-500/15 text-amber-500"
                              : "bg-blue-500/15 text-blue-500"
                        }`}
                      >
                        {c.priority}
                      </span>
                    </td>
                    <td className="py-2.5">
                      <span className="inline-block rounded bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground uppercase">
                        {c.status.replace("_", " ")}
                      </span>
                    </td>
                    <td className="py-2.5 text-muted-foreground text-[11px]">
                      {new Date(c.updated_at).toLocaleDateString()}
                    </td>
                    <td className="py-2.5 text-right">
                      <button
                        type="button"
                        onClick={() =>
                          void navigate({
                            to: "/dashboard/cases/$caseId",
                            params: { caseId: c.id },
                          })
                        }
                        className="rounded-lg bg-primary/10 hover:bg-primary/20 text-primary px-2.5 py-1 text-xs font-semibold transition"
                      >
                        Open
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
