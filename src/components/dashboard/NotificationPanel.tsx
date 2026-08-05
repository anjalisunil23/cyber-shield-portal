import { NOTIFICATIONS } from "@/services/dashboardData";
import { cn } from "@/lib/utils";

export function NotificationPanel() {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#111827]/90 p-5">
      <h3 className="text-sm font-semibold text-slate-100">Notifications</h3>
      <ul className="mt-4 space-y-3">
        {NOTIFICATIONS.map((n) => (
          <li key={n.id} className="rounded-xl border border-white/5 bg-white/[0.02] p-3">
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-medium text-slate-100">{n.title}</p>
              <span className="text-[10px] text-slate-500">{n.time}</span>
            </div>
            <p className="mt-1 text-xs text-slate-400">{n.detail}</p>
            <span
              className={cn(
                "mt-2 inline-block rounded-full px-2 py-0.5 text-[10px]",
                n.level === "danger" && "bg-red-500/15 text-red-400",
                n.level === "success" && "bg-emerald-500/15 text-emerald-400",
                n.level === "warning" && "bg-amber-500/15 text-amber-400",
                n.level === "info" && "bg-cyan-500/15 text-cyan-400",
              )}
            >
              {n.level}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
