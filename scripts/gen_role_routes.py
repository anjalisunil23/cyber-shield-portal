from pathlib import Path

root = Path(r"d:/cybershield/cyber-shield-portal/src/routes")

layouts = {
    "major-admin.tsx": ("major-admin", "major_admin"),
    "admin.tsx": ("admin", "admin"),
    "superior.tsx": ("superior", "superior_officer"),
    "investigator.tsx": ("investigator", "investigator"),
}

for fname, (path_prefix, role) in layouts.items():
    (root / fname).write_text(
        f'''import {{ createFileRoute }} from "@tanstack/react-router";
import {{ RoleShell }} from "@/components/layouts/RoleShell";

export const Route = createFileRoute("/{path_prefix}")({{
  component: () => <RoleShell role="{role}" />,
}});
''',
        encoding="utf-8",
    )
    print("wrote", fname)


def page(dir_name: str, route_path: str, title: str, subtitle: str) -> None:
    d = root / dir_name
    d.mkdir(exist_ok=True)
    fname = route_path.rstrip("/").split("/")[-1] + ".tsx"
    (d / fname).write_text(
        f'''import {{ createFileRoute }} from "@tanstack/react-router";
import {{ PageHeader, Panel }} from "@/components/layouts/DashboardWidgets";

export const Route = createFileRoute("{route_path}")({{
  component: Page,
}});

function Page() {{
  return (
    <div>
      <PageHeader title="{title}" subtitle="{subtitle}" />
      <Panel>
        <p className="text-sm text-slate-400">{title} workspace for CyberShield RBAC.</p>
      </Panel>
    </div>
  );
}}
''',
        encoding="utf-8",
    )
    print("page", route_path)


pages = [
    ("major-admin", "/major-admin/admins", "Admins", "Create, suspend, and manage Admin accounts"),
    ("major-admin", "/major-admin/departments", "Departments", "Investigation units and organizational structure"),
    ("major-admin", "/major-admin/users", "Users", "Platform-wide user directory"),
    ("major-admin", "/major-admin/cases", "Cases", "Global case oversight"),
    ("major-admin", "/major-admin/reports", "Reports", "Platform investigation reports"),
    ("major-admin", "/major-admin/analytics", "Analytics", "Platform analytics and trends"),
    ("major-admin", "/major-admin/audit-logs", "Audit Logs", "Security and activity audit trail"),
    ("major-admin", "/major-admin/settings", "Settings", "System configuration"),
    ("admin", "/admin/users", "Users", "Organization user management"),
    ("admin", "/admin/superior-officers", "Superior Officers", "Create and manage heads of investigation"),
    ("admin", "/admin/investigators", "Investigators", "Create and manage investigators"),
    ("admin", "/admin/cases", "Cases", "District / organization cases"),
    ("admin", "/admin/evidence", "Evidence", "Evidence across assigned cases"),
    ("admin", "/admin/reports", "Reports", "Generate and export reports"),
    ("admin", "/admin/analytics", "Analytics", "Department performance analytics"),
    ("admin", "/admin/settings", "Settings", "Admin preferences"),
    ("superior", "/superior/cases", "Cases", "Create, assign, and close investigations"),
    ("superior", "/superior/evidence", "Evidence", "Review case evidence"),
    ("superior", "/superior/timeline", "Timeline", "Investigation chronology"),
    ("superior", "/superior/relationships", "Relationship Map", "Manual entity relationships"),
    ("superior", "/superior/leads", "Manual Leads", "Investigator leads (no AI)"),
    ("superior", "/superior/reports", "Reports", "Approve and generate reports"),
    ("superior", "/superior/investigators", "Investigators", "Assigned investigation team"),
    ("superior", "/superior/settings", "Settings", "Superior officer preferences"),
    ("investigator", "/investigator/cases", "My Cases", "Cases assigned to you"),
    ("investigator", "/investigator/upload", "Upload Evidence", "Attach files to an assigned case"),
    ("investigator", "/investigator/evidence", "Evidence Repository", "Your uploaded evidence"),
    ("investigator", "/investigator/timeline", "Timeline", "Case timeline events"),
    ("investigator", "/investigator/notes", "Notes", "Investigator notes"),
    ("investigator", "/investigator/leads", "Manual Leads", "Create and track leads"),
    ("investigator", "/investigator/reports", "Reports", "Draft investigation reports"),
    ("investigator", "/investigator/settings", "Settings", "Investigator preferences"),
]

for args in pages:
    page(*args)

print("done")
