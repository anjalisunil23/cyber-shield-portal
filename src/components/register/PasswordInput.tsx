import { AlertCircle, Check, CheckCircle2, Eye, EyeOff, Lock, X } from "lucide-react";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

export type PasswordChecks = {
  length: boolean;
  upper: boolean;
  lower: boolean;
  number: boolean;
  special: boolean;
  noSpaces: boolean;
};

export function getPasswordChecks(password: string): PasswordChecks {
  return {
    length: password.length >= 8 && password.length <= 64,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[^A-Za-z0-9\s]/.test(password),
    noSpaces: password.length > 0 && !/\s/.test(password),
  };
}

export function passwordStrong(checks: PasswordChecks) {
  return (
    checks.length &&
    checks.upper &&
    checks.lower &&
    checks.number &&
    checks.special &&
    checks.noSpaces
  );
}

export function PasswordInput({
  label,
  name,
  value,
  onChange,
  showStrength = false,
  autoComplete = "new-password",
  error,
  success,
  isValid,
  isTouched,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (v: string) => void;
  showStrength?: boolean;
  autoComplete?: string;
  error?: string | null;
  success?: string | null;
  isValid?: boolean;
  isTouched?: boolean;
}) {
  const [show, setShow] = useState(false);
  const checks = useMemo(() => getPasswordChecks(value), [value]);
  const score = Object.values(checks).filter(Boolean).length;

  const showError = Boolean(error && isTouched);
  const showSuccess = Boolean(!showError && isTouched && (success || isValid));
  const messageId = showError ? `${name}-error` : showSuccess ? `${name}-status` : undefined;

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
            aria-invalid={showError ? "true" : "false"}
            aria-describedby={messageId}
            className={cn(
              "w-full rounded-2xl border bg-[#0B1220] py-3 pl-10 pr-11 text-sm text-slate-50 outline-none transition duration-200 placeholder:text-slate-500",
              "border-white/[0.08] focus:border-primary/60 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.2)]",
              showError &&
                "border-red-500/60 focus:border-red-500 focus:shadow-[0_0_0_3px_rgba(239,68,68,0.2)]",
              showSuccess &&
                "border-emerald-500/50 focus:border-emerald-500 focus:shadow-[0_0_0_3px_rgba(16,185,129,0.2)]",
            )}
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

      {showError && (
        <span
          id={`${name}-error`}
          role="alert"
          className="flex items-center gap-1.5 text-xs text-red-400"
        >
          {error}
        </span>
      )}
      {showSuccess && success && (
        <span
          id={`${name}-status`}
          role="status"
          className="flex items-center gap-1.5 text-xs text-emerald-400"
        >
          {success}
        </span>
      )}

      {showStrength && value.length > 0 && (
        <div className="space-y-2 rounded-xl border border-white/[0.05] bg-white/[0.02] p-2.5">
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span>Password requirements</span>
            <span
              className={cn(
                "font-medium",
                score <= 2 ? "text-amber-400" : score < 6 ? "text-cyan" : "text-emerald-400",
              )}
            >
              {score <= 2 ? "Weak" : score < 6 ? "Good" : "Strong"}
            </span>
          </div>
          <div className="flex gap-1.5">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition-all duration-300",
                  i < score
                    ? score <= 2
                      ? "bg-amber-400"
                      : score < 6
                        ? "bg-cyan"
                        : "bg-emerald-400"
                    : "bg-white/10",
                )}
              />
            ))}
          </div>
          <ul className="grid grid-cols-2 gap-1.5 text-[11px]">
            <CheckItem ok={checks.length} label="8–64 characters" />
            <CheckItem ok={checks.upper} label="One uppercase letter" />
            <CheckItem ok={checks.lower} label="One lowercase letter" />
            <CheckItem ok={checks.number} label="One number" />
            <CheckItem ok={checks.special} label="One special character" />
            <CheckItem ok={checks.noSpaces} label="No spaces" />
          </ul>
        </div>
      )}
    </div>
  );
}

function CheckItem({ ok, label }: { ok: boolean; label: string }) {
  return (
    <li
      className={cn(
        "flex items-center gap-1.5 transition-colors duration-200",
        ok ? "text-emerald-400" : "text-slate-500",
      )}
    >
      {ok ? <Check className="h-3.5 w-3.5 shrink-0" /> : <X className="h-3.5 w-3.5 shrink-0" />}
      <span>{label}</span>
    </li>
  );
}
