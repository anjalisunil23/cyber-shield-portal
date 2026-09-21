import { createFileRoute, Link } from "@tanstack/react-router";
import { AuthenticatedShell } from "@/components/layouts/AuthenticatedShell";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/profile/security")({ component: Page });

function Page() {
  return (
    <AuthenticatedShell>
      <PageScaffold
        crumbs={[{ label: "Profile", to: "/profile" }, { label: "Security" }]}
        title="Change password"
      >
        <Panel>
          <form className="space-y-3" onSubmit={(e) => e.preventDefault()}>
            <label className="block text-xs font-medium text-muted-foreground">
              Current password
              <input
                type="password"
                autoComplete="current-password"
                className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-primary/60"
              />
            </label>
            <label className="block text-xs font-medium text-muted-foreground">
              New password
              <input
                type="password"
                autoComplete="new-password"
                className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-primary/60"
              />
            </label>
            <label className="block text-xs font-medium text-muted-foreground">
              Confirm password
              <input
                type="password"
                autoComplete="new-password"
                className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-primary/60"
              />
            </label>
            <div className="flex gap-2">
              <PrimaryButton type="submit">Update password</PrimaryButton>
              <Link to={"/profile" as "/"}>
                <GhostButton>Cancel</GhostButton>
              </Link>
            </div>
          </form>
        </Panel>
      </PageScaffold>
    </AuthenticatedShell>
  );
}
