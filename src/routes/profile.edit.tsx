import { createFileRoute, Link } from "@tanstack/react-router";
import { AuthenticatedShell } from "@/components/layouts/AuthenticatedShell";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/profile/edit")({ component: Page });

function Page() {
  return (
    <AuthenticatedShell>
      <PageScaffold
        crumbs={[{ label: "Profile", to: "/profile" }, { label: "Edit" }]}
        title="Edit profile"
      >
        <Panel>
          <form className="space-y-3" onSubmit={(e) => e.preventDefault()}>
            <label className="block text-xs font-medium text-muted-foreground">
              Full name
              <input className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-primary/60" />
            </label>
            <label className="block text-xs font-medium text-muted-foreground">
              Department
              <input className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-primary/60" />
            </label>
            <label className="block text-xs font-medium text-muted-foreground">
              Phone
              <input
                type="tel"
                className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-primary/60"
              />
            </label>
            <div className="flex gap-2">
              <PrimaryButton type="submit">Save</PrimaryButton>
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
