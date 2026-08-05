import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { investigationApi } from "@/services/investigationApi";

export const Route = createFileRoute("/dashboard/team")({
  component: TeamPage,
});

function TeamPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: () => investigationApi.listUsers(),
  });

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-50">Investigators</h1>
        <p className="text-sm text-slate-400">Team directory for case assignment</p>
      </div>
      {isLoading && <p className="text-sm text-slate-400">Loading…</p>}
      <div className="overflow-x-auto rounded-2xl border border-white/10 bg-[#111827]/90">
        <table className="w-full min-w-[560px] text-left text-sm">
          <thead className="border-b border-white/10 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
            </tr>
          </thead>
          <tbody>
            {(data?.items || []).map((u) => (
              <tr key={u.id} className="border-b border-white/5">
                <td className="px-4 py-3 text-slate-200">{u.full_name}</td>
                <td className="px-4 py-3 text-slate-400">{u.email}</td>
                <td className="px-4 py-3 text-cyan">{u.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
