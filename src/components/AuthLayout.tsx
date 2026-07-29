import { Link } from "@tanstack/react-router";
import { Shield } from "lucide-react";
import type { ReactNode } from "react";
import { ParticleBackground } from "./ParticleBackground";
import { ShieldGraphic } from "./ShieldGraphic";

export function AuthLayout({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <div className="relative min-h-screen">
      <ParticleBackground />
      <div className="mx-auto grid min-h-screen max-w-7xl grid-cols-1 items-center gap-10 px-5 py-10 lg:grid-cols-2 lg:gap-16">
        <div className="animate-rise-in w-full">
          <Link to="/" className="mb-8 inline-flex items-center gap-2">
            <Shield className="h-6 w-6 text-violet-glow" />
            <span className="font-display text-lg font-semibold tracking-tight">Cyber Shield</span>
          </Link>
          <div className="animated-glow-border glass-card rounded-2xl p-6 sm:p-8">
            <h1 className="text-2xl font-semibold sm:text-3xl">{title}</h1>
            <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
            <div className="mt-7">{children}</div>
          </div>
        </div>
        <div className="animate-rise-in order-first lg:order-last" style={{ animationDelay: "0.15s" }}>
          <ShieldGraphic priority />
        </div>
      </div>
    </div>
  );
}
