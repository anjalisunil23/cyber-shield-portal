import { useCountUp } from "@/hooks/useCountUp";

export function AnimatedCounter({
  value,
  suffix = "",
  prefix = "",
  label,
}: {
  value: number;
  suffix?: string;
  prefix?: string;
  label: string;
}) {
  const { ref, value: current } = useCountUp(value);

  return (
    <div className="text-center">
      <p className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
        <span ref={ref}>
          {prefix}
          {current.toLocaleString()}
          {suffix}
        </span>
      </p>
      <p className="mt-2 text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
