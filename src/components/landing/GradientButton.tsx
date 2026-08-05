import { Link } from "@tanstack/react-router";
import type { ComponentProps, ReactNode } from "react";
import { cn } from "@/lib/utils";

type Common = {
  children: ReactNode;
  className?: string;
  variant?: "primary" | "secondary" | "ghost";
};

export function GradientButton({
  children,
  className,
  variant = "primary",
  ...props
}: Common & ComponentProps<"button">) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold transition-all",
        variant === "primary" && "btn-brand",
        variant === "secondary" &&
          "border border-white/15 bg-white/5 text-foreground hover:border-primary/40 hover:bg-white/10",
        variant === "ghost" && "text-muted-foreground hover:text-foreground",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export function GradientLink({
  children,
  className,
  variant = "primary",
  to,
  href,
}: Common & { to?: string; href?: string }) {
  const classes = cn(
    "inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold transition-all",
    variant === "primary" && "btn-brand",
    variant === "secondary" &&
      "border border-white/15 bg-white/5 text-foreground hover:border-primary/40 hover:bg-white/10",
    variant === "ghost" && "text-muted-foreground hover:text-foreground",
    className,
  );

  if (to) {
    return (
      <Link to={to as "/"} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <a href={href} className={classes}>
      {children}
    </a>
  );
}
