import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AuthenticatedShell } from "@/components/layouts/AuthenticatedShell";
import { LoadingBlock, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";
import { investigationApi } from "@/services/investigationApi";
import { clearToken } from "@/lib/auth";

export const Route = createFileRoute("/profile")({ component: Page });

function Page() {
  const [user, setUser] = useState<{
    full_name: string;
    email: string;
    role: string;
    department: string | null;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    investigationApi
      .me()
      .then((data) => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const handleSignOut = () => {
    clearToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  };

  return (
    <AuthenticatedShell>
      {loading ? (
        <LoadingBlock rows={6} />
      ) : (
        <PageScaffold
          crumbs={[{ label: "Home", to: "/" }, { label: "Profile" }]}
          title="Profile"
          actions={
            <Link to="/profile/edit" className="text-sm font-medium text-primary hover:underline">
              Edit
            </Link>
          }
        >
          <div className="flex flex-col items-center gap-4 rounded-xl border border-border bg-card p-5 sm:flex-row">
            <div className="grid h-12 w-12 place-items-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div className="min-w-0 text-center sm:text-left">
              <h2 className="text-base font-semibold text-foreground">
                {user?.full_name || "Account"}
              </h2>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {user?.role?.replaceAll("_", " ")}
                {user?.department ? ` · ${user.department}` : ""}
              </p>
            </div>
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Panel title="Account">
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/profile/edit" className="text-primary hover:underline">
                    Edit details
                  </Link>
                </li>
                <li>
                  <Link to="/profile/security" className="text-primary hover:underline">
                    Change password
                  </Link>
                </li>
                <li>
                  <Link to="/notifications" className="text-primary hover:underline">
                    Notifications
                  </Link>
                </li>
              </ul>
            </Panel>
            <Panel title="Session">
              <PrimaryButton onClick={handleSignOut}>Sign out</PrimaryButton>
            </Panel>
          </div>
        </PageScaffold>
      )}
    </AuthenticatedShell>
  );
}
