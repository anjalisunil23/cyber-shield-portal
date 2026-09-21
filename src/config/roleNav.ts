import type { LucideIcon } from "lucide-react";
import {
  Archive,
  Activity,
  BarChart3,
  BrainCircuit,
  Building2,
  CheckSquare,
  ClipboardList,
  Database,
  FileStack,
  FileText,
  FolderOpen,
  GitBranch,
  HardDrive,
  KeyRound,
  LayoutDashboard,
  MessageSquare,
  Network,
  NotebookPen,
  Settings,
  Shield,
  Timer,
  Upload,
  Users,
  UserCog,
} from "lucide-react";
import type { AppRole } from "@/lib/roles";

export type NavGroup = "main" | "work" | "manage" | "system";

export type NavItem = {
  to: string;
  label: string;
  icon: LucideIcon;
  exact?: boolean;
  group?: NavGroup;
};

export const NAV_GROUP_LABEL: Record<NavGroup, string> = {
  main: "Main",
  work: "Work",
  manage: "Management",
  system: "System",
};

const supervisorNav: NavItem[] = [
  {
    to: "/superior/dashboard",
    label: "Dashboard",
    icon: LayoutDashboard,
    exact: true,
    group: "main",
  },
  { to: "/superior/cases", label: "Cases", icon: FolderOpen, group: "main" },
  { to: "/superior/messages", label: "Messages", icon: MessageSquare, group: "main" },
  { to: "/superior/evidence", label: "Evidence", icon: FileStack, group: "work" },
  { to: "/superior/repository", label: "Repository", icon: Archive, group: "work" },
  { to: "/superior/timeline", label: "Timeline", icon: Timer, group: "work" },
  { to: "/superior/relationships", label: "Relationships", icon: Network, group: "work" },
  { to: "/superior/leads", label: "Leads", icon: GitBranch, group: "work" },
  { to: "/dashboard/ai-analysis", label: "Intelligence", icon: BrainCircuit, group: "work" },
  { to: "/superior/tasks", label: "Tasks", icon: CheckSquare, group: "manage" },
  { to: "/superior/reports", label: "Reports", icon: FileText, group: "manage" },
  { to: "/superior/investigators", label: "Investigators", icon: Users, group: "manage" },
  { to: "/superior/settings", label: "Settings", icon: Settings, group: "system" },
];

export const ROLE_NAV: Record<AppRole, NavItem[]> = {
  major_admin: [
    {
      to: "/major-admin/dashboard",
      label: "Dashboard",
      icon: LayoutDashboard,
      exact: true,
      group: "main",
    },
    { to: "/major-admin/cases", label: "Cases", icon: FolderOpen, group: "main" },
    { to: "/major-admin/repository", label: "Repository", icon: Archive, group: "work" },
    { to: "/major-admin/admins", label: "Admins", icon: Shield, group: "manage" },
    { to: "/major-admin/departments", label: "Departments", icon: Building2, group: "manage" },
    { to: "/major-admin/users", label: "Users", icon: Users, group: "manage" },
    { to: "/major-admin/reports", label: "Reports", icon: FileText, group: "manage" },
    { to: "/major-admin/analytics", label: "Analytics", icon: BarChart3, group: "manage" },
    { to: "/major-admin/roles", label: "Roles", icon: KeyRound, group: "system" },
    { to: "/major-admin/audit-logs", label: "Audit Logs", icon: Activity, group: "system" },
    { to: "/major-admin/storage", label: "Storage", icon: HardDrive, group: "system" },
    { to: "/major-admin/backup", label: "Backup", icon: Database, group: "system" },
    { to: "/major-admin/settings", label: "Settings", icon: Settings, group: "system" },
  ],
  admin: [
    {
      to: "/admin/dashboard",
      label: "Dashboard",
      icon: LayoutDashboard,
      exact: true,
      group: "main",
    },
    { to: "/admin/cases", label: "Cases", icon: FolderOpen, group: "main" },
    { to: "/admin/evidence", label: "Evidence", icon: FileStack, group: "work" },
    { to: "/admin/repository", label: "Repository", icon: Archive, group: "work" },
    { to: "/admin/assignments", label: "Assignments", icon: CheckSquare, group: "work" },
    { to: "/admin/users", label: "Users", icon: Users, group: "manage" },
    { to: "/admin/superior-officers", label: "Officers", icon: UserCog, group: "manage" },
    { to: "/admin/investigators", label: "Investigators", icon: ClipboardList, group: "manage" },
    { to: "/admin/reports", label: "Reports", icon: FileText, group: "manage" },
    { to: "/admin/analytics", label: "Analytics", icon: BarChart3, group: "manage" },
    { to: "/admin/settings", label: "Settings", icon: Settings, group: "system" },
  ],
  supervisor: supervisorNav,
  investigator: [
    {
      to: "/investigator/dashboard",
      label: "Dashboard",
      icon: LayoutDashboard,
      exact: true,
      group: "main",
    },
    { to: "/investigator/cases", label: "Cases", icon: FolderOpen, group: "main" },
    { to: "/investigator/messages", label: "Messages", icon: MessageSquare, group: "main" },
    { to: "/investigator/upload", label: "Upload", icon: Upload, group: "work" },
    { to: "/investigator/evidence", label: "Evidence", icon: FileStack, group: "work" },
    { to: "/investigator/repository", label: "Repository", icon: Archive, group: "work" },
    { to: "/investigator/timeline", label: "Timeline", icon: Timer, group: "work" },
    { to: "/investigator/notes", label: "Notes", icon: NotebookPen, group: "work" },
    { to: "/investigator/leads", label: "Leads", icon: GitBranch, group: "work" },
    { to: "/dashboard/ai-analysis", label: "Intelligence", icon: BrainCircuit, group: "work" },
    { to: "/investigator/tasks", label: "Tasks", icon: CheckSquare, group: "manage" },
    { to: "/investigator/reports", label: "Reports", icon: FileText, group: "manage" },
    { to: "/investigator/settings", label: "Settings", icon: Settings, group: "system" },
  ],
};
