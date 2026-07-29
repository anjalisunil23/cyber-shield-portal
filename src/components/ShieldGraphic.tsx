import shieldHero from "@/assets/shield-hero.png";
import { Network, FileSearch, Fingerprint, FileText, Users, Image as ImageIcon, Box } from "lucide-react";

const ORBIT = [
  { Icon: Network, top: "6%", left: "8%" },
  { Icon: FileSearch, top: "2%", left: "72%" },
  { Icon: Fingerprint, top: "34%", left: "-2%" },
  { Icon: FileText, top: "30%", left: "86%" },
  { Icon: Users, top: "64%", left: "2%" },
  { Icon: ImageIcon, top: "62%", left: "84%" },
  { Icon: Box, top: "86%", left: "44%" },
];

export function ShieldGraphic({ priority = false }: { priority?: boolean }) {
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[520px]">
      <div className="absolute left-1/2 top-1/2 h-[62%] w-[62%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-glow/25 blur-3xl" />
      <div
        className="absolute bottom-[10%] left-1/2 h-40 w-40 -translate-x-1/2 rounded-full border border-violet-glow/40"
        style={{ animation: "radar-pulse 3.4s ease-out infinite" }}
      />
      <div
        className="absolute bottom-[10%] left-1/2 h-40 w-40 -translate-x-1/2 rounded-full border border-violet-glow/30"
        style={{ animation: "radar-pulse 3.4s ease-out 1.7s infinite" }}
      />
      <img
        src={shieldHero}
        alt="Holographic digital mesh shield representing Cyber Shield's secure evidence platform"
        width={1024}
        height={1024}
        loading={priority ? "eager" : "lazy"}
        className="animate-float-slow relative z-10 h-full w-full object-contain drop-shadow-[0_0_60px_rgba(168,85,247,0.45)]"
      />
      {ORBIT.map(({ Icon, top, left }, i) => (
        <div
          key={i}
          className="animate-float-slow absolute grid h-11 w-11 place-items-center rounded-xl border border-violet-glow/35 bg-surface/60 backdrop-blur-sm"
          style={{ top, left, animationDelay: `${i * 0.5}s`, boxShadow: "0 0 22px -6px rgba(168,85,247,0.8)" }}
        >
          <Icon className="h-5 w-5 text-violet-glow" />
        </div>
      ))}
    </div>
  );
}
