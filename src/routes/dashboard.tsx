import { Outlet, useNavigate, useRouterState } from "@tanstack/react-router";
import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from "react";
import { RoleShell } from "@/components/layouts/RoleShell";
import { LoadingBlock } from "@/components/ui-kit/PageKit";
import { getToken, isAuthenticated } from "@/lib/auth";
import { homeForRole, normalizeRole, roleFromAccessToken } from "@/lib/roles";

/** Legacy /dashboard — redirects home, and wraps child workspaces in the role shell. */
export const Route = createFileRoute("/dashboard")({
  component: LegacyDashboardRedirect,
});

function LegacyDashboardRedirect() {
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  useEffect(() => {
    if (!isAuthenticated()) {
      void navigate({ to: "/login" });
      return;
    }
    const path = pathname.replace(/\/$/, "") || "/";
    if (path === "/dashboard") {
      window.location.replace(homeForRole(roleFromAccessToken(getToken())));
    }
  }, [navigate, pathname]);

  const path = pathname.replace(/\/$/, "") || "/";
  if (path === "/dashboard") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-8">
        <div className="w-full max-w-sm">
          <LoadingBlock rows={4} />
        </div>
      </div>
    );
  }

  const role = normalizeRole(roleFromAccessToken(getToken()));
  if (!role) return <Outlet />;
  return <RoleShell role={role} />;
}
