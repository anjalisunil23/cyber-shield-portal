import { CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { GradientLink } from "@/components/landing/GradientButton";
import { ParticleField } from "@/components/landing/ParticleField";
import { ShieldCore } from "@/components/cyber/ShieldCore";

const BULLETS = ["Secure", "Investigate", "Analyze"];

export function HeroSection() {
  return (
    <section id="home" className="relative overflow-hidden pt-28 sm:pt-32">
      <ParticleField />
      <div className="relative z-10 mx-auto grid max-w-7xl items-center gap-12 px-5 pb-20 lg:grid-cols-2 lg:pb-28">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <p className="mb-3 text-xs font-semibold uppercase tracking-[0.22em] text-cyan">
            CyberShield
          </p>
          <h1 className="text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl lg:text-[3.25rem]">
            Cyber Intelligence
            <br />
            <span className="text-gradient-brand">& Investigation Platform</span>
          </h1>
          <p className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            A command center for digital evidence, case investigation, and AI-assisted analysis.
          </p>
          <ul className="mt-6 flex flex-wrap gap-3">
            {BULLETS.map((b) => (
              <li
                key={b}
                className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-sm text-foreground/90"
              >
                <CheckCircle2 className="h-4 w-4 text-success" />
                {b}
              </li>
            ))}
          </ul>
          <div className="mt-10 flex flex-wrap items-center gap-4">
            <GradientLink to="/login" className="min-w-[168px]">
              Enter Dashboard
            </GradientLink>
            <GradientLink to="/register" variant="secondary" className="min-w-[168px]">
              Request access
            </GradientLink>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.15 }}
          className="hidden sm:block"
        >
          <ShieldCore />
        </motion.div>
      </div>
    </section>
  );
}
