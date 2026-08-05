import { PROFILE } from "@/services/dashboardData";

export function ProfileCard() {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#111827]/90 p-5">
      <h3 className="text-sm font-semibold text-slate-100">Investigator Profile</h3>
      <div className="mt-4 flex items-center gap-3">
        <div className="grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-primary to-cyan text-lg font-bold text-white">
          AM
        </div>
        <div>
          <p className="font-semibold text-slate-50">{PROFILE.name}</p>
          <p className="text-xs text-slate-400">{PROFILE.department}</p>
          <p className="text-xs text-cyan">{PROFILE.role}</p>
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <p className="text-[11px] text-slate-400">Cases Assigned</p>
          <p className="mt-1 text-xl font-bold text-slate-50">{PROFILE.casesAssigned}</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <p className="text-[11px] text-slate-400">Performance</p>
          <p className="mt-1 text-xl font-bold text-emerald-400">{PROFILE.performance}</p>
        </div>
      </div>
    </div>
  );
}
