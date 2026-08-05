import { createFileRoute } from "@tanstack/react-router";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
} from "recharts";
import { ChartCard, PageScaffold } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/major-admin/analytics")({ component: Page });

const monthly = [
  { m: "Mar", c: 12 },
  { m: "Apr", c: 18 },
  { m: "May", c: 15 },
  { m: "Jun", c: 22 },
  { m: "Jul", c: 28 },
  { m: "Aug", c: 19 },
];
const growth = [
  { m: "Mar", u: 40 },
  { m: "Apr", u: 48 },
  { m: "May", u: 55 },
  { m: "Jun", u: 61 },
  { m: "Jul", u: 70 },
  { m: "Aug", u: 78 },
];
const radar = [
  { subject: "CCU", A: 120 },
  { subject: "DFL", A: 98 },
  { subject: "DHQ", A: 86 },
  { subject: "SOC", A: 65 },
];

function Page() {
  return (
    <PageScaffold
      crumbs={[{ label: "Major Admin", to: "/major-admin/dashboard" }, { label: "Analytics" }]}
      title="System Analytics"
      subtitle="Platform trends (mock)"
    >
      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Monthly cases">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="m" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="c" fill="#3B82F6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
        <ChartCard title="User growth">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={growth}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="m" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Line type="monotone" dataKey="u" stroke="#06B6D4" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
        <ChartCard title="Department load">
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radar}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} />
                <Radar dataKey="A" stroke="#3B82F6" fill="#3B82F644" />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>
    </PageScaffold>
  );
}
