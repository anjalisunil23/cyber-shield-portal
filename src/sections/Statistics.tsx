import { AnimatedCounter } from "@/components/landing/AnimatedCounter";

const STATS = [
  { value: 10000, suffix: "+", label: "Cases Processed" },
  { value: 2, suffix: "M+", label: "Evidence Files", prefix: "" },
  { value: 98, suffix: "%", label: "AI Accuracy" },
  { value: 24, suffix: "/7", label: "Availability" },
];

export function StatisticsSection() {
  return (
    <section className="py-16">
      <div className="mx-auto max-w-7xl px-5">
        <div className="grid gap-8 rounded-3xl border border-white/10 bg-gradient-to-br from-primary/10 via-[rgb(17_24_39/0.8)] to-cyan/10 px-6 py-12 backdrop-blur sm:grid-cols-2 lg:grid-cols-4 lg:px-10">
          {STATS.map((s) => (
            <AnimatedCounter key={s.label} {...s} />
          ))}
        </div>
      </div>
    </section>
  );
}
