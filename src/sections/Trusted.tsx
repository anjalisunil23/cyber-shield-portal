import { Building2, Landmark, Scale, Shield } from "lucide-react";
import { motion } from "framer-motion";

const ORGS = [
  { label: "Law Enforcement", Icon: Shield },
  { label: "Cyber Crime Units", Icon: Scale },
  { label: "Digital Forensics Labs", Icon: Building2 },
  { label: "Government Agencies", Icon: Landmark },
];

export function TrustedSection() {
  return (
    <section className="border-y border-white/5 bg-white/[0.02] py-12">
      <div className="mx-auto max-w-7xl px-5">
        <p className="mb-8 text-center text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">
          Trusted by investigation teams
        </p>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {ORGS.map(({ label, Icon }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="flex items-center justify-center gap-3 rounded-xl border border-white/10 bg-[rgb(17_24_39/0.5)] px-4 py-5 text-sm text-muted-foreground backdrop-blur"
            >
              <Icon className="h-5 w-5 text-primary" />
              {label}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
