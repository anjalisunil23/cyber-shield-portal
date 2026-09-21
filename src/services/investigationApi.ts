import { apiClient } from "@/services/apiClient";
import type {
  ActivityItem,
  AdminCase,
  AdminDashboardStats,
  AdminEvidence,
  AdminReportGenerated,
  AdminUser,
  CaseInvestigator,
  CasePriority,
  CaseStatus,
  CaseTeamResponse,
  ChatConversation,
  ChatMessage,
  DashboardStats,
  EvidenceItem,
  InvestigationCase,
  LeadItem,
  NoteItem,
  NotificationItem,
  Page,
  RelationshipItem,
  ReportItem,
  SearchResult,
  TimelineItem,
  UserBrief,
  EvidenceAnalysis,
  CaseRiskAssessment,
  CaseCorrelation,
  ExtractedEntity,
  CaseGraphData,
  RAGSearchResult,
  InvestigationSummary,
  PipelineRunResult,
} from "@/services/types";

export const investigationApi = {
  // Cases
  listCases: (params?: Record<string, string | number | undefined>) =>
    apiClient.get<Page<InvestigationCase>>("/api/cases", { params }).then((r) => r.data),

  getCase: (id: string) => apiClient.get<InvestigationCase>(`/api/cases/${id}`).then((r) => r.data),

  createCase: (body: {
    title: string;
    description?: string;
    priority?: CasePriority;
    status?: CaseStatus;
    notes?: string;
    assignee_ids?: string[];
    investigator_lead_id?: string;
  }) => apiClient.post<InvestigationCase>("/api/cases", body).then((r) => r.data),

  updateCase: (
    id: string,
    body: Partial<{
      title: string;
      description: string;
      priority: CasePriority;
      status: CaseStatus;
      notes: string;
    }>,
  ) => apiClient.patch<InvestigationCase>(`/api/cases/${id}`, body).then((r) => r.data),

  deleteCase: (id: string) => apiClient.delete(`/api/cases/${id}`).then((r) => r.data),

  assignCase: (id: string, user_id: string, is_primary = false) =>
    apiClient
      .post<InvestigationCase>(`/api/cases/${id}/assign`, { user_id, is_primary })
      .then((r) => r.data),

  getCaseTeam: (caseId: string) =>
    apiClient.get<CaseTeamResponse>(`/api/cases/${caseId}/team`).then((r) => r.data),

  addCaseTeamInvestigators: (caseId: string, investigatorIds: string[]) =>
    apiClient
      .post<CaseTeamResponse>(`/api/cases/${caseId}/team`, { investigator_ids: investigatorIds })
      .then((r) => r.data),

  addTeamInvestigators: (caseId: string, body: { investigator_ids: string[] }) =>
    apiClient.post<CaseTeamResponse>(`/api/cases/${caseId}/team`, body).then((r) => r.data),

  removeCaseTeamInvestigator: (caseId: string, investigatorUserId: string) =>
    apiClient
      .delete<CaseTeamResponse>(`/api/cases/${caseId}/team/${investigatorUserId}`)
      .then((r) => r.data),

  removeTeamInvestigator: (caseId: string, userId: string) =>
    apiClient.delete<CaseTeamResponse>(`/api/cases/${caseId}/team/${userId}`).then((r) => r.data),

  reassignCaseLead: (
    caseId: string,
    leadIdOrBody:
      | string
      | {
          new_investigator_lead_id?: string;
          new_lead_id?: string;
          keep_previous_lead?: boolean;
          keep_previous_as_investigator?: boolean;
        },
    keepPreviousLead = true,
  ) => {
    const payload =
      typeof leadIdOrBody === "string"
        ? {
            new_lead_id: leadIdOrBody,
            new_investigator_lead_id: leadIdOrBody,
            keep_previous_lead: keepPreviousLead,
          }
        : leadIdOrBody;
    return apiClient
      .post<CaseTeamResponse>(`/api/cases/${caseId}/reassign-lead`, payload)
      .then((r) => r.data);
  },

  submitCaseForReview: (caseId: string) =>
    apiClient.post<InvestigationCase>(`/api/cases/${caseId}/submit-review`).then((r) => r.data),

  reviewCase: (
    caseId: string,
    body: { action: "approve" | "request_changes"; review_comment?: string },
  ) => apiClient.post<InvestigationCase>(`/api/cases/${caseId}/review`, body).then((r) => r.data),

  closeCase: (caseId: string) =>
    apiClient.post<InvestigationCase>(`/api/cases/${caseId}/close`).then((r) => r.data),

  // Chat & Communication
  listChatConversations: () =>
    apiClient.get<ChatConversation[]>("/api/chat/conversations").then((r) => r.data),

  getChatConversation: (conversationId: string) =>
    apiClient
      .get<ChatConversation>(`/api/chat/conversations/${conversationId}`)
      .then((r) => r.data),

  listChatMessages: (conversationId: string, limit = 100, before?: string) =>
    apiClient
      .get<ChatMessage[]>(`/api/chat/conversations/${conversationId}/messages`, {
        params: { limit, before },
      })
      .then((r) => r.data),

  sendChatMessage: (conversationId: string, content: string) =>
    apiClient
      .post<ChatMessage>(`/api/chat/conversations/${conversationId}/messages`, { content })
      .then((r) => r.data),

  getOrCreateDirectChat: (targetUserId: string, caseId?: string) =>
    apiClient
      .post<ChatConversation>("/api/chat/direct", { target_user_id: targetUserId, case_id: caseId })
      .then((r) => r.data),

  getCaseGroupChat: (caseId: string) =>
    apiClient.get<ChatConversation>(`/api/chat/case/${caseId}/group`).then((r) => r.data),

  listChatContacts: () => apiClient.get<UserBrief[]>("/api/chat/contacts").then((r) => r.data),

  markChatConversationRead: (conversationId: string) =>
    apiClient
      .post<{ success: boolean }>(`/api/chat/conversations/${conversationId}/read`)
      .then((r) => r.data),

  getChatUnreadCount: () =>
    apiClient.get<{ unread_total: number }>("/api/chat/unread-count").then((r) => r.data),

  // Evidence
  listEvidence: (caseId: string, params?: Record<string, string | number | undefined>) =>
    apiClient
      .get<Page<EvidenceItem>>(`/api/cases/${caseId}/evidence`, { params })
      .then((r) => r.data),

  uploadEvidence: (caseId: string, file: File, description?: string, tags?: string[]) => {
    const form = new FormData();
    form.append("file", file);
    if (description) form.append("description", description);
    if (tags?.length) form.append("tags", JSON.stringify(tags));
    return apiClient
      .post<EvidenceItem>(`/api/cases/${caseId}/evidence`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  getEvidence: (id: string) =>
    apiClient.get<EvidenceItem>(`/api/evidence/${id}`).then((r) => r.data),

  downloadEvidenceUrl: (id: string) => `/api/evidence/${id}/download`,

  deleteEvidence: (id: string) => apiClient.delete(`/api/evidence/${id}`).then((r) => r.data),

  // Notes
  listNotes: (caseId: string) =>
    apiClient.get<NoteItem[]>(`/api/cases/${caseId}/notes`).then((r) => r.data),
  createNote: (caseId: string, body: { title?: string; body: string; is_pinned?: boolean }) =>
    apiClient.post<NoteItem>(`/api/cases/${caseId}/notes`, body).then((r) => r.data),
  updateNote: (id: string, body: Partial<{ title: string; body: string; is_pinned: boolean }>) =>
    apiClient.patch<NoteItem>(`/api/notes/${id}`, body).then((r) => r.data),
  deleteNote: (id: string) => apiClient.delete(`/api/notes/${id}`).then((r) => r.data),

  // Timeline
  listTimeline: (caseId: string) =>
    apiClient.get<TimelineItem[]>(`/api/cases/${caseId}/timeline`).then((r) => r.data),
  createTimeline: (
    caseId: string,
    body: {
      title: string;
      description?: string;
      event_type?: string;
      event_at?: string;
      related_evidence_id?: string;
    },
  ) => apiClient.post<TimelineItem>(`/api/cases/${caseId}/timeline`, body).then((r) => r.data),
  deleteTimeline: (id: string) => apiClient.delete(`/api/timeline/${id}`).then((r) => r.data),

  // Relationships
  listRelationships: (caseId: string) =>
    apiClient.get<RelationshipItem[]>(`/api/cases/${caseId}/relationships`).then((r) => r.data),
  createRelationship: (
    caseId: string,
    body: {
      source_label: string;
      source_kind: string;
      source_id: string;
      target_label: string;
      target_kind: string;
      target_id: string;
      relationship_type?: string;
      description?: string;
    },
  ) =>
    apiClient
      .post<RelationshipItem>(`/api/cases/${caseId}/relationships`, body)
      .then((r) => r.data),
  deleteRelationship: (id: string) =>
    apiClient.delete(`/api/relationships/${id}`).then((r) => r.data),

  // Leads
  listLeads: (caseId: string) =>
    apiClient.get<LeadItem[]>(`/api/cases/${caseId}/leads`).then((r) => r.data),
  createLead: (
    caseId: string,
    body: {
      title: string;
      description?: string;
      priority?: string;
      status?: string;
      justification?: string;
      related_evidence_ids?: string[];
      assigned_to_id?: string;
    },
  ) => apiClient.post<LeadItem>(`/api/cases/${caseId}/leads`, body).then((r) => r.data),
  updateLead: (
    id: string,
    body: {
      status?: string;
      review_comment?: string;
      priority?: string;
      title?: string;
      description?: string;
      justification?: string;
      related_evidence_ids?: string[];
    },
  ) => apiClient.patch<LeadItem>(`/api/leads/${id}`, body).then((r) => r.data),
  deleteLead: (id: string) => apiClient.delete(`/api/leads/${id}`).then((r) => r.data),

  // Reports
  listReports: (caseId: string) =>
    apiClient.get<ReportItem[]>(`/api/cases/${caseId}/reports`).then((r) => r.data),
  createReport: (
    caseId: string,
    body: { title?: string; case_summary?: string; format?: string },
  ) => apiClient.post<ReportItem>(`/api/cases/${caseId}/reports`, body).then((r) => r.data),
  exportReport: (id: string) =>
    apiClient.get<string>(`/api/reports/${id}/export`).then((r) => r.data),

  // Platform
  dashboardStats: () => apiClient.get<DashboardStats>("/api/dashboard/stats").then((r) => r.data),
  search: (q: string) =>
    apiClient.get<SearchResult>("/api/search", { params: { q } }).then((r) => r.data),
  notifications: (unreadOnly = false) =>
    apiClient
      .get<NotificationItem[]>("/api/notifications", { params: { unread_only: unreadOnly } })
      .then((r) => r.data),
  listNotifications: (params?: { unread_only?: boolean }) =>
    apiClient.get<NotificationItem[]>("/api/notifications", { params }).then((r) => r.data),
  unreadCount: () =>
    apiClient.get<{ count: number }>("/api/notifications/unread-count").then((r) => r.data),
  markRead: (id: string) => apiClient.post(`/api/notifications/${id}/read`).then((r) => r.data),
  markNotificationRead: (id: string) =>
    apiClient.post(`/api/notifications/${id}/read`).then((r) => r.data),
  markAllRead: () => apiClient.post(`/api/notifications/read-all`).then((r) => r.data),
  activity: (page = 1, caseId?: string) =>
    apiClient
      .get<Page<ActivityItem>>("/api/activity", { params: { page, case_id: caseId } })
      .then((r) => r.data),
  listUsers: (params?: { q?: string; page?: number; page_size?: number } | string) => {
    const p = typeof params === "string" ? { q: params } : params;
    return apiClient
      .get<Page<UserBrief & { department?: string | null; is_active?: boolean }>>("/api/users", {
        params: p,
      })
      .then((r) => r.data);
  },
  createUser: (body: {
    full_name: string;
    email: string;
    password: string;
    confirm_password: string;
    role: string;
    department?: string | null;
  }) => apiClient.post("/api/admin/users", body).then((r) => r.data),
  updateUserAdmin: (id: string, body: Record<string, unknown>) =>
    apiClient.patch(`/api/admin/users/${id}`, body).then((r) => r.data),
  listDepartments: () =>
    apiClient
      .get<
        {
          id: string;
          name: string;
          code: string | null;
          description: string | null;
          is_active: boolean;
        }[]
      >("/api/departments")
      .then((r) => r.data),
  createDepartment: (body: { name: string; code?: string; description?: string }) =>
    apiClient.post("/api/departments", body).then((r) => r.data),
  me: () =>
    apiClient
      .get<{
        id: string;
        full_name: string;
        email: string;
        role: string;
        department: string | null;
        department_id?: string | null;
        is_active: boolean;
      }>("/api/auth/me")
      .then((r) => r.data),
  updateMe: (body: { full_name?: string; department?: string }) =>
    apiClient.patch("/api/auth/me", body).then((r) => r.data),

  // ---- Admin module (department-scoped) ----
  adminDashboard: () =>
    apiClient.get<AdminDashboardStats>("/api/admin/dashboard").then((r) => r.data),

  adminListUsers: (params?: Record<string, string | number | boolean | undefined>) =>
    apiClient.get<Page<AdminUser>>("/api/admin/users", { params }).then((r) => r.data),

  adminGetUser: (id: string) =>
    apiClient.get<AdminUser>(`/api/admin/users/${id}`).then((r) => r.data),

  adminCreateUser: (body: {
    full_name: string;
    email: string;
    phone?: string;
    badge_number?: string;
    role: "superior_officer" | "investigator";
    password: string;
    confirm_password: string;
    is_active?: boolean;
    department?: string;
  }) => apiClient.post<AdminUser>("/api/admin/users", body).then((r) => r.data),

  adminUpdateUser: (id: string, body: Record<string, unknown>) =>
    apiClient.patch<AdminUser>(`/api/admin/users/${id}`, body).then((r) => r.data),

  adminDeleteUser: (id: string) => apiClient.delete(`/api/admin/users/${id}`).then((r) => r.data),

  adminSuspendUser: (id: string) =>
    apiClient.post<AdminUser>(`/api/admin/users/${id}/suspend`).then((r) => r.data),

  adminActivateUser: (id: string) =>
    apiClient.post<AdminUser>(`/api/admin/users/${id}/activate`).then((r) => r.data),

  adminResetPassword: (id: string, new_password: string, confirm_password: string) =>
    apiClient
      .post<AdminUser>(`/api/admin/users/${id}/reset-password`, { new_password, confirm_password })
      .then((r) => r.data),

  adminUploadAvatar: (id: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return apiClient
      .post<AdminUser>(`/api/admin/users/${id}/avatar`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  adminListCases: (params?: Record<string, string | number | undefined>) =>
    apiClient.get<Page<AdminCase>>("/api/admin/cases", { params }).then((r) => r.data),

  adminGetCase: (id: string) =>
    apiClient.get<AdminCase>(`/api/admin/cases/${id}`).then((r) => r.data),

  adminCreateCase: (body: {
    title: string;
    description?: string;
    priority?: CasePriority;
    status?: CaseStatus;
    notes?: string;
    superior_officer_id?: string;
    investigator_ids?: string[];
  }) => apiClient.post<AdminCase>("/api/admin/cases", body).then((r) => r.data),

  adminUpdateCase: (id: string, body: Record<string, unknown>) =>
    apiClient.patch<AdminCase>(`/api/admin/cases/${id}`, body).then((r) => r.data),

  adminDeleteCase: (id: string) => apiClient.delete(`/api/admin/cases/${id}`).then((r) => r.data),

  adminAssignCase: (
    id: string,
    body: { superior_officer_id?: string; investigator_ids?: string[] },
  ) => apiClient.post<AdminCase>(`/api/admin/cases/${id}/assign`, body).then((r) => r.data),

  adminArchiveCase: (id: string) =>
    apiClient.post<AdminCase>(`/api/admin/cases/${id}/archive`).then((r) => r.data),

  adminListEvidence: (params?: Record<string, string | number | undefined>) =>
    apiClient.get<Page<AdminEvidence>>("/api/admin/evidence", { params }).then((r) => r.data),

  adminDeleteEvidence: (id: string) =>
    apiClient.delete(`/api/admin/evidence/${id}`).then((r) => r.data),

  adminDownloadEvidence: async (id: string, filename?: string) => {
    const res = await apiClient.get(`/api/evidence/${id}/download`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || "evidence.bin";
    a.click();
    URL.revokeObjectURL(url);
  },

  adminEvidenceStorage: () =>
    apiClient
      .get<{
        total_files: number;
        total_bytes: number;
        by_type: { type: string; count: number; bytes: number }[];
      }>("/api/admin/evidence/storage")
      .then((r) => r.data),

  adminListReports: (page = 1) =>
    apiClient.get<Page<ReportItem>>("/api/admin/reports", { params: { page } }).then((r) => r.data),

  adminGenerateReport: (body: {
    report_type: "case" | "department" | "investigator" | "evidence";
    case_id?: string;
    investigator_id?: string;
    format?: "csv" | "pdf" | "html";
    title?: string;
  }) =>
    apiClient.post<AdminReportGenerated>("/api/admin/reports/generate", body).then((r) => r.data),

  adminActivity: (page = 1) =>
    apiClient
      .get<Page<ActivityItem>>("/api/admin/activity", { params: { page } })
      .then((r) => r.data),

  // ---- AI Intelligence & Forensic Decision-Support ----
  processEvidence: (evidenceId: string) =>
    apiClient
      .post<{ success: boolean; status: string; pipeline_steps: Record<string, unknown> }>(
        `/api/evidence/${evidenceId}/process`,
      )
      .then((r) => r.data),

  getEvidenceAnalysis: (evidenceId: string) =>
    apiClient.get<EvidenceAnalysis>(`/api/evidence/${evidenceId}/analysis`).then((r) => r.data),

  runCasePipeline: (caseId: string) =>
    apiClient.post<PipelineRunResult>(`/api/cases/${caseId}/pipeline`).then((r) => r.data),

  getCaseCorrelations: (caseId: string) =>
    apiClient.get<CaseCorrelation[]>(`/api/cases/${caseId}/correlations`).then((r) => r.data),

  getCaseEntities: (caseId: string) =>
    apiClient.get<ExtractedEntity[]>(`/api/cases/${caseId}/entities`).then((r) => r.data),

  getCaseRisk: (caseId: string) =>
    apiClient.get<CaseRiskAssessment>(`/api/cases/${caseId}/risk`).then((r) => r.data),

  getCaseGraph: (caseId: string) =>
    apiClient.get<CaseGraphData>(`/api/cases/${caseId}/graph`).then((r) => r.data),

  searchCaseEvidence: (caseId: string, query: string) =>
    apiClient.post<RAGSearchResult>(`/api/cases/${caseId}/search`, { query }).then((r) => r.data),

  getCaseSummary: (caseId: string) =>
    apiClient.post<InvestigationSummary>(`/api/cases/${caseId}/summarize`).then((r) => r.data),

  verifyLead: (leadId: string, reason?: string) =>
    apiClient
      .post<{ success: boolean; lead_id: string; status: string; review_state: string }>(
        `/api/leads/${leadId}/verify`,
        { reason },
      )
      .then((r) => r.data),

  rejectLead: (leadId: string, reason?: string) =>
    apiClient
      .post<{ success: boolean; lead_id: string; status: string; review_state: string }>(
        `/api/leads/${leadId}/reject`,
        { reason },
      )
      .then((r) => r.data),

  modifyLead: (
    leadId: string,
    payload: { title?: string; description?: string; reason?: string },
  ) =>
    apiClient
      .post<{
        success: boolean;
        lead_id: string;
        title: string;
        status: string;
        review_state: string;
      }>(`/api/leads/${leadId}/modify`, payload)
      .then((r) => r.data),

  seedSyntheticCase: () =>
    apiClient
      .post<{ success: boolean; case_id: string; case_number: string; title: string }>(
        "/api/demo/seed-synthetic-case",
      )
      .then((r) => r.data),

  getAIStatus: () =>
    apiClient.get<import("./types").AIEngineStatus>("/api/ai/status").then((r) => r.data),

  getCaseAuditLog: (caseId: string, page = 1) =>
    apiClient
      .get<Page<ActivityItem>>(`/api/cases/${caseId}/audit-log`, { params: { page } })
      .then((r) => r.data),

  exportCaseIntelligence: (caseId: string) =>
    apiClient
      .get<Record<string, unknown>>(`/api/cases/${caseId}/intelligence-export`)
      .then((r) => r.data),

  listRepository: (params?: Record<string, string | number | undefined>) =>
    apiClient
      .get<Page<import("./types").RepositoryItem>>("/api/evidence-repository", { params })
      .then((r) => r.data),

  getRepositoryItem: (id: string) =>
    apiClient
      .get<import("./types").RepositoryItem>(`/api/evidence-repository/${id}`)
      .then((r) => r.data),

  previewRepository: async (id: string, mime?: string | null, fileType?: string) => {
    const isMedia =
      (mime || "").startsWith("image/") ||
      (mime || "").startsWith("audio/") ||
      (mime || "").startsWith("video/") ||
      mime === "application/pdf" ||
      fileType === "image" ||
      fileType === "audio" ||
      fileType === "video";
    if (isMedia) {
      const res = await apiClient.get(`/api/evidence-repository/${id}/preview`, {
        responseType: "blob",
      });
      return {
        kind: "blob" as const,
        url: URL.createObjectURL(res.data as Blob),
        mime: mime || "application/octet-stream",
      };
    }
    const res = await apiClient.get<{ text: string; filename: string }>(
      `/api/evidence-repository/${id}/preview`,
    );
    return { kind: "text" as const, text: res.data.text || "", filename: res.data.filename };
  },

  downloadRepository: async (id: string, filename: string) => {
    const res = await apiClient.get(`/api/evidence-repository/${id}/download`, {
      responseType: "blob",
    });
    const url = URL.createObjectURL(res.data as Blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  },

  generateRepository: (body: {
    case_id: string;
    types?: string[];
    count?: number;
    complete?: boolean;
  }) =>
    apiClient
      .post<import("./types").RepositoryGenerateResult>("/api/evidence-repository/generate", body)
      .then((r) => r.data),

  generateRepositoryAll: () =>
    apiClient
      .post<import("./types").RepositoryGenerateResult>("/api/evidence-repository/generate-all")
      .then((r) => r.data),

  getRepositoryJob: (jobId: string) =>
    apiClient
      .get<{
        status: string;
        completed?: number;
        total_cases?: number;
        total_files?: number;
        error?: string;
        cases?: { case_number: string; created: number; ok: boolean }[];
      }>(`/api/evidence-repository/jobs/${jobId}`)
      .then((r) => r.data),

  addRepositoryToCase: (id: string, caseId: string) =>
    apiClient
      .post<EvidenceItem>(`/api/evidence-repository/${id}/add-to-case`, { case_id: caseId })
      .then((r) => r.data),

  resetSyntheticRepository: () =>
    apiClient
      .delete<{
        success: boolean;
        repository_items_deleted: number;
        imported_evidence_deleted: number;
        message: string;
      }>("/api/evidence-repository/synthetic")
      .then((r) => r.data),
};
