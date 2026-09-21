/** Shared API domain types for CyberShield Phase 1. */

export type CasePriority = "low" | "medium" | "high" | "critical";
export type CaseStatus =
  | "open"
  | "in_progress"
  | "under_review"
  | "changes_requested"
  | "approved"
  | "closed"
  | "evidence_collection"
  | "analysis"
  | "completed"
  | "archived";

export type EntityKind =
  "evidence" | "person" | "phone" | "email" | "location" | "device" | "organization" | "other";

export type RelationshipType =
  | "evidence_to_evidence"
  | "evidence_to_person"
  | "evidence_to_device"
  | "evidence_to_location"
  | "person_to_person"
  | "person_to_device"
  | "other";

export type LeadStatus = "open" | "in_progress" | "approved" | "rejected" | "closed" | "dismissed";

export type LeadPriority = "low" | "medium" | "high" | "critical";

export type UserBrief = {
  id: string;
  full_name: string;
  name?: string;
  email: string;
  role: string;
};

export type CaseAssignment = {
  id: string;
  user_id: string;
  is_primary: boolean;
  assigned_at: string;
  user?: UserBrief | null;
};

export type CaseInvestigatorRole = "INVESTIGATOR_LEAD" | "INVESTIGATOR";

export type CaseInvestigator = {
  id: string;
  case_id: string;
  user_id: string;
  role: CaseInvestigatorRole | string;
  status: "active" | "removed" | string;
  assigned_by_id?: string | null;
  assigned_at: string;
  name?: string;
  email?: string;
  user?: UserBrief | null;
};

export type CaseTeamResponse = {
  case_id: string;
  case_number: string;
  investigator_lead?: CaseInvestigator | null;
  team_investigators: CaseInvestigator[];
  total_members: number;
};

export type ChatParticipant = {
  id: string;
  conversation_id: string;
  user_id: string;
  role_in_case?: string;
  is_active?: boolean;
  joined_at: string;
  left_at?: string | null;
  last_read_at?: string;
  name?: string;
  full_name?: string;
  email?: string;
  user?: UserBrief | null;
};

export type ChatMessage = {
  id: string;
  conversation_id: string;
  sender_id?: string | null;
  content: string;
  is_system: boolean;
  created_at: string;
  sender?: UserBrief | null;
};

export type ChatConversation = {
  id: string;
  case_id?: string | null;
  type: "case_group" | "direct" | string;
  title: string;
  created_by_id?: string | null;
  created_at: string;
  updated_at: string;
  case_number?: string | null;
  participants: ChatParticipant[];
  last_message?: ChatMessage | null;
  messages?: ChatMessage[];
  unread_count: number;
};

export type InvestigationCase = {
  id: string;
  case_number: string;
  title: string;
  description: string | null;
  priority: CasePriority;
  status: CaseStatus;
  notes: string | null;
  department_id?: string | null;
  supervisor_id?: string | null;
  investigator_lead_id?: string | null;
  review_comment?: string | null;
  submitted_at?: string | null;
  reviewed_at?: string | null;
  created_by_id: string;
  created_at: string;
  updated_at: string;
  created_by?: UserBrief | null;
  supervisor?: UserBrief | null;
  investigator_lead?: UserBrief | null;
  assignments: CaseAssignment[];
  investigator_assignments?: CaseInvestigator[];
};

export type ExifMetadata = {
  Make?: string | null;
  Model?: string | null;
  DateTimeOriginal?: string | null;
  width?: number | string | null;
  height?: number | string | null;
  GPSInfo?: string | Record<string, unknown> | null;
  [key: string]: string | number | boolean | Record<string, unknown> | unknown[] | null | undefined;
};

export type EvidenceMetadata = {
  exif?: ExifMetadata | null;
  Make?: string | null;
  Model?: string | null;
  DateTimeOriginal?: string | null;
  width?: number | string | null;
  height?: number | string | null;
  GPSInfo?: string | Record<string, unknown> | null;
  [key: string]: string | number | boolean | Record<string, unknown> | unknown[] | null | undefined;
};

export type EvidenceItem = {
  id: string;
  case_id: string;
  filename: string;
  original_name: string;
  file_type: string;
  mime_type: string | null;
  file_size: number;
  sha256_hash: string;
  file_hash?: string;
  warning?: string | null;
  description: string | null;
  tags: string[] | null;
  metadata_json?: EvidenceMetadata | null;
  upload_date: string;
  is_duplicate: boolean;
  duplicate_of_id?: string | null;
  uploaded_by?: UserBrief | null;
  ocr_text?: string | null;
  speech_transcript?: string | null;
  risk_score?: number | null;
  ai_summary?: string | null;
  ai_metadata?: Record<string, unknown> | null;
  processing_status?: string | null;
};

export type NoteItem = {
  id: string;
  case_id: string;
  author_id: string;
  title: string | null;
  body: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  author?: UserBrief | null;
};

export type TimelineItem = {
  id: string;
  case_id: string;
  event_type: string;
  title: string;
  description: string | null;
  event_at: string;
  related_evidence_id?: string | null;
  created_by?: UserBrief | null;
};

export type RelationshipItem = {
  id: string;
  case_id: string;
  relationship_type: RelationshipType;
  source_kind: EntityKind;
  source_id: string;
  source_label: string;
  target_kind: EntityKind;
  target_id: string;
  target_label: string;
  description: string | null;
  ai_generated: boolean;
};

export type LeadItem = {
  id: string;
  case_id: string;
  title: string;
  description: string | null;
  priority: LeadPriority;
  status: LeadStatus;
  justification?: string | null;
  review_comment?: string | null;
  related_evidence_id?: string | null;
  related_evidence_ids?: string[] | null;
  assigned_to_id?: string | null;
  assigned_to?: UserBrief | null;
  created_by?: UserBrief | null;
  created_at: string;
  updated_at?: string;
  metadata_json?: Record<string, unknown> | null;
};

export type NotificationItem = {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  link: string | null;
  is_read: boolean;
  created_at: string;
};

export type ActivityItem = {
  id: string;
  action: string;
  description: string;
  case_id?: string | null;
  actor_role?: string | null;
  created_at: string;
  user?: UserBrief | null;
};

export type ReportItem = {
  id: string;
  case_id: string;
  title: string;
  format: string;
  content: string | null;
  created_at: string;
  summary_json?: Record<string, unknown> | null;
};

export type Page<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type DashboardStats = {
  active_cases: number;
  completed_cases: number;
  evidence_uploaded: number;
  investigators: number;
  reports: number;
  monthly_cases: { month: string; count: number }[];
  evidence_types: { type: string; count: number }[];
  priority_distribution: { priority: string; count: number }[];
  recent_activity: ActivityItem[];
  recent_cases: InvestigationCase[];
  latest_uploads: EvidenceItem[];
  case_status_counts?: Record<string, number>;
  ai_processing?: { processed: number; processing: number; failed: number; pending: number };
  risk_distribution?: { low: number; medium: number; high: number; critical: number };
  lead_review?: { pending: number; verified: number; rejected: number; modified: number };
};

export type AdminUser = {
  id: string;
  full_name: string;
  email: string;
  role: string;
  department: string | null;
  department_id?: string | null;
  phone?: string | null;
  badge_number?: string | null;
  profile_image_url?: string | null;
  is_active: boolean;
  created_at: string;
  last_login?: string | null;
};

export type AdminCase = InvestigationCase & {
  department_id?: string | null;
  evidence_count?: number;
  notes_count?: number;
  timeline_count?: number;
  superior_officer?: UserBrief | null;
  investigators?: UserBrief[];
};

export type AdminDashboardStats = {
  superior_officers: number;
  investigators: number;
  total_cases: number;
  open_cases: number;
  closed_cases: number;
  evidence_count: number;
  monthly_cases: { month: string; count: number }[];
  evidence_types: { type: string; count: number }[];
  priority_distribution: { priority: string; count: number }[];
  recent_activity: ActivityItem[];
  recent_cases: AdminCase[];
  notifications: NotificationItem[];
  storage_bytes: number;
};

export type AdminEvidence = EvidenceItem & {
  case_number?: string | null;
};

export type AdminReportGenerated = {
  id?: string | null;
  title: string;
  report_type: string;
  format: string;
  content: string;
  created_at?: string | null;
  summary?: Record<string, unknown>;
};

export type SearchResult = {
  cases: InvestigationCase[];
  evidence: EvidenceItem[];
  notes: NoteItem[];
  investigators: UserBrief[];
  reports: ReportItem[];
  leads?: LeadItem[];
  timeline?: TimelineItem[];
};

export type AIEngineStatus = {
  llm: { provider: string; model: string; available: boolean; mode: string; disclaimer: string };
  ocr_engine: string;
  stt_engine: string;
  mode: string;
  disclaimer: string;
};

// ---- AI Intelligence & Forensic Decision-Support Types ----

export type ExtractedEntity = {
  type: string;
  raw_value: string;
  normalized_value: string;
  confidence: number;
  context?: string;
  source_evidence_id?: string;
  occurrences?: number;
  evidence_ids?: string[];
  evidence_names?: string[];
  contexts?: string[];
};

export type EvidenceAnalysis = {
  id: string;
  case_id: string;
  original_name: string;
  filename: string;
  file_type: string;
  mime_type: string | null;
  file_size: number;
  sha256_hash: string;
  upload_date: string | null;
  is_duplicate: boolean;
  duplicate_of_id: string | null;
  duplicate_warning: string | null;
  processing_status: string;
  pipeline_steps: Record<string, unknown>;
  metadata: Record<string, unknown>;
  ocr_text: string;
  ocr_engine: string;
  ocr_confidence: number;
  speech_transcript: string;
  stt_engine: string;
  extracted_entities: ExtractedEntity[];
  entity_count: number;
  risk_score: number | null;
  disclaimer: string;
};

export type RiskFactor = {
  factor: string;
  points: number;
  detail: string;
};

export type CaseRiskAssessment = {
  case_id: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  badge_color: string;
  factors: RiskFactor[];
  top_factors?: string[];
  disclaimer: string;
};

export type CaseCorrelation = {
  entity_type: string;
  normalized_value: string;
  evidence_count: number;
  supporting_evidence_ids: string[];
  supporting_evidence_names: string[];
  confidence_score: number;
  explanation: string;
};

export type GraphNode = {
  id: string;
  label: string;
  kind: string;
  color: string;
  size: number;
  file_type?: string;
  evidence_id?: string;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
  confidence: number;
  ai_generated: boolean;
  description: string;
};

export type CaseGraphData = {
  case_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type RAGCitation = {
  evidence_id: string;
  evidence_name: string;
  file_type: string;
  reference: string;
};

export type RAGMatchingEvidence = {
  id: string;
  original_name: string;
  file_type: string;
  snippet: string;
  sha256: string;
  match_score: number;
};

export type RAGSearchResult = {
  query: string;
  answer: string;
  citations: RAGCitation[];
  matching_evidence: RAGMatchingEvidence[];
  total_matches: number;
  disclaimer: string;
};

export type InvestigationSummary = {
  case_id: string;
  case_number: string;
  title: string;
  priority: string;
  status: string;
  generated_at: string;
  lead_investigator: string;
  supervisor: string;
  evidence_count: number;
  evidence_summary: {
    id: string;
    name: string;
    file_type: string;
    size_kb: number;
    sha256: string;
    is_duplicate: boolean;
    has_ocr: boolean;
    has_transcript: boolean;
  }[];
  important_entities: {
    type: string;
    value: string;
    source_evidence: string;
    confidence: number;
  }[];
  key_relationships: {
    source: string;
    target: string;
    type: string;
    description?: string | null;
    confidence: number;
    status: string;
  }[];
  timeline_event_count: number;
  timeline_events: {
    time: string;
    title: string;
    description: string;
  }[];
  verified_findings: {
    id: string;
    title: string;
    priority: string;
    status: string;
    review_state: string;
    why: string;
    reviewer_note: string;
  }[];
  unverified_ai_leads: {
    id: string;
    title: string;
    priority: string;
    status: string;
    review_state: string;
    why: string;
    reviewer_note: string;
  }[];
  rejected_leads: {
    id: string;
    title: string;
    priority: string;
    status: string;
    review_state: string;
    why: string;
    reviewer_note: string;
  }[];
  summary_text: string;
  disclaimer: string;
};

export type PipelineRunResult = {
  success: boolean;
  case_id: string;
  evidence_processed: number;
  total_evidence: number;
  correlations_found: number;
  timeline_events_generated: number;
  risk_score: number;
  risk_level: string;
  leads_generated: number;
};

export type RepositoryItem = {
  id: string;
  case_id: string;
  case_number?: string | null;
  case_title?: string | null;
  filename: string;
  original_name: string;
  file_type: string;
  category: string;
  mime_type: string | null;
  file_size: number;
  sha256_hash: string;
  description: string | null;
  source_type: string;
  processing_status: string;
  synthetic: boolean;
  dataset: string;
  tags?: string[] | null;
  metadata_json?: Record<string, unknown> | null;
  imported_evidence_id?: string | null;
  created_at: string;
  disclaimer?: string;
};

export type RepositoryGenerateResult = {
  success: boolean;
  case_id?: string;
  case_number?: string;
  theme?: string;
  created: number;
  skipped_existing?: number;
  files?: string[];
  cases?: { case_number: string; created: number; ok?: boolean }[];
  total_files?: number;
  disclaimer?: string;
  job_id?: string;
  status?: string;
};
