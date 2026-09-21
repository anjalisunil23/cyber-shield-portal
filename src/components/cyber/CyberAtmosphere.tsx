import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion";

/** Subtle command-center grid + node field. CSS-only; disabled when reduced motion. */
export function CyberAtmosphere({ dense = false }: { dense?: boolean }) {
  const reduced = usePrefersReducedMotion();

  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="cyber-grid absolute inset-0 opacity-40 dark:opacity-70" />
      <div className="absolute -left-24 top-0 h-72 w-72 rounded-full bg-primary/10 blur-3xl dark:bg-primary/20" />
      <div className="absolute right-0 top-24 h-80 w-80 rounded-full bg-cyan/10 blur-3xl dark:bg-cyan/15" />
      {!reduced && !dense ? (
        <svg
          className="absolute inset-0 hidden h-full w-full opacity-30 md:block"
          viewBox="0 0 1200 800"
        >
          <g stroke="rgb(59 130 246 / 0.28)" strokeWidth="0.8" fill="none">
            <line x1="80" y1="120" x2="280" y2="90" />
            <line x1="280" y1="90" x2="520" y2="160" />
            <line x1="520" y1="160" x2="760" y2="80" />
            <line x1="760" y1="80" x2="1040" y2="140" />
            <line x1="280" y1="90" x2="340" y2="320" />
            <line x1="520" y1="160" x2="610" y2="380" />
            <line x1="760" y1="80" x2="900" y2="340" />
          </g>
          {[
            [80, 120],
            [280, 90],
            [520, 160],
            [760, 80],
            [1040, 140],
            [340, 320],
            [610, 380],
            [900, 340],
          ].map(([cx, cy], i) => (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={i % 3 === 0 ? 3.2 : 2.2}
              className="cyber-node"
              fill={i % 2 === 0 ? "#3b82f6" : "#06b6d4"}
              style={{ animationDelay: `${i * 0.4}s` }}
            />
          ))}
        </svg>
      ) : null}
    </div>
  );
}
