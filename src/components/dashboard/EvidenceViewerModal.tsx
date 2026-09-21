import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  X,
  FileText,
  Image as ImageIcon,
  Music,
  MapPin,
  Camera,
  Fingerprint,
  RefreshCw,
  ExternalLink,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Download,
  Copy,
  Clock,
  Sparkles,
  Search,
} from "lucide-react";
import { toast } from "sonner";
import { investigationApi } from "@/services/investigationApi";
import { apiMessage } from "@/services/apiClient";
import type { EvidenceItem, EvidenceAnalysis } from "@/services/types";

export function EvidenceViewerModal({
  evidence,
  onClose,
}: {
  evidence: EvidenceItem;
  onClose: () => void;
}) {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<
    "overview" | "metadata" | "ocr" | "audio" | "entities"
  >("overview");

  // Fetch full live forensic intelligence analysis from backend
  const analysisQ = useQuery({
    queryKey: ["evidence-analysis", evidence.id],
    queryFn: () => investigationApi.getEvidenceAnalysis(evidence.id),
    retry: false,
  });

  const reprocess = useMutation({
    mutationFn: () => investigationApi.processEvidence(evidence.id),
    onSuccess: () => {
      toast.success("AI pipeline re-processed evidence successfully");
      void qc.invalidateQueries({ queryKey: ["evidence-analysis", evidence.id] });
      void qc.invalidateQueries({ queryKey: ["evidence"] });
    },
    onError: (e) => toast.error(apiMessage(e, "Failed to reprocess evidence")),
  });

  const analysis = analysisQ.data;
  const hash = evidence.file_hash || evidence.sha256_hash;
  const metadata = analysis?.metadata || evidence.metadata_json || {};
  const exif = (metadata.exif as Record<string, unknown>) || {};
  const gpsCoord =
    (metadata.gps_coordinates as string) || (exif.GPSInfo ? "Available in EXIF" : "Not Available");
  const ocrText = analysis?.ocr_text || evidence.ocr_text || "";
  const transcript = analysis?.speech_transcript || evidence.speech_transcript || "";
  const entities = analysis?.extracted_entities || [];

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`);
  };

  const isImage = evidence.file_type === "image";
  const isAudio = evidence.file_type === "audio";
  const isVideo = evidence.file_type === "video";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative flex flex-col h-[90vh] w-full max-w-5xl rounded-2xl border border-border bg-card shadow-2xl overflow-hidden text-foreground">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-6 py-4 bg-background/60">
          <div className="flex items-center gap-3 min-w-0">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary/15 text-primary">
              {isImage ? (
                <ImageIcon className="h-5 w-5" />
              ) : isAudio ? (
                <Music className="h-5 w-5" />
              ) : (
                <FileText className="h-5 w-5" />
              )}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold truncate">{evidence.original_name}</h2>
                <span className="rounded-md bg-muted px-2 py-0.5 text-[10px] font-mono uppercase text-primary">
                  {evidence.file_type}
                </span>
                {evidence.is_duplicate && (
                  <span className="rounded-md bg-amber-500/15 border border-amber-500/30 px-2 py-0.5 text-[10px] font-semibold text-amber-500 flex items-center gap-1">
                    <AlertTriangle className="h-3 w-3" /> Duplicate
                  </span>
                )}
              </div>
              <p className="text-xs text-muted-foreground truncate font-mono">SHA-256: {hash}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              disabled={reprocess.isPending}
              onClick={() => reprocess.mutate()}
              className="inline-flex items-center gap-1.5 rounded-xl border border-border bg-background px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted transition-colors disabled:opacity-50"
              title="Re-run OCR, speech transcription, and entity extraction"
            >
              <RefreshCw
                className={`h-3.5 w-3.5 text-primary ${reprocess.isPending ? "animate-spin" : ""}`}
              />
              {reprocess.isPending ? "Processing..." : "Re-run AI"}
            </button>
            <a
              href={investigationApi.downloadEvidenceUrl(evidence.id)}
              download={evidence.original_name}
              className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <Download className="h-3.5 w-3.5" /> Download
            </a>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors ml-2"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Duplicate Warning Banner */}
        {evidence.is_duplicate && (
          <div className="bg-amber-500/10 border-b border-amber-500/20 px-6 py-2.5 flex items-center gap-2 text-xs text-amber-600 dark:text-amber-300">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>
              {analysis?.duplicate_warning ||
                "Identical SHA-256 hash detected in this case repository. Chain-of-custody reference preserved."}
            </span>
          </div>
        )}

        {/* Pipeline Stepper — reflects actual backend pipeline_steps */}
        <div className="border-b border-border bg-background/40 px-6 py-3">
          <PipelineStepper
            steps={analysis?.pipeline_steps || {}}
            processingStatus={
              analysis?.processing_status || evidence.processing_status || "UPLOADED"
            }
            entityCount={entities.length}
            loading={analysisQ.isLoading || reprocess.isPending}
          />
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-border px-6 bg-card">
          <button
            type="button"
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === "overview"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            File Preview & Digest
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("metadata")}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === "metadata"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Forensic Metadata & EXIF
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("ocr")}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === "ocr"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Extracted Text / OCR ({ocrText ? "Available" : "None"})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("audio")}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === "audio"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Speech Transcript ({transcript ? "Available" : "None"})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("entities")}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === "entities"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Extracted Entities ({entities.length})
          </button>
        </div>

        {/* Tab Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {activeTab === "overview" && (
            <div className="grid gap-6 lg:grid-cols-12">
              {/* Media Preview Window */}
              <div className="lg:col-span-7 flex flex-col items-center justify-center rounded-2xl border border-border bg-background p-4 min-h-[320px]">
                {isImage ? (
                  <div className="space-y-3 text-center w-full">
                    <img
                      src={investigationApi.downloadEvidenceUrl(evidence.id)}
                      alt={evidence.original_name}
                      className="max-h-[360px] mx-auto rounded-xl object-contain border border-border/50 shadow-md"
                      onError={(e) => {
                        (e.target as HTMLElement).style.display = "none";
                      }}
                    />
                    <p className="text-xs text-muted-foreground font-mono">
                      Image frame preview rendered directly from encrypted vault storage.
                    </p>
                  </div>
                ) : isAudio ? (
                  <div className="space-y-4 text-center w-full p-6">
                    <div className="grid h-16 w-16 mx-auto place-items-center rounded-2xl bg-primary/10 text-primary">
                      <Music className="h-8 w-8" />
                    </div>
                    <audio
                      controls
                      src={investigationApi.downloadEvidenceUrl(evidence.id)}
                      className="w-full max-w-md mx-auto mt-2"
                    />
                    <p className="text-xs text-muted-foreground">
                      Audio playback stream from secure forensic repository.
                    </p>
                  </div>
                ) : (
                  <div className="w-full h-full flex flex-col justify-between">
                    <div className="rounded-xl bg-card p-4 border border-border font-mono text-xs text-foreground overflow-y-auto max-h-[360px] whitespace-pre-wrap">
                      {ocrText ||
                        evidence.description ||
                        "Raw evidence file loaded. Select Extracted Text or Entities tab to view parsed intelligence."}
                    </div>
                  </div>
                )}
              </div>

              {/* Technical Digest Cards */}
              <div className="lg:col-span-5 space-y-4">
                <div className="rounded-xl border border-border bg-background/80 p-4 space-y-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Forensic File Digest
                  </h3>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between py-1 border-b border-border/60">
                      <span className="text-muted-foreground">Original Name:</span>
                      <span
                        className="font-semibold text-foreground truncate max-w-[200px]"
                        title={evidence.original_name}
                      >
                        {evidence.original_name}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-border/60">
                      <span className="text-muted-foreground">File Size:</span>
                      <span className="font-mono text-foreground">
                        {(evidence.file_size / 1024).toFixed(1)} KB (
                        {evidence.file_size.toLocaleString()} bytes)
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-border/60">
                      <span className="text-muted-foreground">MIME Type:</span>
                      <span className="font-mono text-foreground">
                        {evidence.mime_type || "application/octet-stream"}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-border/60">
                      <span className="text-muted-foreground">Upload Timestamp:</span>
                      <span className="text-foreground">
                        {new Date(evidence.upload_date).toLocaleString()}
                      </span>
                    </div>
                    <div className="py-1">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">SHA-256 Digest:</span>
                        <button
                          type="button"
                          onClick={() => copyToClipboard(hash, "SHA-256")}
                          className="text-[10px] text-primary hover:underline flex items-center gap-1"
                        >
                          <Copy className="h-3 w-3" /> Copy
                        </button>
                      </div>
                      <p className="mt-1 font-mono text-[10px] text-foreground bg-card p-2 rounded-lg border border-border select-all break-all">
                        {hash}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Quick Intelligence Summary */}
                <div className="rounded-xl border border-border bg-background/80 p-4 space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Extracted Intelligence Summary
                  </h3>
                  <div className="grid grid-cols-2 gap-2 text-center">
                    <div className="rounded-lg bg-card p-2 border border-border">
                      <p className="text-[10px] text-muted-foreground">Entities Identified</p>
                      <p className="text-base font-bold text-primary">{entities.length}</p>
                    </div>
                    <div className="rounded-lg bg-card p-2 border border-border">
                      <p className="text-[10px] text-muted-foreground">Text Characters</p>
                      <p className="text-base font-bold text-foreground">
                        {(ocrText || transcript).length}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "metadata" && (
            <div className="space-y-4">
              <div className="rounded-xl border border-border bg-background p-4 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <Camera className="h-4 w-4 text-primary" /> Camera & Device Information
                </h3>
                <div className="grid gap-3 sm:grid-cols-2 text-xs">
                  <div className="p-3 rounded-lg bg-card border border-border">
                    <p className="text-muted-foreground text-[11px]">Device / Camera Model</p>
                    <p className="font-semibold text-foreground mt-0.5">
                      {typeof exif.Make === "string" || typeof exif.Model === "string"
                        ? `${typeof exif.Make === "string" ? exif.Make : ""} ${typeof exif.Model === "string" ? exif.Model : ""}`.trim()
                        : (metadata.camera_model as string) || "Not Available"}
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-card border border-border">
                    <p className="text-muted-foreground text-[11px]">Original Embedded Time</p>
                    <p className="font-mono text-foreground mt-0.5">
                      {(typeof exif.DateTimeOriginal === "string" ? exif.DateTimeOriginal : "") ||
                        (metadata.creation_date as string) ||
                        "Not Available"}
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-card border border-border">
                    <p className="text-muted-foreground text-[11px]">Dimensions / Resolution</p>
                    <p className="font-mono text-foreground mt-0.5">
                      {exif.width && exif.height
                        ? `${exif.width} x ${exif.height} px`
                        : "Not Available"}
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-card border border-border">
                    <p className="text-muted-foreground text-[11px]">Document Author / Creator</p>
                    <p className="font-semibold text-foreground mt-0.5">
                      {(metadata.author as string) || "Not Available"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Geolocation */}
              <div className="rounded-xl border border-border bg-background p-4 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-emerald-500" /> Geolocation & Physical Location
                </h3>
                <div className="p-3 rounded-lg bg-card border border-border flex items-center justify-between">
                  <div>
                    <p className="text-[11px] text-muted-foreground">GPS Coordinates</p>
                    <p className="font-mono text-sm font-bold text-foreground mt-0.5">{gpsCoord}</p>
                  </div>
                  {gpsCoord !== "Not Available" && (
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(gpsCoord)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/25"
                    >
                      View on Map <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === "ocr" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Engine:</span>
                  <span className="rounded bg-primary/10 border border-primary/20 px-2 py-0.5 text-xs font-mono text-primary uppercase">
                    {analysis?.ocr_engine || "Standard OCR"}
                  </span>
                  {analysis?.ocr_confidence ? (
                    <span className="rounded bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 text-xs font-semibold text-emerald-500">
                      Confidence: {Math.round(analysis.ocr_confidence * 100)}%
                    </span>
                  ) : null}
                </div>
                {ocrText && (
                  <button
                    type="button"
                    onClick={() => copyToClipboard(ocrText, "OCR Text")}
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                  >
                    <Copy className="h-3.5 w-3.5" /> Copy Text
                  </button>
                )}
              </div>

              <div className="rounded-xl border border-border bg-background p-4 min-h-[250px]">
                {ocrText ? (
                  <pre className="font-mono text-xs text-foreground whitespace-pre-wrap leading-relaxed">
                    {ocrText}
                  </pre>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-xs">
                      No machine-readable text detected in this evidence item.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "audio" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Transcription Engine:</span>
                  <span className="rounded bg-cyan/10 border border-cyan/20 px-2 py-0.5 text-xs font-mono text-cyan uppercase">
                    {analysis?.stt_engine || "Whisper STT"}
                  </span>
                </div>
                {transcript && (
                  <button
                    type="button"
                    onClick={() => copyToClipboard(transcript, "Transcript")}
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                  >
                    <Copy className="h-3.5 w-3.5" /> Copy Transcript
                  </button>
                )}
              </div>

              <div className="rounded-xl border border-border bg-background p-4 min-h-[250px]">
                {transcript ? (
                  <pre className="font-mono text-xs text-foreground whitespace-pre-wrap leading-relaxed">
                    {transcript}
                  </pre>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <Music className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-xs">No audio speech transcript recorded for this item.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "entities" && (
            <div className="space-y-4">
              <p className="text-xs text-muted-foreground">
                Domain entities extracted with contextual surrounding snippets and normalized values
                for cross-evidence matching.
              </p>

              {entities.length === 0 ? (
                <div className="rounded-xl border border-border bg-background p-12 text-center text-muted-foreground">
                  <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-xs">No structured entities found in evidence content.</p>
                </div>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2">
                  {entities.map((ent, idx) => {
                    const badgeColor =
                      ent.type === "PERSON"
                        ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                        : ent.type === "PHONE"
                          ? "bg-cyan/10 text-cyan border-cyan/30"
                          : ent.type === "EMAIL"
                            ? "bg-violet-500/10 text-violet-400 border-violet-500/30"
                            : ent.type === "LOCATION"
                              ? "bg-pink-500/10 text-pink-400 border-pink-500/30"
                              : ent.type === "DEVICE"
                                ? "bg-blue-500/10 text-blue-400 border-blue-500/30"
                                : "bg-muted text-foreground border-border";

                    return (
                      <div
                        key={idx}
                        className="rounded-xl border border-border bg-background p-3.5 space-y-2"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span
                            className={`rounded-md px-2 py-0.5 text-[10px] font-bold border uppercase ${badgeColor}`}
                          >
                            {ent.type}
                          </span>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            Conf: {Math.round(ent.confidence * 100)}%
                          </span>
                        </div>

                        <div>
                          <p className="text-xs font-semibold text-foreground">
                            {ent.normalized_value}
                          </p>
                          {ent.raw_value !== ent.normalized_value && (
                            <p className="text-[10px] text-muted-foreground font-mono">
                              Raw: {ent.raw_value}
                            </p>
                          )}
                        </div>

                        {ent.context && (
                          <div className="rounded-lg bg-card p-2 border border-border/60">
                            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">
                              Forensic Context
                            </p>
                            <p className="text-[11px] text-foreground mt-0.5 italic">
                              "{ent.context}"
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Disclaimer */}
        <div className="border-t border-border px-6 py-3 bg-background/80 flex items-center justify-between text-[11px] text-muted-foreground">
          <p className="flex items-center gap-1.5">
            <ShieldAlert className="h-3.5 w-3.5 text-primary" />
            <span>
              Cyber Shield Decision-Support: AI-extracted findings are assistive and require
              independent investigator verification.
            </span>
          </p>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-border px-3 py-1 font-medium text-foreground hover:bg-muted"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
}

function stepState(
  raw: unknown,
  loading: boolean,
): "done" | "partial" | "failed" | "pending" | "processing" {
  if (loading) return "processing";
  const value = String(raw ?? "PENDING").toUpperCase();
  if (value.includes("FAILED")) return "failed";
  if (value.includes("PARTIAL")) return "partial";
  if (value.includes("COMPLETED") || value === "DONE") return "done";
  if (value.includes("PROCESSING")) return "processing";
  return "pending";
}

function PipelineStepper({
  steps,
  processingStatus,
  entityCount,
  loading,
}: {
  steps: Record<string, unknown>;
  processingStatus: string;
  entityCount: number;
  loading: boolean;
}) {
  const items = [
    { key: "hash_verification", label: "Hash Verified" },
    { key: "metadata_extraction", label: "Metadata Extracted" },
    { key: "content_extraction", label: "Content / OCR / STT" },
    { key: "entity_extraction", label: `Entities Normalized (${entityCount})` },
  ];

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px]">
        {items.map((item, idx) => {
          const state = stepState(steps[item.key], loading);
          const color =
            state === "done"
              ? "text-emerald-500"
              : state === "partial"
                ? "text-amber-500"
                : state === "failed"
                  ? "text-red-500"
                  : state === "processing"
                    ? "text-primary"
                    : "text-muted-foreground";
          return (
            <div key={item.key} className="flex items-center gap-2">
              <div className={`flex items-center gap-1.5 font-medium ${color}`}>
                {state === "done" ? (
                  <CheckCircle2 className="h-3.5 w-3.5" />
                ) : state === "failed" ? (
                  <AlertTriangle className="h-3.5 w-3.5" />
                ) : state === "processing" ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Clock className="h-3.5 w-3.5" />
                )}
                <span>{item.label}</span>
              </div>
              {idx < items.length - 1 && <span className="text-muted-foreground">➔</span>}
            </div>
          );
        })}
        <div className="flex items-center gap-1.5 text-cyan font-medium">
          <Sparkles className="h-3.5 w-3.5" />
          <span>{processingStatus.replace(/_/g, " ")}</span>
        </div>
      </div>
    </div>
  );
}
