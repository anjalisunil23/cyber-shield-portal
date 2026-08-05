/** Role-based access helpers for CyberShield. */

export type AppRole = "major_admin" | "admin" | "superior_officer" | "investigator";

export const ROLE_HOME: Record<AppRole, string> = {
  major_admin: "/major-admin/dashboard",
  admin: "/admin/dashboard",
  superior_officer: "/superior/dashboard",
  investigator: "/investigator/dashboard",
};

export const ROLE_LABEL: Record<AppRole, string> = {
  major_admin: "Major Admin",
  admin: "Admin",
  superior_officer: "Superior Officer",
  investigator: "Investigator",
};

export function isAppRole(value: string | null | undefined): value is AppRole {
  return (
    value === "major_admin" ||
    value === "admin" ||
    value === "superior_officer" ||
    value === "investigator"
  );
}

export function homeForRole(role: string | null | undefined): string {
  if (isAppRole(role)) return ROLE_HOME[role];
  return "/login";
}

/** Decode JWT payload without verifying (routing only; API still validates). */
export function roleFromAccessToken(token: string | null): AppRole | null {
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1] ?? ""));
    return isAppRole(payload.role) ? payload.role : null;
  } catch {
    return null;
  }
}
