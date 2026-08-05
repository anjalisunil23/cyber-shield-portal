import { createFileRoute, Link, Outlet } from "@tanstack/react-router";
import { ProfileCard } from "@/components/ui-kit/Cards";
import { PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/profile")({ component: Page });

function Page() {
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100 sm:px-8">
      <div className="mx-auto max-w-4xl">
        <PageScaffold crumbs={[{ label: "Home", to: "/" }, { label: "Profile" }]} title="User Profile" subtitle="View and edit your account" actions={<Link to={"/profile/edit" as "/"} className="text-sm text-cyan">Edit profile</Link>}>
          <ProfileCard name="Alex Mercer" email="alex.mercer@agency.gov" role="Investigator" department="Cyber Crime Unit" />
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Panel title="Quick links"><ul className="space-y-2 text-sm"><li><Link to={"/profile/edit" as "/"} className="text-cyan">Edit profile</Link></li><li><Link to={"/profile/security" as "/"} className="text-cyan">Change password</Link></li><li><Link to={"/notifications" as "/"} className="text-cyan">Notifications</Link></li></ul></Panel>
            <Panel title="Session"><p className="text-sm text-slate-400">Signed in · mock session</p><PrimaryButton className="mt-3">Sign out UI</PrimaryButton></Panel>
          </div>
          <Outlet />
        </PageScaffold>
      </div>
    </div>
  );
}
