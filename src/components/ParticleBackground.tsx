const ORBS = [
  { top: "-12%", left: "-8%", size: 520, hue: "168,85,247", delay: "0s" },
  { top: "35%", left: "72%", size: 460, hue: "123,47,247", delay: "-6s" },
  { top: "78%", left: "12%", size: 400, hue: "99,102,241", delay: "-12s" },
];

const NODES = Array.from({ length: 22 }, (_, i) => ({
  left: (i * 17 + ((i * 29) % 13)) % 100,
  top: (i * 31 + ((i * 7) % 19)) % 100,
  size: 2 + ((i * 5) % 3),
  delay: -((i * 3) % 9),
  dur: 7 + ((i * 5) % 8),
}));

export function ParticleBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 opacity-[0.14] [background-image:linear-gradient(to_right,rgba(168,85,247,0.16)_1px,transparent_1px),linear-gradient(to_bottom,rgba(168,85,247,0.16)_1px,transparent_1px)] [background-size:72px_72px] [mask-image:radial-gradient(circle_at_50%_35%,#000_20%,transparent_78%)]" />

      {ORBS.map((o, i) => (
        <div
          key={i}
          className="absolute rounded-full blur-[90px]"
          style={{
            top: o.top,
            left: o.left,
            width: o.size,
            height: o.size,
            background: `radial-gradient(circle, rgba(${o.hue},0.28), transparent 68%)`,
            animation: `aurora-drift 22s ease-in-out ${o.delay} infinite`,
          }}
        />
      ))}

      {NODES.map((n, i) => (
        <span
          key={i}
          className="absolute rounded-full bg-violet-glow"
          style={{
            left: `${n.left}%`,
            top: `${n.top}%`,
            width: n.size,
            height: n.size,
            boxShadow: "0 0 10px rgba(168,85,247,0.9)",
            animation: `node-twinkle ${n.dur}s ease-in-out ${n.delay}s infinite`,
          }}
        />
      ))}
    </div>
  );
}
