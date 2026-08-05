import { Outlet, useNavigate } from "@tanstack/react-router";
import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from "react";
import { getToken, isAuthenticated } from "@/lib/auth";
import { homeForRole, roleFromAccessToken } from "@/lib/roles";

/** Legacy /dashboard — redirects to role-specific home. */
export const Route = createFileRoute("/dashboard")({
  component: LegacyDashboardRedirect,
});

function LegacyDashboardRedirect() {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      void navigate({ to: "/login" });
      return;
    }
    window.location.replace(homeForRole(roleFromAccessToken(getToken())));
  }, [navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#020617] text-slate-400">
      Redirecting to your role workspace…
      <Outlet />
    </div>
  );
}
