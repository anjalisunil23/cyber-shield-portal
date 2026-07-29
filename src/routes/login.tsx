import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { AuthLayout } from "@/components/AuthLayout";

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

const ROLES = ["Investigator", "Forensic Officer", "Supervisor", "Admin"];
const field =
  "mt-2 w-full rounded-xl border border-input bg-surface/40 px-4 py-3 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-violet-glow/70 focus:ring-2 focus:ring-ring/30";

function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState(ROLES[0]);

  return (
    <AuthLayout title="Sign in" subtitle="Access your cases, evidence and AI-assisted reports.">
      <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
        <div>
          <label htmlFor="identifier" className="text-sm font-medium">Email or username</label>
          <input id="identifier" type="text" autoComplete="username" placeholder="officer@agency.gov" className={field} />
        </div>

        <div>
          <label htmlFor="password" className="text-sm font-medium">Password</label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="••••••••"
              className={`${field} pr-12`}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              aria-label={showPassword ? "Hide password" : "Show password"}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <div>
          <span className="text-sm font-medium">Role</span>
          <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
            {ROLES.map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRole(r)}
                className={`rounded-xl border px-2 py-2 text-xs font-medium transition-all ${
                  role === r
                    ? "border-violet-glow/70 bg-accent/60 text-foreground shadow-[0_0_22px_-8px_rgba(168,85,247,0.9)]"
                    : "border-border text-muted-foreground hover:text-foreground"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
          <label className="flex items-center gap-2 text-muted-foreground">
            <input type="checkbox" className="h-4 w-4 rounded border-input bg-surface/40 accent-primary" />
            Remember me
          </label>
          <a href="#" className="text-violet-glow hover:underline">Forgot password?</a>
        </div>

        <button type="submit" className="btn-violet w-full rounded-xl py-3 text-sm font-semibold">
          Login
        </button>

        <p className="text-center text-sm text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link to="/register" className="text-violet-glow hover:underline">Register</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
