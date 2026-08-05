export function ParticleBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 opacity-[0.18] [background-image:linear-gradient(to_right,rgba(168,85,247,0.14)_1px,transparent_1px),linear-gradient(to_bottom,rgba(168,85,247,0.14)_1px,transparent_1px)] [background-size:64px_64px]" />
    </div>
  );
}
