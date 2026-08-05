import { motion } from "framer-motion";
import { DashboardMockup } from "@/components/landing/DashboardMockup";
import { SectionHeading } from "@/components/landing/SectionHeading";

export function DashboardPreviewSection() {
  return (
    <section id="dashboard" className="py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-5">
        <SectionHeading
          eyebrow="Product preview"
          title="Investigation console built for speed"
          description="A realistic workspace with analytics, evidence tables, timelines, graphs, and an AI assistant panel."
        />
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.7 }}
          className="mt-12"
        >
          <DashboardMockup />
        </motion.div>
      </div>
    </section>
  );
}
