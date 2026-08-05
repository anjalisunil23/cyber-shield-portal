import { ACTIVITY } from "@/services/dashboardData";

export function ActivityFeed() {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#111827]/90 p-5">
      <h3 className="text-sm font-semibold text-slate-100">Activity Feed</h3>
      <ul className="mt-4 space-y-3">
        {ACTIVITY.map((a) => (
          <li key={a.id} className="flex gap-3">
            <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-cyan shadow-[0_0_10px_rgba(6,182,212,0.8)]" />
            <div>
              <p className="text-sm text-slate-200">{a.text}</p>
              <p className="text-[11px] text-slate-500">{a.time}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
