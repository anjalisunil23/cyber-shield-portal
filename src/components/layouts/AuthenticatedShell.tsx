import type { ReactNode } from "react";
import { RoleShell } from "@/components/layouts/RoleShell";
import { getToken } from "@/lib/auth";
import { normalizeRole, roleFromAccessToken } from "@/lib/roles";

export function AuthenticatedShell({ children }: { children: ReactNode }) {
  const role = normalizeRole(roleFromAccessToken(getToken())) || "investigator";
  return <RoleShell role={role}>{children}</RoleShell>;
}
