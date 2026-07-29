import { createFileRoute, Link } from "@tanstack/react-router";
import { Shield, Network, Sparkles, FileText, GitBranch, ScanEye } from "lucide-react";
import { ParticleBackground } from "@/components/ParticleBackground";
import { ShieldGraphic } from "@/components/ShieldGraphic";

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
            <a href="#about" className="transition-colors hover:text-foreground">About</a>
            <a href="#contact" className="transition-colors hover:text-foreground">Contact</a>
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
              <a
                href="#features"
                className="rounded-xl border border-border px-6 py-3 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Explore modules
              </a>
            </div>
          </div>
          <div className="animate-rise-in" style={{ animationDelay: "0.15s" }}>
            <ShieldGraphic priority />
          </div>
        </section>

        <section id="features" className="mx-auto max-w-7xl px-5 py-16">
          <h2 className="text-3xl font-semibold sm:text-4xl">Core modules</h2>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            Four connected capabilities that take a case from raw seizure to a defensible, reviewable report.
          </p>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map(({ Icon, title, desc }) => (
              <article key={title} className="glass-card glow-hover p-6">
                <div
                  className="grid h-11 w-11 place-items-center rounded-xl border border-violet-glow/35 bg-surface/60"
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
            <a href="#about" className="hover:text-foreground">About</a>
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
