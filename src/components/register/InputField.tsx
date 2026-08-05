import type { LucideIcon } from "lucide-react";
import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  icon: LucideIcon;
  error?: string;
};

export function InputField({ label, icon: Icon, className, id, error, ...props }: Props) {
  const inputId = id ?? props.name ?? label.toLowerCase().replace(/\s+/g, "-");

  return (
    <label className="block space-y-1.5" htmlFor={inputId}>
      <span className="text-xs font-medium text-slate-300">{label}</span>
      <span className="relative block">
        <Icon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          id={inputId}
          className={cn(
            "w-full rounded-2xl border border-white/[0.08] bg-[#0B1220] py-3 pl-10 pr-3 text-sm text-slate-50 outline-none transition",
            "placeholder:text-slate-500",
            "focus:border-primary/60 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.2)]",
            error && "border-red-500/50",
            className,
          )}
          {...props}
        />
      </span>
      {error && <span className="text-xs text-red-400">{error}</span>}
    </label>
  );
}
