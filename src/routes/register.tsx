import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { AuthLayout } from "@/components/AuthLayout";

export const Route = createFileRoute("/register")({
  head: () => ({
    meta: [
      { title: "Create Account — Cyber Shield" },
      {
        name: "description",
        content: "Register for Cyber Shield to manage digital evidence with explainable AI support.",
      },
      { property: "og:title", content: "Create Account — Cyber Shield" },
      {
        property: "og:description",
        content: "Request access as an investigator, forensic officer or supervisor.",
      },
    ],
  }),
  component: RegisterPage,
});

const ROLES = ["Investigator", "Forensic Officer", "Supervisor"];
const field =
  "mt-2 w-full rounded-xl border border-input bg-surface/40 px-4 py-3 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-violet-glow/70 focus:ring-2 focus:ring-ring/30";

function RegisterPage() {
  const [show, setShow] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  return (
    <AuthLayout
      title="Create account"
      subtitle="Set up your Cyber Shield workspace with role-based access."
    >
      <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
        <div>
          <label htmlFor="name" className="text-sm font-medium">Full name</label>
          <input id="name" type="text" autoComplete="name" placeholder="Alex Mercer" className={field} />
        </div>

        <div>
          <label htmlFor="email" className="text-sm font-medium">Email</label>
          <input id="email" type="email" autoComplete="email" placeholder="alex.mercer@agency.gov" className={field} />
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label htmlFor="password" className="text-sm font-medium">Password</label>
            <div className="relative">
              <input
                id="password"
                type={show ? "text" : "password"}
                autoComplete="new-password"
                placeholder="••••••••"
                className={`${field} pr-12`}
              />
              <button
                type="button"
                onClick={() => setShow((v) => !v)}
                aria-label={show ? "Hide password" : "Show password"}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
              >
                {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <div>
            <label htmlFor="confirm" className="text-sm font-medium">Confirm password</label>
            <div className="relative">
              <input
                id="confirm"
                type={showConfirm ? "text" : "password"}
                autoComplete="new-password"
                placeholder="••••••••"
                className={`${field} pr-12`}
              />
              <button
                type="button"
                onClick={() => setShowConfirm((v) => !v)}
                aria-label={showConfirm ? "Hide password" : "Show password"}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
              >
                {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label htmlFor="role" className="text-sm font-medium">Role</label>
            <select id="role" className={field} defaultValue={ROLES[0]}>
              {ROLES.map((r) => (
                <option key={r} value={r} className="bg-popover">{r}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="dept" className="text-sm font-medium">
              Department / unit <span className="text-muted-foreground">(optional)</span>
            </label>
            <input id="dept" type="text" placeholder="Cyber Crime Unit" className={field} />
          </div>
        </div>

        <label className="flex items-start gap-3 text-sm text-muted-foreground">
          <input type="checkbox" className="mt-0.5 h-4 w-4 shrink-0 rounded border-input bg-surface/40 accent-primary" />
          I agree to the data handling and ethical use policy
        </label>

        <button type="submit" className="btn-violet w-full rounded-xl py-3 text-sm font-semibold">
          Create Account
        </button>

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link to="/login" className="text-violet-glow hover:underline">Login</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
