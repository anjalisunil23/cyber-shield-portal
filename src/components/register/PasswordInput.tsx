import { Check, Eye, EyeOff, Lock, X } from "lucide-react";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

export type PasswordChecks = {
  length: boolean;
  upper: boolean;
  number: boolean;
  special: boolean;
};

export function getPasswordChecks(password: string): PasswordChecks {
  return {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    number: /\d/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };
}

export function passwordStrong(checks: PasswordChecks) {
  return checks.length && checks.upper && checks.number && checks.special;
}

export function PasswordInput({
  label,
  name,
  value,
  onChange,
  showStrength = false,
  autoComplete = "new-password",
}: {
  label: string;
  name: string;
  value: string;
  onChange: (v: string) => void;
  showStrength?: boolean;
  autoComplete?: string;
}) {
  const [show, setShow] = useState(false);
  const checks = useMemo(() => getPasswordChecks(value), [value]);
  const score = Object.values(checks).filter(Boolean).length;

  return (
    <div className="space-y-2">
      <label className="block space-y-1.5" htmlFor={name}>
        <span className="text-xs font-medium text-slate-300">{label}</span>
        <span className="relative block">
          <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            id={name}
            name={name}
            type={show ? "text" : "password"}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            autoComplete={autoComplete}
            required
            className="w-full rounded-2xl border border-white/[0.08] bg-[#0B1220] py-3 pl-10 pr-11 text-sm text-slate-50 outline-none transition placeholder:text-slate-500 focus:border-primary/60 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.2)]"
            placeholder="••••••••"
          />
          <button
            type="button"
            onClick={() => setShow((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-slate-200"
            aria-label={show ? "Hide password" : "Show password"}
          >
            {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </span>
      </label>

      {showStrength && value.length > 0 && (
        <div className="space-y-2">
          <div className="flex gap-1.5">
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition",
                  i < score
                    ? score <= 2
                      ? "bg-amber-400"
                      : score === 3
                        ? "bg-cyan"
                        : "bg-emerald-400"
                    : "bg-white/10",
                )}
              />
            ))}
          </div>
          <ul className="grid grid-cols-2 gap-1.5 text-[11px]">
            <CheckItem ok={checks.length} label="8 characters" />
            <CheckItem ok={checks.upper} label="Uppercase" />
            <CheckItem ok={checks.number} label="Number" />
            <CheckItem ok={checks.special} label="Special character" />
          </ul>
        </div>
      )}
    </div>
  );
}

function CheckItem({ ok, label }: { ok: boolean; label: string }) {
  return (
    <li className={cn("flex items-center gap-1.5", ok ? "text-emerald-400" : "text-slate-500")}>
      {ok ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
      {label}
    </li>
  );
}
