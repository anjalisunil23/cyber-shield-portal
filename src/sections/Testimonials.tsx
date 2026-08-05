import { GlassCard } from "@/components/landing/GlassCard";
import { SectionHeading } from "@/components/landing/SectionHeading";

const TESTIMONIALS = [
  {
    quote:
      "CyberShield compressed weeks of media review into days. The relationship graph alone changed how we prioritize leads.",
    name: "Priya Nair",
    role: "Senior Digital Forensics Officer",
    initials: "PN",
  },
  {
    quote:
      "Explainable AI scoring means supervisors can approve findings with confidence. Human oversight stays in the loop.",
    name: "Marcus Hale",
    role: "Investigation Supervisor",
    initials: "MH",
  },
  {
    quote:
      "Chat and email entity extraction is remarkably accurate. Our unit finally has one place for every evidence type.",
    name: "Aisha Rahman",
    role: "Cyber Crime Analyst",
    initials: "AR",
  },
];

export function TestimonialsSection() {
  return (
    <section className="py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-5">
        <SectionHeading
          eyebrow="Testimonials"
          title="Trusted by investigation professionals"
          description="Feedback from teams using CyberShield for digital evidence workflows."
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <GlassCard key={t.name} transition={{ delay: i * 0.08 }}>
              <p className="text-sm leading-relaxed text-foreground/90">&ldquo;{t.quote}&rdquo;</p>
              <div className="mt-6 flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-full bg-gradient-to-br from-primary to-cyan text-xs font-bold text-white">
                  {t.initials}
                </div>
                <div>
                  <p className="text-sm font-semibold">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role}</p>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </section>
  );
}
