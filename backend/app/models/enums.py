"""Shared domain enums for CyberShield investigation platform."""

import enum


class CasePriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class CaseStatus(str, enum.Enum):
    open = "open"
    under_review = "under_review"
    evidence_collection = "evidence_collection"
    analysis = "analysis"
    completed = "completed"
    archived = "archived"


class LeadStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"
    dismissed = "dismissed"


class LeadPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RelationshipType(str, enum.Enum):
    evidence_to_evidence = "evidence_to_evidence"
    evidence_to_person = "evidence_to_person"
    evidence_to_device = "evidence_to_device"
    evidence_to_location = "evidence_to_location"
    person_to_person = "person_to_person"
    person_to_device = "person_to_device"
    other = "other"


class EntityKind(str, enum.Enum):
    evidence = "evidence"
    person = "person"
    device = "device"
    location = "location"
    other = "other"


class TimelineEventType(str, enum.Enum):
    case_created = "case_created"
    case_updated = "case_updated"
    status_updated = "status_updated"
    investigator_assigned = "investigator_assigned"
    evidence_uploaded = "evidence_uploaded"
    evidence_deleted = "evidence_deleted"
    note_added = "note_added"
    note_updated = "note_updated"
    lead_created = "lead_created"
    relationship_created = "relationship_created"
    report_generated = "report_generated"
    manual = "manual"


class NotificationType(str, enum.Enum):
    case_assigned = "case_assigned"
    evidence_uploaded = "evidence_uploaded"
    status_changed = "status_changed"
    new_note = "new_note"
    lead_created = "lead_created"
    user_created = "user_created"
    case_closed = "case_closed"
    general = "general"


class ActivityAction(str, enum.Enum):
    login = "login"
    logout = "logout"
    create = "create"
    update = "update"
    delete = "delete"
    download = "download"
    view = "view"
    export = "export"
    password_reset = "password_reset"


class ReportFormat(str, enum.Enum):
    pdf = "pdf"
    csv = "csv"
    html = "html"
