import { Badge, priorityBadgeClass, statusBadgeClass } from "@/components/dashboard/Badge";
import { PRIORITY_QUEUE } from "@/services/dashboardData";

export function PriorityQueue() {
  return (
    <div className="overflow-x-auto rounded-2xl border border-white/10 bg-[#111827]/90">
      <div className="border-b border-white/10 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-100">Priority Queue</h3>
      </div>
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-5 py-3 font-medium">Case Name</th>
            <th className="px-5 py-3 font-medium">Priority</th>
            <th className="px-5 py-3 font-medium">Deadline</th>
            <th className="px-5 py-3 font-medium">Assigned To</th>
            <th className="px-5 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {PRIORITY_QUEUE.map((r) => (
            <tr key={r.name} className="border-t border-white/5">
              <td className="px-5 py-3 text-slate-200">{r.name}</td>
              <td className="px-5 py-3">
                <Badge className={priorityBadgeClass(r.priority)}>{r.priority}</Badge>
              </td>
              <td className="px-5 py-3 text-slate-400">{r.deadline}</td>
              <td className="px-5 py-3 text-slate-300">{r.assignee}</td>
              <td className="px-5 py-3">
                <Badge className={statusBadgeClass(r.status)}>{r.status}</Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
