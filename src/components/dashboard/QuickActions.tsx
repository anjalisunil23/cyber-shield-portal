import { BrainCircuit, FileSearch, FolderPlus, Search, Upload, UserPlus } from "lucide-react";
import { toast } from "sonner";

const ACTIONS = [
  { label: "Create New Case", icon: FolderPlus },
  { label: "Upload Evidence", icon: Upload },
  { label: "Run AI Analysis", icon: BrainCircuit },
  { label: "Search Evidence", icon: Search },
  { label: "Generate Report", icon: FileSearch },
  { label: "Invite Investigator", icon: UserPlus },
];

export function QuickActions() {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#111827]/90 p-5">
      <h3 className="text-sm font-semibold text-slate-100">Quick Actions</h3>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {ACTIONS.map(({ label, icon: Icon }) => (
          <button
            key={label}
            type="button"
            onClick={() => toast.success(label)}
            className="group flex min-h-[88px] flex-col items-start justify-between rounded-2xl border border-white/10 bg-gradient-to-br from-primary/10 to-cyan/5 p-4 text-left transition hover:border-cyan/40 hover:shadow-[0_0_30px_-12px_rgba(6,182,212,0.6)]"
          >
            <Icon className="h-5 w-5 text-primary group-hover:text-cyan" />
            <span className="text-sm font-semibold text-slate-100">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
