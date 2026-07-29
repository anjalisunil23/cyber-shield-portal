const STREAMS = Array.from({ length: 28 }, (_, i) => ({
  left: (i * 3.6 + ((i * 37) % 11)) % 100,
  duration: 9 + ((i * 7) % 12),
  delay: -((i * 13) % 20),
  height: 90 + ((i * 29) % 200),
  opacity: 0.06 + ((i * 17) % 10) / 100,
}));

export function ParticleBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 opacity-[0.18] [background-image:linear-gradient(to_right,rgba(168,85,247,0.14)_1px,transparent_1px),linear-gradient(to_bottom,rgba(168,85,247,0.14)_1px,transparent_1px)] [background-size:64px_64px]" />
      {STREAMS.map((s, i) => (
        <span
          key={i}
          className="absolute top-0 w-px"
          style={{
            left: `${s.left}%`,
            height: `${s.height}px`,
            opacity: s.opacity,
            background: "linear-gradient(to bottom, transparent, #a855f7, transparent)",
            animation: `data-fall ${s.duration}s linear ${s.delay}s infinite`,
          }}
        />
      ))}
    </div>
  );
}
