import { TIMELINE_EVENTS } from "@/services/dashboardData";

export function Timeline() {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#111827]/90 p-5">
      <h3 className="text-sm font-semibold text-slate-100">Timeline View</h3>
      <ol className="relative mt-6 space-y-5 border-l border-white/10 pl-5">
        {TIMELINE_EVENTS.map((e) => (
          <li key={e.title} className="relative">
            <span className="absolute -left-[27px] top-1 h-3 w-3 rounded-full border-2 border-[#111827] bg-cyan" />
            <p className="text-sm font-medium text-slate-100">{e.title}</p>
            <p className="mt-0.5 text-xs text-slate-400">{e.detail}</p>
            <p className="mt-1 text-[11px] text-slate-500">{e.time}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
