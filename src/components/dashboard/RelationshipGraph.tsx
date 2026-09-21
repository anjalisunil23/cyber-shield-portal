import { Link } from "@tanstack/react-router";
import { Share2, ArrowRight } from "lucide-react";
import { DynamicRelationshipGraph } from "./DynamicRelationshipGraph";

export function RelationshipGraph({ caseId }: { caseId?: string } = {}) {
  if (caseId) {
    return <DynamicRelationshipGraph caseId={caseId} />;
  }

  const nodes = [
    { id: "s1", label: "Suspect", x: 80, y: 70, c: "#EF4444" },
    { id: "v1", label: "Victim", x: 220, y: 50, c: "#22C55E" },
    { id: "w1", label: "Witness", x: 160, y: 140, c: "#F59E0B" },
    { id: "e1", label: "Evidence", x: 60, y: 160, c: "#3B82F6" },
    { id: "d1", label: "Device", x: 250, y: 150, c: "#06B6D4" },
    { id: "l1", label: "Location", x: 150, y: 30, c: "#8B5CF6" },
  ];
  const edges: [number, number][] = [
    [0, 1],
    [0, 2],
    [0, 3],
    [1, 4],
    [2, 5],
    [3, 4],
  ];

  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Cross-Evidence Knowledge Graph</h3>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Multi-hop linkages: Suspects · Victims · Evidence · Devices · Locations
          </p>
        </div>
        <Link
          to="/dashboard/ai-analysis"
          className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-medium"
        >
          Explore in AI Hub <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
      <svg viewBox="0 0 320 200" className="mt-4 h-52 w-full">
        {edges.map(([a, b], i) => (
          <line
            key={i}
            x1={nodes[a].x}
            y1={nodes[a].y}
            x2={nodes[b].x}
            y2={nodes[b].y}
            stroke="rgba(148,163,184,0.35)"
            strokeWidth="1.5"
          />
        ))}
        {nodes.map((n) => (
          <g key={n.id}>
            <circle
              cx={n.x}
              cy={n.y}
              r="16"
              fill={n.c}
              fillOpacity="0.25"
              stroke={n.c}
              strokeWidth="2"
            />
            <text x={n.x} y={n.y + 30} textAnchor="middle" fill="#94A3B8" fontSize="9">
              {n.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
