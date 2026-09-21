import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function GlassPanel({
  children,
  className,
  glow = false,
  ...props
}: HTMLAttributes<HTMLDivElement> & { children: ReactNode; glow?: boolean }) {
  return (
    <div
      className={cn("glass-card relative overflow-hidden", glow && "glow-hover", className)}
      {...props}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent"
      />
      {children}
    </div>
  );
}
