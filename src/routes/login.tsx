import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Eye, EyeOff, Fingerprint, Lock, Shield, User } from "lucide-react";
import { ParticleBackground } from "@/components/ParticleBackground";
import { CyberGlobe } from "@/components/CyberGlobe";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Login — Cyber Shield" },
      { name: "description", content: "Sign in to the Cyber Shield investigation support platform." },
      { property: "og:title", content: "Login — Cyber Shield" },
      { property: "og:description", content: "Secure access for investigators, forensic officers and supervisors." },
    ],
  }),
  component: LoginPage,
});

const ROLES = [
  { label: "Investigator", to: "/dashboard/investigator" as const },
  { label: "Supervisor", to: "/dashboard/supervisor" as const },
  { label: "Admin", to: "/dashboard/admin" as const },
];

export function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState(ROLES[0]);
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen">
      <ParticleBackground />

      <div className="mx-auto grid min-h-screen max-w-7xl items-center gap-12 px-5 py-12 lg:grid-cols-[minmax(0,1fr)_420px] lg:gap-8">
        <div className="animate-rise-in">
          <Link to="/" className="mb-8 inline-flex items-center gap-2">
            <Shield className="h-6 w-6 text-violet-glow" />
            <span className="font-display text-lg font-semibold tracking-tight">Cyber Shield</span>
          </Link>
          <h1 className="max-w-lg text-3xl font-bold leading-tight sm:text-4xl">
            Secure access to your <span className="text-gradient-violet">digital evidence</span> workspace
          </h1>
          <p className="mt-4 max-w-md text-sm text-muted-foreground sm:text-base">
            Encrypted sessions, role-based permissions and a full audit trail on every case action.
          </p>
          <div className="mt-8">
            <CyberGlobe />
          </div>
        </div>

        <div className="animate-rise-in w-full" style={{ animationDelay: "0.12s" }}>
          <div className="relative mt-9">
            <div
              className="absolute -top-9 left-1/2 z-20 grid h-[72px] w-[72px] -translate-x-1/2 place-items-center rounded-full border border-violet-glow/60 bg-surface/80 backdrop-blur-md"
              style={{ boxShadow: "0 0 38px -8px rgba(168,85,247,0.95)" }}
            >
              <Fingerprint className="h-9 w-9 text-violet-glow" />
            </div>

            <div className="animated-glow-border glass-card rounded-2xl px-6 pb-7 pt-12 sm:px-8">
              <h2 className="text-center text-xl font-semibold">Sign in</h2>
              <p className="mt-1 text-center text-xs text-muted-foreground">
                Biometric-grade authentication for authorised officers
              </p>

              <form
                className="mt-7 space-y-4"
                onSubmit={(e) => {
                  e.preventDefault();
                  navigate({ to: role.to });
                }}
              >
                <label className="flex items-center gap-3 rounded-xl border border-input bg-surface/40 px-3.5 py-3 transition-colors focus-within:border-violet-glow/70">
                  <User className="h-4 w-4 shrink-0 text-violet-glow" />
                  <input
                    type="text"
                    autoComplete="username"
                    placeholder="Username"
                    aria-label="Username"
                    className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
                  />
                </label>

                <label className="flex items-center gap-3 rounded-xl border border-input bg-surface/40 px-3.5 py-3 transition-colors focus-within:border-violet-glow/70">
                  <Lock className="h-4 w-4 shrink-0 text-violet-glow" />
                  <input
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="Password"
                    aria-label="Password"
                    className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    className="text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </label>

                <div className="grid grid-cols-3 gap-2">
                  {ROLES.map((r) => (
                    <button
                      key={r.label}
                      type="button"
                      onClick={() => setRole(r)}
                      className={`rounded-lg border px-2 py-2 text-[11px] font-medium transition-all ${
                        role.label === r.label
                          ? "border-violet-glow/70 bg-accent/60 text-foreground shadow-[0_0_22px_-8px_rgba(168,85,247,0.9)]"
                          : "border-border text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>

                <div className="flex items-center justify-between text-xs">
                  <label className="flex items-center gap-2 text-muted-foreground">
                    <input type="checkbox" className="h-3.5 w-3.5 rounded border-input bg-surface/40 accent-primary" />
                    Remember me
                  </label>
                  <a href="#" className="text-violet-glow hover:underline">Forgot password?</a>
                </div>

                <button type="submit" className="btn-violet w-full rounded-xl py-3 text-sm font-semibold">
                  LOGIN
                </button>

                <Link
                  to="/register"
                  className="block w-full rounded-xl border border-violet-glow/45 py-3 text-center text-sm font-semibold text-foreground transition-colors hover:bg-accent/40"
                >
                  REGISTER
                </Link>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
