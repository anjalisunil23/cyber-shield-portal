export function ParticleField() {
  const dots = Array.from({ length: 28 }, (_, i) => ({
    left: `${(i * 37) % 100}%`,
    top: `${(i * 53) % 100}%`,
    delay: `${(i % 10) * 0.45}s`,
    duration: `${6 + (i % 7)}s`,
    size: 2 + (i % 3),
  }));

  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="landing-grid absolute inset-0 opacity-70" />
      <div className="absolute -left-20 top-10 h-72 w-72 rounded-full bg-primary/20 blur-3xl" />
      <div className="absolute right-0 top-24 h-80 w-80 rounded-full bg-cyan/15 blur-3xl" />
      <div className="absolute bottom-10 left-1/3 h-64 w-64 rounded-full bg-primary/10 blur-3xl" />
      {dots.map((d, i) => (
        <span
          key={i}
          className="absolute rounded-full bg-cyan/70"
          style={{
            left: d.left,
            top: d.top,
            width: d.size,
            height: d.size,
            animation: `particle-drift ${d.duration} linear ${d.delay} infinite`,
          }}
        />
      ))}
    </div>
  );
}
