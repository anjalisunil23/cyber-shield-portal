import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Shield, Network, Sparkles, FileText, GitBranch, ScanEye,
  Briefcase, ShieldCheck, Settings2, Lock, Activity, ArrowRight,
} from "lucide-react";
import { ParticleBackground } from "@/components/ParticleBackground";
import { CyberGlobe } from "@/components/CyberGlobe";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Cyber Shield — AI-Powered Investigation Support Platform" },
      {
        name: "description",
        content:
          "Consolidate digital case evidence and generate explainable, AI-assisted reports for investigators, forensic officers and supervisors.",
      },
      { property: "og:title", content: "Cyber Shield — AI-Powered Investigation Support Platform" },
      {
        property: "og:description",
        content:
          "Evidence correlation, explainable lead scoring, forensic report integration and knowledge graphs — with human oversight at every step.",
      },
    ],
  }),
  component: Landing,
});

const FEATURES = [
  {
    Icon: Network,
    title: "Evidence Correlation",
    desc: "Link devices, communications, documents and media across a case to surface relationships analysts would otherwise miss.",
  },
  {
    Icon: Sparkles,
    title: "Explainable Lead Scoring",
    desc: "Every lead is ranked with the exact signals and evidence items that produced the score — never a black box.",
  },
  {
    Icon: FileText,
    title: "Forensic Report Integration",
    desc: "Ingest standard forensic tool exports and fold their findings directly into the case timeline and reporting.",
  },
  {
    Icon: GitBranch,
    title: "Knowledge Graph",
    desc: "Navigate entities, locations and events as an interactive graph with full provenance back to source evidence.",
  },
];

const STATS = [
  { value: "72%", label: "Less time spent collating evidence" },
  { value: "4x", label: "Faster first-pass report drafting" },
  { value: "100%", label: "Actions written to the audit trail" },
  { value: "0", label: "Autonomous AI decisions" },
];

const ROLES = [
  {
    Icon: Briefcase,
    title: "Investigator",
    to: "/dashboard/investigator" as const,
    points: ["Create and manage cases", "Log notes and evidence metadata", "Request forensic analysis", "Finalize AI-drafted reports"],
  },
  {
    Icon: ShieldCheck,
    title: "Supervisor",
    to: "/dashboard/supervisor" as const,
    points: ["Approve reports before closure", "Monitor caseloads and forensic workload", "Correct and rate AI summaries", "Assign forensic resources"],
  },
  {
    Icon: Settings2,
    title: "Admin",
    to: "/dashboard/admin" as const,
    points: ["Manage accounts and roles", "Maintain audit logs", "Track uptime and incidents", "Configure system settings"],
  },
];

const FLOW = [
  { step: "01", title: "Ingest", desc: "Evidence metadata, forensic exports and case notes land in one custody-tracked vault." },
  { step: "02", title: "Correlate", desc: "The engine links entities across sources and ranks leads with visible reasoning." },
  { step: "03", title: "Draft", desc: "An AI-assisted report is composed with every claim tied to its source evidence." },
  { step: "04", title: "Approve", desc: "Investigators finalize and supervisors sign off before anything is filed." },
];

function Landing() {
  return (
    <div className="relative min-h-screen">
      <ParticleBackground />

      <header className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-xl">
        <nav className="mx-auto grid max-w-7xl grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-5 py-3.5 md:flex md:justify-between">
          <Link to="/" className="flex min-w-0 items-center gap-2">
            <Shield className="h-6 w-6 shrink-0 text-violet-glow" />
            <span className="truncate font-display text-lg font-semibold tracking-tight">Cyber Shield</span>
          </Link>
          <div className="hidden items-center gap-8 text-sm text-muted-foreground md:flex">
            <a href="#features" className="transition-colors hover:text-foreground">Features</a>
            <a href="#roles" className="transition-colors hover:text-foreground">Roles</a>
            <a href="#workflow" className="transition-colors hover:text-foreground">Workflow</a>
            <a href="#about" className="transition-colors hover:text-foreground">About</a>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="rounded-xl border border-border px-4 py-2 text-sm font-medium transition-colors hover:border-violet-glow/60"
            >
              Login
            </Link>
            <Link to="/register" className="btn-violet rounded-xl px-4 py-2 text-sm font-medium">
              Get Started
            </Link>
          </div>
        </nav>
      </header>

      <main>
        <section className="mx-auto grid max-w-7xl items-center gap-12 px-5 py-16 lg:grid-cols-2 lg:py-24">
          <div className="animate-rise-in">
            <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">
              <ScanEye className="h-3.5 w-3.5 text-violet-glow" /> Digital forensics, augmented
            </span>
            <h1 className="mt-5 text-4xl font-bold leading-[1.08] sm:text-5xl lg:text-6xl">
              AI-Powered <span className="text-gradient-violet">Investigation Support</span> Platform
            </h1>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
              Cyber Shield consolidates case evidence from every source and generates explainable,
              AI-assisted reports for investigators, forensic officers and supervisors — so teams spend
              their time on judgement, not collation.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/register" className="btn-violet rounded-xl px-6 py-3 text-sm font-semibold">
                Get Started
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl border border-border px-6 py-3 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                View dashboards <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-3 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-2"><Lock className="h-4 w-4 text-violet-glow" /> End-to-end custody tracking</span>
              <span className="inline-flex items-center gap-2"><Activity className="h-4 w-4 text-violet-glow" /> Full audit trail</span>
            </div>
          </div>
          <div className="animate-rise-in" style={{ animationDelay: "0.15s" }}>
            <CyberGlobe />
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5">
          <div className="glass-card grid gap-6 p-7 sm:grid-cols-2 lg:grid-cols-4">
            {STATS.map((s) => (
              <div key={s.label}>
                <p className="font-display text-3xl font-semibold text-gradient-violet sm:text-4xl">{s.value}</p>
                <p className="mt-2 text-sm text-muted-foreground">{s.label}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="features" className="mx-auto max-w-7xl px-5 py-16">
          <h2 className="text-3xl font-semibold sm:text-4xl">Core modules</h2>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            Four connected capabilities that take a case from raw seizure to a defensible, reviewable report.
          </p>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map(({ Icon, title, desc }) => (
              <article key={title} className="glass-card glow-hover group p-6">
                <div
                  className="grid h-11 w-11 place-items-center rounded-xl border border-violet-glow/35 bg-surface/60 transition-transform duration-300 group-hover:scale-110"
                  style={{ boxShadow: "0 0 22px -8px rgba(168,85,247,0.9)" }}
                >
                  <Icon className="h-5 w-5 text-violet-glow" />
                </div>
                <h3 className="mt-5 text-lg font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{desc}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="roles" className="mx-auto max-w-7xl px-5 py-10">
          <h2 className="text-3xl font-semibold sm:text-4xl">Built for every role</h2>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            Permissions, dashboards and workflows tailored to how each team member works a case.
          </p>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {ROLES.map(({ Icon, title, points, to }) => (
              <Link key={title} to={to} className="glass-card glow-hover group p-6">
                <div
                  className="grid h-12 w-12 place-items-center rounded-xl border border-violet-glow/35 bg-surface/60 transition-transform duration-300 group-hover:scale-110"
                  style={{ boxShadow: "0 0 24px -8px rgba(168,85,247,0.9)" }}
                >
                  <Icon className="h-6 w-6 text-violet-glow" />
                </div>
                <h3 className="mt-5 text-lg font-semibold">{title}</h3>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  {points.map((p) => (
                    <li key={p} className="flex gap-2">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-glow" />
                      {p}
                    </li>
                  ))}
                </ul>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-violet-glow">
                  Open dashboard <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            ))}
          </div>
        </section>

        <section id="workflow" className="mx-auto max-w-7xl px-5 py-16">
          <h2 className="text-3xl font-semibold sm:text-4xl">How a case moves</h2>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {FLOW.map(({ step, title, desc }) => (
              <div key={step} className="glass-card glow-hover relative overflow-hidden p-6">
                <span className="font-display text-4xl font-bold text-violet-glow/25">{step}</span>
                <h3 className="mt-3 text-lg font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="about" className="mx-auto max-w-7xl px-5 py-10">
          <div className="animated-glow-border glass-card overflow-hidden p-7 sm:p-10">
            <div className="grid gap-6 md:grid-cols-[auto_minmax(0,1fr)] md:items-center">
              <div
                className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl border border-violet-glow/40 bg-surface/60"
                style={{ boxShadow: "0 0 30px -8px rgba(168,85,247,0.9)" }}
              >
                <Shield className="h-7 w-7 text-violet-glow" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-violet-glow">
                  Human oversight guaranteed
                </p>
                <h2 className="mt-2 text-2xl font-semibold sm:text-3xl">AI output is advisory only</h2>
                <p className="mt-3 max-w-3xl text-sm leading-relaxed text-muted-foreground sm:text-base">
                  Cyber Shield never makes an investigative decision. Every correlation, score and generated
                  report section is presented with its underlying evidence and requires explicit human review
                  and approval by an authorised officer before it enters a case file.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer id="contact" className="mt-12 border-t border-border/60 bg-background/50">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-9 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-violet-glow" />
            <span className="font-display text-sm font-semibold">Cyber Shield</span>
          </div>
          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
            <a href="#features" className="hover:text-foreground">Features</a>
            <a href="#roles" className="hover:text-foreground">Roles</a>
            <Link to="/dashboard" className="hover:text-foreground">Dashboards</Link>
            <Link to="/login" className="hover:text-foreground">Login</Link>
            <Link to="/register" className="hover:text-foreground">Register</Link>
          </div>
          <p className="text-xs text-muted-foreground">
            Synthetic data only — built for research and demonstration.
          </p>
        </div>
      </footer>
    </div>
  );
}
