"""Seed comprehensive synthetic data into PostgreSQL database for testing."""

from uuid import uuid4
from datetime import datetime, timezone
from app.db.session import get_db
from app.models.department import Department
from app.models.user import User, UserRole
from app.models.case import Case, CaseAssignment
from app.models.evidence import Evidence
from app.models.note import Note
from app.models.timeline import TimelineEvent
from app.models.lead import ManualLead
from app.models.relationship import Relationship
from app.models.enums import CasePriority, CaseStatus, LeadStatus, LeadPriority, RelationshipType, EntityKind, TimelineEventType
from app.core.security import hash_password

DEMO_USERS = [
    {
        "full_name": "Major Admin User",
        "email": "admin@cybershield.gov",
        "password": "Admin123!",
        "role": UserRole.major_admin,
        "department": "Executive Command",
        "badge_number": "MA-001",
    },
    {
        "full_name": "System Administrator",
        "email": "sysadmin@cybershield.gov",
        "password": "Admin123!",
        "role": UserRole.admin,
        "department": "IT & Security",
        "badge_number": "ADM-002",
    },
    {
        "full_name": "Superior Officer",
        "email": "supervisor@cybershield.gov",
        "password": "Supervisor123!",
        "role": UserRole.supervisor,
        "department": "Digital Forensics Division",
        "badge_number": "SUP-003",
    },
    {
        "full_name": "Lead Investigator",
        "email": "investigator@cybershield.gov",
        "password": "Password123!",
        "role": UserRole.investigator,
        "department": "Cyber Crime Unit",
        "badge_number": "INV-004",
    },
]

def seed():
    db = next(get_db())

    # 1. Departments
    dept_ccu = db.query(Department).filter(Department.code == "CCU").first()
    if not dept_ccu:
        dept_ccu = Department(id=uuid4(), name="Cyber Crime Unit", code="CCU", description="Primary cyber investigation unit", is_active=True)
        db.add(dept_ccu)

    dept_dfu = db.query(Department).filter(Department.code == "DFU").first()
    if not dept_dfu:
        dept_dfu = Department(id=uuid4(), name="Digital Forensics Unit", code="DFU", description="Hardware & media analysis unit", is_active=True)
        db.add(dept_dfu)

    db.flush()

    # 2. Users
    user_map = {}
    for user_data in DEMO_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            dept_id = dept_ccu.id if "Cyber" in user_data["department"] else dept_dfu.id
            existing = User(
                full_name=user_data["full_name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                department=user_data["department"],
                department_id=dept_id,
                badge_number=user_data["badge_number"],
                is_active=True
            )
            db.add(existing)
            db.flush()
        user_map[user_data["role"]] = existing

    # 3. Cases
    inv = user_map.get(UserRole.investigator)
    sup = user_map.get(UserRole.supervisor)

    c1 = db.query(Case).filter(Case.case_number == "CS-2026-0001").first()
    if not c1 and inv:
        c1 = Case(
            id=uuid4(),
            case_number="CS-2026-0001",
            title="Cross-border messaging fraud investigation",
            description="Analysis of intercepted messaging platform traffic and fraudulent transactions",
            priority=CasePriority.critical,
            status=CaseStatus.analysis,
            notes="Requires urgent device correlation",
            created_by_id=inv.id,
            department_id=inv.department_id,
        )
        db.add(c1)
        db.flush()

        # Assignment
        db.add(CaseAssignment(case_id=c1.id, user_id=inv.id, assigned_by_id=sup.id if sup else inv.id, is_primary=True))
        if sup:
            db.add(CaseAssignment(case_id=c1.id, user_id=sup.id, assigned_by_id=sup.id, is_primary=False))

        # Sample Evidence
        ev1 = Evidence(
            id=uuid4(),
            case_id=c1.id,
            filename="whatsapp_dump_2026.json",
            original_name="whatsapp_dump_2026.json",
            file_type="json",
            mime_type="application/json",
            file_size=1048576,
            storage_path=f"uploads/{c1.id}/whatsapp_dump_2026.json",
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            description="Exported chat logs containing transaction IDs",
            tags=["chat_export", "fraud", "messaging"],
            uploaded_by_id=inv.id,
            is_duplicate=False
        )
        db.add(ev1)

        # Sample Note
        db.add(Note(case_id=c1.id, author_id=inv.id, title="Initial Triage", body="Identified 3 recurring phone numbers across chat exports.", is_pinned=True))

        # Sample Timeline
        db.add(TimelineEvent(case_id=c1.id, event_type=TimelineEventType.case_created, title="Case Opened", description="Investigation launched based on financial intelligence report.", created_by_id=inv.id))

        # Sample Lead
        db.add(ManualLead(case_id=c1.id, title="Track beneficiary bank account", description="Trace account number 994829104 at Global Bank", priority=LeadPriority.high, status=LeadStatus.in_progress, assigned_to_id=inv.id, created_by_id=inv.id))

        # Sample Relationship
        db.add(Relationship(case_id=c1.id, relationship_type=RelationshipType.evidence_to_person, source_kind=EntityKind.evidence, source_id=str(ev1.id), source_label="whatsapp_dump_2026.json", target_kind=EntityKind.person, target_id="suspect-001", target_label="Suspect A", description="Chat log references suspect alias", ai_generated=False))

    c2 = db.query(Case).filter(Case.case_number == "CS-2026-0002").first()
    if not c2 and inv:
        c2 = Case(
            id=uuid4(),
            case_number="CS-2026-0002",
            title="Encrypted storage drive forensic extraction",
            description="Seized hard drive from suspected cybercrime hub",
            priority=CasePriority.high,
            status=CaseStatus.evidence_collection,
            notes="Media pending bit-stream image validation",
            created_by_id=inv.id,
            department_id=inv.department_id,
        )
        db.add(c2)
        db.flush()
        db.add(CaseAssignment(case_id=c2.id, user_id=inv.id, assigned_by_id=inv.id, is_primary=True))

    db.commit()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed()
