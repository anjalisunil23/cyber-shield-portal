import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Share2,
  Filter,
  Info,
  Maximize2,
  FileText,
  User,
  Phone,
  Mail,
  MapPin,
  Smartphone,
  Building2,
  Sparkles,
} from "lucide-react";
import { investigationApi } from "@/services/investigationApi";
import type { CaseGraphData, GraphNode, GraphEdge } from "@/services/types";

export function DynamicRelationshipGraph({ caseId }: { caseId: string }) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterKind, setFilterKind] = useState<string>("all");

  const graphQ = useQuery({
    queryKey: ["case-graph", caseId],
    queryFn: () => investigationApi.getCaseGraph(caseId),
    enabled: !!caseId,
  });

  const rawData: CaseGraphData = graphQ.data || {
    case_id: caseId,
    nodes: [],
    edges: [],
  };

  // Filter nodes & edges
  const filteredNodes = useMemo(() => {
    if (filterKind === "all") return rawData.nodes;
    return rawData.nodes.filter((n) => n.kind === filterKind || n.kind === "evidence");
  }, [rawData.nodes, filterKind]);

  const activeNodeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  const filteredEdges = useMemo(() => {
    return rawData.edges.filter((e) => activeNodeIds.has(e.source) && activeNodeIds.has(e.target));
  }, [rawData.edges, activeNodeIds]);

  // Layout positions: calculate pleasant radial / force-directed positions in 720x420 viewBox
  const positionedNodes = useMemo(() => {
    const width = 720;
    const height = 400;
    const cx = width / 2;
    const cy = height / 2;
    const total = filteredNodes.length;

    if (total === 0) return [];

    // Separate into central entities and surrounding evidence
    const evidenceNodes = filteredNodes.filter((n) => n.kind === "evidence");
    const entityNodes = filteredNodes.filter((n) => n.kind !== "evidence");

    const result: (GraphNode & { x: number; y: number })[] = [];

    // Inner circle for key entities
    const innerRadius = Math.min(130, 40 + entityNodes.length * 15);
    entityNodes.forEach((n, i) => {
      const angle = (i / Math.max(1, entityNodes.length)) * 2 * Math.PI - Math.PI / 2;
      result.push({
        ...n,
        x: Math.round(cx + innerRadius * Math.cos(angle)),
        y: Math.round(cy + innerRadius * Math.sin(angle)),
      });
    });

    // Outer circle for evidence files
    const outerRadius = Math.min(185, innerRadius + 60);
    evidenceNodes.forEach((n, i) => {
      const angle = (i / Math.max(1, evidenceNodes.length)) * 2 * Math.PI - Math.PI / 4;
      result.push({
        ...n,
        x: Math.round(cx + outerRadius * Math.cos(angle)),
        y: Math.round(cy + outerRadius * Math.sin(angle)),
      });
    });

    return result;
  }, [filteredNodes]);

  const nodePosMap = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    for (const n of positionedNodes) {
      map.set(n.id, { x: n.x, y: n.y });
    }
    return map;
  }, [positionedNodes]);

  const kinds = [
    { id: "all", label: "All Nodes" },
    { id: "person", label: "Persons" },
    { id: "phone", label: "Phone Numbers" },
    { id: "email", label: "Emails" },
    { id: "location", label: "Locations" },
    { id: "device", label: "Devices" },
  ];

  if (graphQ.isLoading) {
    return (
      <div className="rounded-2xl border border-border bg-card p-12 text-center text-xs text-muted-foreground animate-pulse">
        Generating multi-source relationship graph...
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
            <Share2 className="h-4 w-4 text-primary" /> Interactive Evidence Relationship Graph
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Real-time entity correlations, links, and cross-source associations extracted from
            digital evidence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-3.5 w-3.5 text-muted-foreground" />
          <select
            value={filterKind}
            onChange={(e) => setFilterKind(e.target.value)}
            className="rounded-lg border border-border bg-background px-2.5 py-1 text-xs text-foreground"
          >
            {kinds.map((k) => (
              <option key={k.id} value={k.id}>
                {k.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative rounded-xl border border-border bg-background/90 overflow-hidden flex items-center justify-center min-h-[380px]">
        {positionedNodes.length === 0 ? (
          <p className="text-xs text-muted-foreground p-8 text-center">
            No active relationships or evidence nodes found for this case.
          </p>
        ) : (
          <svg viewBox="0 0 720 400" className="w-full h-[380px] select-none">
            {/* Edges */}
            {filteredEdges.map((e) => {
              const p1 = nodePosMap.get(e.source);
              const p2 = nodePosMap.get(e.target);
              if (!p1 || !p2) return null;

              const isHighlighted =
                selectedNode && (selectedNode.id === e.source || selectedNode.id === e.target);

              return (
                <g key={e.id}>
                  <line
                    x1={p1.x}
                    y1={p1.y}
                    x2={p2.x}
                    y2={p2.y}
                    stroke={isHighlighted ? "#06B6D4" : "rgba(148, 163, 184, 0.35)"}
                    strokeWidth={isHighlighted ? 2.5 : 1.2}
                    strokeDasharray={e.ai_generated ? "4,3" : undefined}
                  />
                  {/* Midpoint relationship badge */}
                  <circle
                    cx={(p1.x + p2.x) / 2}
                    cy={(p1.y + p2.y) / 2}
                    r={3}
                    fill={isHighlighted ? "#06B6D4" : "rgba(148, 163, 184, 0.6)"}
                  />
                </g>
              );
            })}

            {/* Nodes */}
            {positionedNodes.map((n) => {
              const isSelected = selectedNode?.id === n.id;
              const isEvidence = n.kind === "evidence";

              return (
                <g
                  key={n.id}
                  onClick={() => setSelectedNode(isSelected ? null : n)}
                  className="cursor-pointer transition-transform duration-150 hover:scale-110"
                >
                  {/* Glow circle on selected */}
                  {isSelected && (
                    <circle
                      cx={n.x}
                      cy={n.y}
                      r={n.size + 6}
                      fill="none"
                      stroke={n.color}
                      strokeWidth={2}
                      strokeDasharray="3,3"
                      className="animate-spin"
                    />
                  )}

                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={n.size}
                    fill={n.color}
                    fillOpacity={isEvidence ? 0.2 : 0.25}
                    stroke={n.color}
                    strokeWidth={isSelected ? 3 : 1.8}
                  />

                  {/* Icon or letter symbol */}
                  <text
                    x={n.x}
                    y={n.y + 4}
                    textAnchor="middle"
                    fill={n.color}
                    fontSize="10"
                    fontWeight="bold"
                    pointerEvents="none"
                  >
                    {isEvidence ? "EV" : n.kind.charAt(0).toUpperCase()}
                  </text>

                  {/* Label under node */}
                  <text
                    x={n.x}
                    y={n.y + n.size + 12}
                    textAnchor="middle"
                    fill="#E2E8F0"
                    fontSize="9"
                    fontWeight="500"
                    className="truncate"
                  >
                    {n.label.length > 18 ? `${n.label.slice(0, 16)}…` : n.label}
                  </text>
                </g>
              );
            })}
          </svg>
        )}

        {/* Selected Node Inspector Floating Card */}
        {selectedNode && (
          <div className="absolute bottom-3 right-3 w-72 rounded-xl border border-border bg-card/95 p-3.5 shadow-2xl backdrop-blur-md space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="rounded bg-primary/10 border border-primary/20 px-2 py-0.5 text-[10px] font-bold text-primary uppercase">
                {selectedNode.kind}
              </span>
              <button
                type="button"
                onClick={() => setSelectedNode(null)}
                className="text-muted-foreground hover:text-foreground text-xs"
              >
                ✕
              </button>
            </div>
            <p className="font-bold text-sm text-foreground truncate" title={selectedNode.label}>
              {selectedNode.label}
            </p>
            <p className="text-[11px] text-muted-foreground">
              Connected across case evidence. Click surrounding linked nodes to inspect correlation
              pathway.
            </p>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border text-[11px] text-muted-foreground">
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-[#34D399]" /> Person
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-[#22D3EE]" /> Phone
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-[#A78BFA]" /> Email
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-[#F472B6]" /> Location
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-[#38BDF8]" /> Evidence
          </span>
        </div>
        <span className="flex items-center gap-1 italic">
          <Sparkles className="h-3 w-3 text-cyan" /> Dashed lines indicate AI-correlated links
        </span>
      </div>
    </div>
  );
}
