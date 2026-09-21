import { AlertCircle, CheckCircle2, Loader2, type LucideIcon } from "lucide-react";
import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  icon: LucideIcon;
  error?: string | null;
  success?: string | null;
  isValid?: boolean;
  isTouched?: boolean;
  isLoading?: boolean;
};

export function InputField({
  label,
  icon: Icon,
  className,
  id,
  error,
  success,
  isValid,
  isTouched,
  isLoading,
  ...props
}: Props) {
  const inputId = id ?? props.name ?? label.toLowerCase().replace(/\s+/g, "-");
  const showError = Boolean(error && isTouched);
  const showSuccess = Boolean(!showError && !isLoading && isTouched && (success || isValid));
  const messageId = showError ? `${inputId}-error` : showSuccess ? `${inputId}-status` : undefined;

  return (
    <label className="block space-y-1.5" htmlFor={inputId}>
      <span className="flex items-center justify-between text-xs font-medium text-slate-300">
        <span>{label}</span>
        {isLoading && (
          <span className="flex items-center gap-1 text-[11px] text-cyan">
            <Loader2 className="h-3 w-3 animate-spin" />
            Checking…
          </span>
        )}
      </span>
      <span className="relative block">
        <Icon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500 transition-colors" />
        <input
          id={inputId}
          aria-invalid={showError ? "true" : "false"}
          aria-describedby={messageId}
          className={cn(
            "w-full rounded-2xl border bg-[#0B1220] py-3 pl-10 pr-10 text-sm text-slate-50 outline-none transition duration-200",
            "placeholder:text-slate-500",
            "border-white/[0.08] focus:border-primary/60 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.2)]",
            showError &&
              "border-red-500/60 focus:border-red-500 focus:shadow-[0_0_0_3px_rgba(239,68,68,0.2)]",
            showSuccess &&
              "border-emerald-500/50 focus:border-emerald-500 focus:shadow-[0_0_0_3px_rgba(16,185,129,0.2)]",
            className,
          )}
          {...props}
        />
        {isLoading ? (
          <Loader2 className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-cyan" />
        ) : showError ? (
          <AlertCircle className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-red-400" />
        ) : showSuccess ? (
          <CheckCircle2 className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-emerald-400" />
        ) : null}
      </span>
      {showError && (
        <span
          id={`${inputId}-error`}
          role="alert"
          className="flex items-center gap-1.5 text-xs text-red-400"
        >
          {error}
        </span>
      )}
      {showSuccess && success && (
        <span
          id={`${inputId}-status`}
          role="status"
          className="flex items-center gap-1.5 text-xs text-emerald-400"
        >
          {success}
        </span>
      )}
    </label>
  );
}
